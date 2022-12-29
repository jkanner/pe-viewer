import streamlit as st
import pesummary
from pesummary.io import read
from peutils import *
from makewaveform import make_waveform, simple_plot_waveform
from makealtair import make_altair_plots, get_params_intersect
from makeskymap import make_skymap
from copy import deepcopy

import matplotlib
matplotlib.use('Agg')

from matplotlib.backends.backend_agg import RendererAgg
lock = RendererAgg.lock

st.set_page_config(layout="wide")
st.title('PE Viewer')

st.markdown("""Make plots of waveforms, source parameters, and skymaps for gravitational-wave events.
""")

st.image('img/blackhole.jpg')

# -- Query GWOSC for GWTC events
eventlist = get_eventlist(catalog=['GWTC-3-confident', 'GWTC-2.1-confident', 'GWTC-1-confident'],
                          optional=False)

# -- 2nd and 3rd events are optional, so include "None" option
eventlist2 = deepcopy(eventlist)
eventlist2.insert(0,None)  

# -- Helper method to get list of events
def get_event_list():
    x = [st.session_state['ev1'], 
        st.session_state['ev2'],
        st.session_state['ev3']]
    chosenlist = list(filter(lambda a: a != None, x))
    return chosenlist

#-- Define method for updating PE, to be called when chosen event changes
def update_pe():
    chosenlist = get_event_list()
    # -- Load all PE samples into datadict 
    with st.spinner(text="Downloading black hole data ..."):
        st.session_state['datadict'] = make_datadict(chosenlist)    
    # -- Load the published PE samples into a pesummary object
    with st.spinner(text="Formatting data ..."):
        st.session_state['published_dict'] = format_data(chosenlist, st.session_state['datadict'])  

with st.sidebar:
    with st.form("event_selection"):
        st.markdown("### Select events")
        ev1 = st.selectbox('Event 1', eventlist,  key='ev1')
        ev2 = st.selectbox('Event 2', eventlist2,  key='ev2')    
        ev3 = st.selectbox('Event 3', eventlist2,  key='ev3')
        submitted = st.form_submit_button("Update data", on_click=update_pe)

chosenlist = get_event_list()

# -- Initialize session state when app is first loaded
if 'datadict' not in st.session_state:
    update_pe()

    
twodim, skymap, onedim, waveform, about = st.tabs([
    '2-D Plot',
    'Skymaps',
    'All Parameters',
    'Waveform',
    'About'
])

# -- Short-cut variable names
datadict = st.session_state['datadict']
published_dict = st.session_state['published_dict']

with about:
    with open('README.md', 'r') as filein:
        readtxt = filein.read()    
    st.markdown(readtxt)

with twodim:
    st.markdown("""
        * These 2-D plots can reveal correlations between parameters.  
        * Select the events you'd like to see in the left sidebar, and the parameters to plot below.
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


with skymap:
    make_skymap(chosenlist, datadict)

with onedim:    
    make_altair_plots(chosenlist, published_dict)


with waveform:
    st.markdown("### Making waveform for Event 1: {0}".format(ev1))

    try:
        make_waveform(ev1, datadict)
    except:
        st.write("Unable to generate maximum likelihood waveform.  Making approximate waveform instead.")
        simple_plot_waveform(ev1)
    




    

