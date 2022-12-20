from peutils import *
import streamlit as st

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False

from matplotlib.backends.backend_agg import RendererAgg
lock = RendererAgg.lock


def make_skymap(chosenlist):
    aprx_dict = {}
    for ev in chosenlist:
        st.markdown("### Skymap for {0}".format(ev))        
        data = load_samples(ev)
        aprx_dict[ev] = st.radio("Select set of samples to use", data.skymap.keys(), key='aprx_'+ev)
        with lock:
            fig = data.skymap[aprx_dict[ev]].plot(contour=[50, 90])
            st.pyplot(fig[0])
        
