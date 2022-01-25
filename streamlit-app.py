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

st.title('PE Viewer')

st.markdown("""Display plots of posterior samples from gravitational wave events.""")

sectionnames = [
    '1-D posterior plots',
    '2-D posterior plot',
    'Skymaps',
    'Waveform',
]

def headerlabel(number):
    return "{0}".format(sectionnames[number-1])

page = st.radio('Select Section:', [1,2,3,4], format_func=headerlabel)
st.markdown("## {}".format(headerlabel(page)))

# -- Query GWOSC for GWTC events
eventlist = get_eventlist(catalog=['GWTC-2', 'GWTC-1-confident'],
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

if page == 2:
    st.markdown("""
        * These 2-D plots can reveal correlations between parameters.  
        * Select the events you'd like to see in the left sidebar, and the parameters to plot below.
        * The plots may take about 2 minutes to produce.
        """)
    st.markdown("### Making plots for events:")
    for ev in chosenlist:
        if ev is None: continue
        st.markdown(ev)

    # -- Load PE samples for all events into a pesummary object
    published_dict = load_multiple_events(chosenlist)

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
        with st.spinner(text="This triangle plot takes 2 minutes to make.  We apologize for the wait ..."):
            fig = published_dict.plot(ch_param, type='reverse_triangle',
                                    grid=False)
        st.pyplot(fig[0])


    for param in [param1, param2]:
        st.markdown("### {0}".format(param))
        with lock:
            fig = published_dict.plot(param, type='hist', kde=True)                # -- pesummary v0.9.1
            # fig = published_dict.plot(param, type='hist', kde=True, module='gw') #-- pesummary v 0.11.0
            st.pyplot(fig)

if page == 1:    
    make_altair_plots(chosenlist)

if page == 4:

    st.markdown("### Making waveform for Event 1: {0}".format(ev1))
    if int(ev1[2:4]) < 18:  # -- Kludge to find events before 2018
        st.markdown("Found GWTC-1 Event")
        plot_gwtc1_waveform(ev1)
    else:
        make_waveform(ev1)

if page == 3:
    make_skymap(chosenlist)

st.markdown("## About this app")

st.markdown("""

This app displays data from LIGO, Virgo, and GEO downloaded from the Gravitational Wave Open Science Center at https://gw-openscience.org .

[See the code](https://github.com/jkanner/streamlit-pe-demo)
""")
