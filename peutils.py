import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import requests, os, io
import tempfile

from gwpy.timeseries import TimeSeries
from gwosc.locate import get_urls
from gwosc import datasets
from gwosc.api import fetch_event_json

from copy import deepcopy
import base64

import pesummary
from pesummary.io import read


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

    allevents = set()
    
    for cat in catalog:
        # -- Get list of events
        # find_datasets(catalog='GWTC-1-confident',type='events')
        eventlist = datasets.find_datasets(type='events', catalog=cat)
        eventlist = [name.split('-')[0] for name in eventlist if name[0:2] == 'GW']
        eventset = set([name for name in eventlist])
        allevents = allevents.union(eventset)
        
    eventlist = list(allevents)
    eventlist.sort()
    if optional:
        eventlist.insert(0,None)    
    return eventlist

# -- Load PE samples
@st.cache
def load_samples_old(event):
    fn = 'small-pe-gwtc2/{0}_small.h5'.format(event)
    samples = read(fn)
    return samples


# -- Assemble samples into sample dictionary
def load_multiple_events(chosenlist):
    sample_dict = {}
    data_load_state = st.text('Loading data...')
    for i,chosen in enumerate(chosenlist, 1):
        data_load_state.text('Loading event ... {0}'.format(i))
        if chosen is None: continue
        samples = load_samples(chosen)
        try:
            #-- GWTC-2
            sample_dict[chosen] = samples.samples_dict['PublicationSamples']
        except:
            #-- GWTC-1
            sample_dict[chosen] = samples.samples_dict
            
    data_load_state.text('Loading event ... done'.format(i))
    published_dict = pesummary.utils.samples_dict.MultiAnalysisSamplesDict( sample_dict )
    return published_dict


# -- Load PE samples from web
@st.cache
def load_samples(event, waveform=False):

    if waveform:
        fn = '{0}_waveform.h5'.format(event)
    else:
        fn = '{0}_small.h5'.format(event)
        
    url = 'https://labcit.ligo.caltech.edu/~jkanner/demo/pe/small-pe-gwtc2/{0}'.format(fn)

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


    return samples




params = ['a_1', 'a_2', 'chi_eff', 'chi_p', 'chirp_mass',
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
@st.cache   #-- Magic command to cache data
def load_strain(t0, detector):
    straindata = TimeSeries.fetch_open_data(detector, t0-14, t0+14, cache=False)
    return straindata

def get_params_intersect(sample_dict, chosenlist):
    allparams = set(sample_dict[chosenlist[0]].parameters)
    for event in sample_dict.keys():
        thisparam = set(sample_dict[event].parameters)
        allparams = allparams.intersection(thisparam)
    return allparams
 
