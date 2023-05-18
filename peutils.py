import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import requests, os, io, json
import tempfile

from gwpy.timeseries import TimeSeries
from gwosc.locate import get_urls
from gwosc import datasets
from gwosc.api import fetch_event_json

from copy import deepcopy
import base64

import pesummary
from pesummary.io import read
import pesummary.utils.samples_dict


# Use the non-interactive Agg backend, which is recommended as a
# thread-safe backend.
# See https://matplotlib.org/3.3.2/faq/howto_faq.html#working-with-threads.
import matplotlib as mpl
mpl.use("agg")

from matplotlib.backends.backend_agg import RendererAgg
lock = RendererAgg.lock


# -- Query for eventlist
@st.cache
def get_eventlist(catalog=None, optional=False):

    eventlist = []

    # -- Get GWTC list
    url = 'https://www.gwosc.org/eventapi/json/GWTC/'
    gwtc = requests.get(url).json()

    for event_id, info in gwtc['events'].items():
        if info['catalog.shortName'] in catalog:
            eventlist.append(info['commonName'])
        
    eventlist.sort()
    if optional:
        eventlist.insert(0,None)    
    return eventlist

# -- Assemble samples into sample dictionary
#@st.cache(max_entries=5, suppress_st_warning=True)
def format_data(chosenlist, datadict):
    sample_dict = {}
    for i,chosen in enumerate(chosenlist, 1):
        if chosen is None: continue
        samples = datadict[chosen]
        url, waveform = get_pe_url(chosen)
        try:
            #-- This key should be the preferred samples for GWTC-2.1 and GWTC-3
            sample_dict[chosen] = samples.samples_dict[waveform]
        except:
            #-- GWTC-1
            sample_dict[chosen] = samples.samples_dict
    published_dict = pesummary.utils.samples_dict.MultiAnalysisSamplesDict( sample_dict )
    return published_dict


# -- Create dictionary of samples
#@st.cache(max_entries=5, suppress_st_warning=True)
def make_datadict(chosenlist):
    datadict = {}
    for ev in chosenlist:
        with st.spinner(text="Downloading data for {0} ...".format(ev)):
            datadict[ev] = load_samples(ev)
    return datadict

# -- Load PE samples from web
@st.cache(max_entries=1, show_spinner=False, persist=True)
def load_samples(event, gwtc=True):
    if gwtc:
        url, waveform = get_pe_url(event)

    try: 
        r = requests.get(url)
        tfile = tempfile.NamedTemporaryFile(suffix='.h5')
        tfile.write(r.content)
        samples = read(tfile.name)
        
    except:
        url = 'https://dcc.ligo.org/public/0157/P1800370/005/{0}_GWTC-1.hdf5'.format(event)
        r = requests.get(url)
        tfile = tempfile.NamedTemporaryFile(suffix='.h5')
        tfile.write(r.content)
        if event == 'GW170817':
            samples = read(tfile.name, path_to_samples="IMRPhenomPv2NRT_lowSpin_posterior")
        else:
            samples = read(tfile.name)

    try: 
        samples.downsample(2000)
    except:
        pass
    return samples


def stockcache(eventlist):
    total = len(eventlist)
    st.write("## Intializing  cache.  This may take several hours")
    cachebar = st.progress(0.01)
    for count, ev in enumerate(eventlist):
        cachebar.progress(count/total)
        with st.spinner(text="Downloading data for {0} ({1} / {2})".format(ev, count, total)):
            load_samples(ev)


ALL_PARAM = ['a_1', 'a_2', 'chi_eff', 'chi_p', 'chirp_mass',
          'chirp_mass_source', 'comoving_distance', 'cos_iota',
          'cos_theta_jn', 'cos_tilt_1', 'cos_tilt_2', 'dec',
          'final_mass', 'final_mass_non_evolved',
          'final_mass_source', 'final_mass_source_non_evolved',
          'final_spin', 'final_spin_non_evolved', 'geocent_time',
          'inverted_mass_ratio', 'iota', 'log_likelihood',
          'luminosity_distance', 'mass_1', 'mass_1_source',
          'mass_2', 'mass_2_source', 'mass_ratio', 'neff', 'p',
          'peak_luminosity', 'peak_luminosity_non_evolved',
          'phase', 'phi_1', 'phi_12', 'phi_2', 'phi_jl', 'ps',
          'psi', 'psiJ', 'ra', 'radiated_energy',
          'radiated_energy_non_evolved', 'redshift',
          'spin_1x', 'spin_1y', 'spin_1z', 'spin_2x',
          'spin_2y', 'spin_2z', 'symmetric_mass_ratio',
          'theta_jn', 'tilt_1', 'tilt_2', 'total_mass',
          'total_mass_source']


# -- Load strain data
@st.cache(max_entries=6)   #-- Magic command to cache data
def load_strain(t0, detector):
    straindata = TimeSeries.fetch_open_data(detector, t0-14, t0+14, cache=False)
    return straindata

def get_params_intersect(sample_dict, chosenlist):
    allparams = set(sample_dict[chosenlist[0]].parameters)
    for event in sample_dict.keys():
        thisparam = set(sample_dict[event].parameters)
        allparams = allparams.intersection(thisparam)
    return allparams
 

# -- Find URL of the PE set
@st.cache(max_entries=200)
def get_pe_url(event):
    url = 'https://www.gw-openscience.org/eventapi/json/GWTC/'
    gwtc = requests.get(url).json()
    
    for event_id, info in gwtc['events'].items():
        if info['commonName'] == event:
            # -- Grab single event JSON
            evurl = info['jsonurl']
            eventinfo = requests.get(evurl).json()

            # -- Find PE data URL for GWTC-1 events
            meta = eventinfo['events'][event_id]
            if meta['catalog.shortName'] == 'GWTC-1-confident':
                for peset, peinfo in meta['parameters'].items():
                    if 'R2_pe_combined' in peset:
                        return peinfo['data_url'], peinfo['waveform_family']


            # -- Find PE data URL for all other events
            for peset, peinfo in eventinfo['events'][event_id]['parameters'].items():
                if peinfo['is_preferred'] and (peinfo['pipeline_type'] == 'pe'):
                    return peinfo['data_url'], peinfo['waveform_family']


if __name__ == '__main__':
    get_pe_url('cow')
    #print(get_pe_url('GW150914'))
    #print(get_pe_url('GW170817'))

    samples = load_samples('GW200225_060421', gwtc=True)
    print(samples)



