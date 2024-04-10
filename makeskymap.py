from peutils import *
import streamlit as st

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False

from matplotlib.backends.backend_agg import RendererAgg
lock = RendererAgg.lock


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
            st.write("""
            First, download a [PE sample file](https://zenodo.org/api/files/ecf41927-9275-47da-8b37-e299693fe5cb/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5).

            Then:
            """)
            
            st.write("""
            ```
            fn = 'IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_cosmo.h5'
            from pesummary.io import read
            data = read(fn, diable_prior=True)
            data.skymap["C01:IMRPhenomXPHM"].plot(contour=[50, 90])
            ```
            """)
            st.write("Or, see [code for this app](https://github.com/jkanner/pe-viewer/blob/main/makeskymap.py)")

def frmt_keyname(name):
    return "`" + name + "`"
