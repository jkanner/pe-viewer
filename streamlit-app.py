import streamlit as st
import pesummary
from pesummary.io import read
from peutils import *
from makewaveform import make_waveform, simple_plot_waveform
from makealtair import make_altair_plots, get_params_intersect
from makeskymap import make_skymap
from copy import deepcopy
import glob, os

import matplotlib
matplotlib.use('Agg')

from matplotlib.backends.backend_agg import RendererAgg
lock = RendererAgg.lock

st.set_page_config(layout="centered",
                   page_title="GW Event Viewer",
                   page_icon="https://gwosc.org/static/images/icons/gwosc-fav.ico",
                   menu_items = { "Get help": "https://ask.igwn.org",
                                  "Report a Bug": "https://github.com/jkanner/pe-viewer/issues",
                                  "About": "This app was created by staff at the [Gravitational Wave Open Science Center](https://gwosc.org)."})

st.title('GW Event Viewer')

st.markdown("""Make plots of waveforms, source parameters, and skymaps for gravitational-wave events.
""")

st.image('img/black-hole-ellipse.png')

# -- Query GWOSC for GWTC events
eventlist = get_eventlist(catalog=['GWTC-3-confident', 'GWTC-2.1-confident', 'GWTC-1-confident'],
                          optional=False)

# -- 2nd and 3rd events are optional, so include "None" option
eventlist2 = deepcopy(eventlist)
eventlist2.insert(0,None)  

# -- Check for any get params
startindex1, startindex2, startindex3 = get_getparams(eventlist,eventlist2)

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
    with st.spinner(text="Loading data ..."):
        st.session_state['datadict'] = make_datadict(chosenlist)    
    # -- Load the published PE samples into a pesummary object
    with st.spinner(text="Formatting data ..."):
        st.session_state['published_dict'] = format_data(chosenlist, st.session_state['datadict'])  

# -- Create form to set event data selection
with st.sidebar:
    with st.form("event_selection"):
        st.markdown("### Select events")
        ev1 = st.selectbox('Event 1', eventlist,  key='ev1', index=startindex1)
        ev2 = st.selectbox('Event 2', eventlist2,  key='ev2', index=startindex2)    
        ev3 = st.selectbox('Event 3', eventlist2,  key='ev3', index=startindex3)
        submitted = st.form_submit_button("Update data", on_click=update_pe)

chosenlist = get_event_list()

# --
# Display page tab structure
# --
about, twodim, skymap, onedim, waveform, config  = st.tabs([
    'About',
    '2-D Plots',
    'Skymaps',
    'All Parameters',
    'Waveform',
    'Config'
])

# -- Display ABOUT information before the data is loaded
with about:
    with st.expander("Watch video introduction"):
        st.video('https://youtu.be/74SxD0T92Oo')
    with open('README.md', 'r') as filein:
        readtxt = filein.read()    
    st.markdown(readtxt)


# -- Initialize session state (e.g. download GW150914 data)
if 'datadict' not in st.session_state:
    update_pe()


# -- Add share info
with about:
    st.markdown("## Share this page")
    st.markdown(":link: [Link to share these plots](/?event1={0}&event2={1}&event3={2})".format(ev1, ev2, ev3)) 

# ------------------------
# -- Dispaly config options
# -----------------------
with config:

    # -- Check cache status
    homedir = os.path.expanduser('~')
    cachelist = glob.glob(homedir + '/.streamlit/cache/*.memo')
    cachesize = len(cachelist)
    cachepercent = int(cachesize / len(eventlist) * 100)
    st.metric('Cache Size:', '{0}%'.format(cachepercent))

    st.write("## Build Cache")
    st.write("""This app uses a local cache to store data downloaded from zenodo.  The cache is designed to 
            build up over time as the app is used, or the cache may be built on-demand.  This process could take
            up to several hours, but may improve app performance after it is complete.""")

    if cachepercent < 99:
        st.button('Build Cache', on_click=stockcache, args=[eventlist], type='primary')
    else:
        st.write("Cache is complete!")
    
    st.write("## Clear Cache")
    st.write("""Clearing the cache will force the app
       to download samples directly from zenodo.
       This may slow down the app.""")

    with st.expander('Clear Cache'):
        st.warning("WARNING: Clearing the cache will slow down the app for all users.", icon="⚠️")
        if st.button("Clear Cache", type='primary'):
            st.cache_data.clear()


# -- Short-cut variable names
datadict = st.session_state['datadict']
published_dict = st.session_state['published_dict']

# --------------
# Display plots
# --------------
with twodim:
    st.markdown("""
        * These 2-D plots can reveal correlations between parameters.  
        * Select the events you'd like to see in the left sidebar, and the parameters to plot below.
        """)
    st.markdown("### Making plots for events:")
    for ev in chosenlist:
        if ev is None: continue
        peurl, namekey = get_pe_url(ev)
        weburl = 'https://gwosc.org/eventapi/html/GWTC/#:~:text={0}'.format(ev)
        st.markdown('#### {0}'.format(ev))
        st.markdown('[ ⬇️ Samples]({0}) | [ 🔗 Catalog]({1})'.format(peurl, weburl))
        st.text('Samples name ' + namekey)


    # -- Select parameters to plot
    st.markdown("## Select parameters to plot")
    params = get_params_intersect(published_dict, chosenlist)

    try:
        indx1 = params.index('mass_1')
        indx2 = params.index('mass_2')
    except:
        indx1 = 0
        indx2 = 1

    with st.form('twodimform'):
        param1 = st.selectbox( 'Parameter 1', params, index=indx1 )
        param2 = st.selectbox( 'Parameter 2', params, index=indx2 )
        st.form_submit_button('Update plots')

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
    st.markdown("This app only creates waveforms for one event (Event 1) to reduce run time.")

    try:
        make_waveform(ev1, datadict)
    except:
        st.write("Unable to generate maximum likelihood waveform.  Making approximate waveform instead.")
        simple_plot_waveform(ev1)
    


    

