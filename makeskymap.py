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
        # if ev is None: continue

        if int(ev[2:4]) < 18:

            #-- GWTC-1
            from matplotlib.figure import Figure
            url = 'https://dcc.ligo.org/public/0157/P1800381/007/{0}_skymap.fits.gz'.format(ev)
            
            with lock:
                fig = Figure()
                #ax = fig.subplots(subplot_kw={'projection': 'geo aitoff'})
                ax = fig.subplots(subplot_kw={'projection': 'astro hours mollweide'})    
                ax.imshow_hpx(url, cmap='cylon')
                st.pyplot(fig)

        else:
            # -- GWTC-3
            data = load_samples(ev)
            aprx_dict[ev] = st.radio("Select set of samples to use", data.skymap.keys(), key='aprx_'+ev)
            with lock:
                fig = data.skymap[aprx_dict[ev]].plot(contour=[50, 90])
                st.pyplot(fig[0])
        
