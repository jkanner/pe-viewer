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
from peutils import *
import pesummary
from peutils import *

def get_params_intersect(sample_dict, chosenlist):
    allparams = set(sample_dict[chosenlist[0]].parameters)
    for event in sample_dict.keys():
        thisparam = set(sample_dict[event].parameters)
        allparams = allparams.intersection(thisparam)

    # -- Intersect with the list of good parameters from peutils
    thisparam = set(ALL_PARAM)
    allparams = allparams.intersection(thisparam)
    paramlist = list(allparams)
    paramlist.sort()
    return paramlist
        
def make_altair_plots(chosenlist, sample_dict):

    st.markdown("""
    This page will show 1-D posterior plots for any parameters available for all selected events.
    See the pesummary docs for [definitions of standard parameters](https://lscsoft.docs.ligo.org/pesummary/stable_docs/gw/parameters.html)
    """)
    
    for ev in chosenlist:
        if ev is None: continue
        peurl, namekey, catalog = get_pe_url(ev)
        weburl = 'https://gwosc.org/eventapi/html/GWTC/#:~:text={0}'.format(ev)
        
        st.markdown('#### {0}'.format(ev))
        st.markdown(' ⬇️ [Samples]({0}) | 🔗 [Catalog]({1})'.format(peurl, weburl))
        st.text('Samples name ' + namekey)
        
    #sample_dict = load_multiple_events(chosenlist)
 
    # -- Color list
    colorlist = ['blue', 'red', 'green']

    # -- Get parameters present in all selected events
    allparams = get_params_intersect(sample_dict, chosenlist)
    
    col1, col2 = st.columns(2)
    # -- Loop over parameters
    for count, param in enumerate(allparams):
                
        chartlist = []
        for i,event in enumerate(chosenlist):

            if event is None: continue

            samples = sample_dict[event]
            
            # -- Make histogram
            value, bins = np.histogram(samples[param], bins=50, density=True)
            
            source = pd.DataFrame({
                param : bins[1:],
                'Probability Density': value,
                'Event': len(value)*[event]
            })

            chart = alt.Chart(source).mark_area(
                opacity=0.5,
                interpolate='step',
            ).encode(
                alt.X(param),
                alt.Y('Probability Density'),
                color='Event:N')

            chartlist.append(chart)

        allchart = chartlist[0]
        for chart in chartlist[1:]:
            allchart+=chart

        # -- Def
        refurl = 'https://lscsoft.docs.ligo.org/pesummary/reference/gw/parameters.html#:~:text={0}'.format(param)

        unitlabel = samples.all_latex_labels[param]
        
        #st.altair_chart(allchart, use_container_width=True)
        if (count % 2):
            col2.markdown("### [{1}]({0})".format(refurl, unitlabel))
            col2.altair_chart(allchart, use_container_width=True)
        else:
            col1.markdown("### [{1}]({0})".format(refurl, unitlabel))
            col1.altair_chart(allchart, use_container_width=True)

    with st.expander("See the code"):
        st.write("""First, download a posterior samples file from the
        [GWTC-2.1](https://zenodo.org/records/6513631) or
        [GWTC-3](https://zenodo.org/records/8177023) data release.  Then try this code:
        """)

        st.write("""
        ```
        from pesummary.io import read
        import matplotlib.pyplot as plt
        
        filename = 'IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5'
        data = read(filename, disable_prior=True)
        samples = data.samples_dict['C01:IMRPhenomXPHM']
        mass_samples = samples['mass_1']
            
        plt.hist(mass_samples, bins=30, density=True)
        plt.xlabel('mass_1')
        plt.ylabel('Probability Density')

        ```
        """)

        st.write("""
        For more information:
        * See the [code for this app](https://github.com/jkanner/pe-viewer/blob/main/streamlit-app.py)
        * See the [GWTC-3 Example Notebook](https://zenodo.org/records/8177023/preview/GWTC3p0PEDataReleaseExample.ipynb?include_deleted=0)
        """)

    

