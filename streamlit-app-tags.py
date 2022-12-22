import streamlit as st
import pesummary
from pesummary.io import read
from peutils import *
from makewaveform import make_waveform, plot_gwtc1_waveform
from makealtair import make_altair_plots, get_params_intersect
from makeskymap import make_skymap
from copy import deepcopy

import matplotlib
matplotlib.use('Agg')

from matplotlib.backends.backend_agg import RendererAgg
lock = RendererAgg.lock

st.set_page_config(layout="wide")
st.title('PE Viewer')

st.markdown("""Display plots of posterior samples from gravitational wave events.""")

# -- Query GWOSC for GWTC events
eventlist = get_eventlist(catalog=['GWTC-3-confident', 'GWTC-2.1-confident', 'GWTC-1-confident'],
                          optional=False)

# -- 2nd and 3rd events are optional, so include "None" option
eventlist2 = deepcopy(eventlist)
eventlist2.insert(0,None)    

st.sidebar.markdown("### Select events")
ev1 = st.sidebar.selectbox('Event 1', eventlist)
ev2 = st.sidebar.selectbox('Event 2', eventlist2)    
ev3 = st.sidebar.selectbox('Event 3', eventlist2)
x = [ev1, ev2, ev3]
chosenlist = list(filter(lambda a: a != None, x))

# -- Load all PE samples into datadict 
datadict = make_datadict(chosenlist)

# -- Load the published PE samples into a pesummary object
published_dict = format_data(chosenlist, datadict)

twodim, onedim,  skymap, waveform, about = st.tabs([
    '2-D posterior plot',
    '1-D posterior plots',
    'Skymaps',
    'Waveform',
    'About'
])

with about:
    st.markdown("## About this app")
    st.markdown("""
    This app displays data from LIGO, Virgo, and KAGRA downloaded from the Gravitational Wave Open Science Center at https://gwosc.org .

    #### Source code: [jkanner/streamlit-pe-demo](https://github.com/jkanner/streamlit-pe-demo)
    """)
    with open('README.md', 'r') as filein:
        readtxt = filein.read()    
    st.markdown(readtxt)

with twodim:
    st.markdown("""
        * These 2-D plots can reveal correlations between parameters.  
        * Select the events you'd like to see in the left sidebar, and the parameters to plot below.
        * The plots may take about 2 minutes to produce.
        """)
    st.markdown("### Making plots for events:")
    for ev in chosenlist:
        if ev is None: continue
        st.markdown(ev)

    # -- Select parameters to plot
    st.markdown("## Select parameters to plot")
    params = get_params_intersect(published_dict, chosenlist)

    try:
        indx1 = params.index('mass_1')
        indx2 = params.index('mass_2')
    except:
        indx1 = 0
        indx2 = 1
        
    param1 = st.selectbox( 'Parameter 1', params, index=indx1 )
    param2 = st.selectbox( 'Parameter 2', params, index=indx2 )

    # -- Make plot based on selected parameters
    st.markdown("### Triangle plot")
    ch_param = [param1, param2]
    with lock:
        with st.spinner(text="Making triangle plot ..."):
            fig = published_dict.plot(ch_param, type='reverse_triangle',
                                    grid=False)
        st.pyplot(fig[0])


    for param in [param1, param2]:
        st.markdown("### {0}".format(param))
        with lock:
            fig = published_dict.plot(param, type='hist', kde=True)                # -- pesummary v0.9.1
            # fig = published_dict.plot(param, type='hist', kde=True, module='gw') #-- pesummary v 0.11.0
            st.pyplot(fig)

with onedim:    
    make_altair_plots(chosenlist, published_dict)

with skymap:
    make_skymap(chosenlist, datadict)

with waveform:
    st.markdown("### Making waveform for Event 1: {0}".format(ev1))
    if 'GW170817' in ev1:  
        st.markdown("Making approximate waveform for GW170817 ...")
        plot_gwtc1_waveform(ev1)
    else:
        make_waveform(ev1, datadict)




    

