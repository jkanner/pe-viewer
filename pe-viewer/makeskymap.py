from peutils import *
import streamlit as st

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False

import threading
lock = threading.RLock()

def make_skymap(chosenlist, datadict):
    aprx_dict = {}
    for ev in chosenlist:
        st.markdown("### Skymap for {0}".format(ev))   

        #-- GW170817 is a special case, using GWTC-1 samples
        if 'GW170817' in ev:   
            from matplotlib.figure import Figure
            url = 'https://dcc.ligo.org/public/0157/P1800381/007/{0}_skymap.fits.gz'.format(ev)
            with lock:
                fig = Figure()
                #ax = fig.subplots(subplot_kw={'projection': 'geo aitoff'})
                ax = fig.subplots(subplot_kw={'projection': 'astro hours mollweide'})    
                ax.imshow_hpx(url, cmap='cylon')
                st.pyplot(fig)

        # -- All other events       
        else:         
            data = datadict[ev]
            aprx_dict[ev] = st.radio("Select set of samples to use", data.skymap.keys(), key='aprx_'+ev, format_func=frmt_keyname)
            with lock:

                try:
                    fig = data.skymap[aprx_dict[ev]].plot(contour=[50, 90])
                    st.pyplot(fig[0])
                except:
                    st.markdown("Failed to generate skymap")


        with st.expander('See code'):
            st.write("""First, download a posterior samples file from the
            [GWTC-2.1](https://zenodo.org/records/6513631) or
            [GWTC-3](https://zenodo.org/records/8177023) data release.  Then try this code:
            """)

            st.write("""
            ```
            fn = 'IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5'
            from pesummary.io import read
            data = read(fn, diable_prior=True)
            data.skymap["C01:IMRPhenomXPHM"].plot(contour=[50, 90])
            ```
            """)
            
            st.write("""
            For more information:
            * See the [code for this app](https://github.com/jkanner/pe-viewer/blob/main/streamlit-app.py)
            * See the [GWTC-3 Example Notebook](https://zenodo.org/records/8177023/preview/GWTC3p0PEDataReleaseExample.ipynb?include_deleted=0)
        """)


def frmt_keyname(name):
    return "`" + name + "`"
