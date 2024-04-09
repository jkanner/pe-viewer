import streamlit as st
from pesummary.io import read
import numpy as np
import altair as alt
import pandas as pd
import gwpy
from scipy import signal
import io
from scipy.io import wavfile
from copy import deepcopy

import os
import base64

from gwosc import datasets
from gwosc.api import fetch_event_json
from peutils import *


# -- Try download for waveform data
def get_download_link(signal, filename='waveform.csv'):
    """
    Generates a link allowing the data in a pycbc strain timeseries
    """
    data_dict = {'Time':signal.times, 'Strain':signal.value}
    data = pd.DataFrame(data_dict)
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

# -- Make audio helper function
def make_audio_file(bp_data, t0=None, lowpass=False):
    # -- window data for gentle on/off
    window = signal.windows.tukey(len(bp_data), alpha=1.0/10)
    if lowpass:
        win_data = bp_data.lowpass(1100)*window
    else:
        win_data = bp_data*window
        
    # -- Normalize for 16 bit audio
    win_data = np.int16(win_data/np.max(np.abs(win_data)) * 32767 * 0.9)
    fs=1/win_data.dt.value
    virtualfile = io.BytesIO()    
    wavfile.write(virtualfile, int(fs), win_data)
    return virtualfile


# -- Plotting helper function
def plot_signal(signal, color_num=0, display=True):
    source = pd.DataFrame({
        'Time (s)': signal.times[...],
        'Strain / 1e-21': signal.value / 1e-21,
        'color':['#1f77b4', '#ff7f0e'][color_num]
    })
        
    chart = alt.Chart(source).mark_line().encode(
        alt.X('Time (s)'),
        alt.Y('Strain / 1e-21:Q'),
        color=alt.Color('color', scale=None),
    )

    if display:
        st.altair_chart(chart, use_container_width=True)

    return(chart)

def plot_white_signal(signal, color_num=0, display=True):
    source = pd.DataFrame({
        'GPS Time (s)': signal.times,
        'Strain': signal.value,
        'color':['#1f77b4', '#ff7f0e', '#aaa'][color_num]
    })
        
    chart = alt.Chart(source).mark_line().encode(
        alt.X('GPS Time (s)'),
        alt.Y('Strain:Q'),
        color=alt.Color('color', scale=None),
    ).interactive(bind_y = False)

    if display:
        st.altair_chart(chart, use_container_width=True)

    return(chart)

def make_waveform(event, datadict):    
    
    pedata = datadict[event]
    
    # -- Get dictionary of samples, indexed by run
    samples_dict = pedata.samples_dict

    # -- For now, hard code approxmiate to IMRPhenomXPHM
    # aprx = 'IMRPhenomXPHM'

    # -- Clean list of approximates
    aprxlist =  deepcopy(pedata.approximant)

    for item in pedata.approximant:
        if type(item) != str:  aprxlist.remove(item)    #-- Remove items where no approxmiant is found
        if item == 'SEOBNRv4PHM': aprxlist.remove(item) #-- Remove waveforms used by RIFT, because RIFT does not report times
                
        
    # -- Select corresponding samples
    aprx = st.radio("Select set of samples to use", aprxlist, key='aprx_waveform'+event)
    indx_num = pedata.approximant.index(aprx)
    indx = list(samples_dict.keys())[indx_num]
    st.text('Waveform Family: {0}'.format(aprx))
    st.text('Using samples for {0}'.format(indx))
    
    # -- Get a single run
    posterior_samples = samples_dict[indx]
    
    # -- Get reference frequency
    try:
        fref = float(pedata.config[indx]['engine']['fref'])
    except:
        fref = float(pedata.config[indx]['config']["reference-frequency"])
        
    # -- Find the index of max log likelihood
    st.write("Finding maximum likelihood sample ...")
    loglike = posterior_samples['log_likelihood']
    maxl_index = loglike.argmax()
    
    # -- Example parameter
    chirp_mass = posterior_samples['chirp_mass'][maxl_index]
    mass1 = posterior_samples['mass_1'][maxl_index]
    mass2 = posterior_samples['mass_2'][maxl_index]
    chi_eff = posterior_samples['chi_eff'][maxl_index]
    dist = posterior_samples['luminosity_distance'][maxl_index]
    
    st.markdown("#### Detector Frame Waveform Properties:")
    st.write("Mass 1: {0:.2f}".format(mass1), 'M$_{\odot}$')
    st.write("Mass 2: {0:.2f}".format(mass2), 'M$_{\odot}$')
    st.markdown("Effective Spin: {0:.2f}".format(chi_eff))
    st.markdown("Luminosity distance: {0:.2f} Mpc".format(dist))

    if chirp_mass < 10:
        f_low = 60
        fs = 4096
    else:
        f_low = 20
        fs = 4096

    hp_dict = posterior_samples.maxL_td_waveform(aprx,
                                            delta_t=1/fs,
                                            f_low=f_low,
                                            f_ref=fref)

    hp = hp_dict['h_plus']
 
    t0 = datasets.event_gps(event)
    hp_length = len(hp) / fs
    if hp_length > 8:
        hp = hp.crop( t0-7, t0+1 )

    # -- Plot waveform w/ altair
    plot_signal(hp)
    
    # -- Make audio files
    st.audio(make_audio_file(hp))
    
    # -- Make file for download
    outfile = io.StringIO()
    outdata = zip(hp.times, hp.value)
    for t, s in outdata:
        outfile.write('{0}, {1}\n'.format(t.value, s))
    
    url = get_download_link(hp, filename="{0}_waveform.csv".format(event))

    st.markdown(url, unsafe_allow_html=True)

    # -- Get detector / gps info
    detectorlist = list(datasets.event_detectors(event))
    detectorlist.sort()
    
    # -- Set plot zoom
    dt = 0.2
    cropstart = t0 - dt
    cropend   = t0 + dt

    st.markdown("## Project waveform onto each detector")
    st.markdown("Whitened and band-passed detector data in gray, with projected waveform in orange.")
    # -- Band-pass controls
    freqrange = st.slider('Band-pass frequency range (Hz)', min_value=10, max_value=2000, value=(30,400), key=event)
    
    for ifo in detectorlist:
        
        st.markdown("### {0}".format(ifo))

        # -- Get strain data
        straindata = load_strain(t0, ifo)
        strain = deepcopy(straindata)
        asd = strain.asd()

        # -- Whiten, bandpass, and crop
        white_data = strain.whiten(asd=asd)
        bp_data = white_data.bandpass(freqrange[0], freqrange[1])
        bp_cropped = bp_data.crop(cropstart, cropend)
        
        # plot_white_signal(bp_cropped)
        
        # -- Project waveform onto detector
        hp = posterior_samples.maxL_td_waveform(aprx,
                                            delta_t=1/fs,
                                            f_low=f_low,
                                            f_ref=fref,
                                            project=ifo)

        st.write(aprx)
        
        # -- Taper and zero pad
        hp = hp.taper()
        # -- Zero pad
        hp = hp.pad(60*fs)

        # -- whiten and bandpass template
        white_temp = hp.whiten(asd=asd)
        bp_temp = white_temp.bandpass(freqrange[0], freqrange[1])
        crop_temp = bp_temp.crop(cropstart, cropend)
        
        chart1 = plot_white_signal(bp_cropped, color_num=2, display=False)
        chart2 = plot_white_signal(crop_temp, color_num=1, display=False)

        st.altair_chart(chart1+chart2, use_container_width=True)

def simple_plot_gwtc1(name, datadict):

    # -- Special case for GW170817 and GW190425
    from pesummary.utils.samples_dict import SamplesDict
        
    aprx = 'IMRPhenomXPHM'
    fs = 4096

    keys = list(datadict.keys())

    samples = datadict[keys[0]].samples_dict

    # -- test for single or multiple analyses
    try:
        test = samples['ra']
    except:
        samples = samples[list(samples.keys())[0]]

    # -- Create dummy samples for params missing from GW170817
    dummysamples = [np.zeros(len(samples['ra']))]
    dummysamples.append(np.zeros(len(samples['ra'])))
    for this_param in samples.samples:
        dummysamples.append(this_param)

    parameters = ["iota", "log_likelihood"] + samples.parameters
    dummyDict = SamplesDict(parameters, dummysamples)
    
    samples = dummyDict
    hp_dict = samples.maxL_td_waveform(aprx,
                                            delta_t=1/fs,
                                            f_low=100,
                                            f_ref=100)

    hp = hp_dict['h_plus']

 
    t0 = datasets.event_gps(name)
    hp_length = len(hp) / fs
    if hp_length > 8:
        hp = hp.crop( t0-7, t0+1 )

    # -- Plot waveform w/ altair
    plot_signal(hp)
    
    # -- Make audio files
    st.audio(make_audio_file(hp))
    
    # -- Make file for download
    outfile = io.StringIO()
    outdata = zip(hp.times, hp.value)
    for t, s in outdata:
        outfile.write('{0}, {1}\n'.format(t.value, s))
    
    url = get_download_link(hp, filename="{0}_waveform.csv".format(name))
    
    st.markdown(url, unsafe_allow_html=True)

    
