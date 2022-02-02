# PE Viewer

A web app to make plots of posterior samples, skymaps, and waveforms for gravitational wave events.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/jkanner/pe-viewer/main/streamlit-app.py)

## Context

This app plots results from the gravitational wave observatories LIGO, Virgo, and KAGRA.  You can learn
more about these instruments at https://www.ligo.org.


## Event Selection

Each "event" is a compact object merger observed in gravitational waves.  The event list corresponds to all confident events in the "Gravitational Wave Transient Catalog" (GWTC), available at: 
https://gw-osc.org/eventapi/html/GWTC

From the sidebar at left, you can select one or more events.  After selecting an event, the app will find publicly available parameter estimation posterior samples and download them from zenodo.  All of the displayed plots will be derived from these samples.

## 1-D Plots

Selecting "1-D Plots" will display one dimensional posterior plots for some parameters of the selected events.  If two or more events are selected, then the values for different events will be displayed together.

## 2-D Plot

This feature shows a "triangle" plot that can reveal 
correlations between parameters.  The plot uses some 
high quality shading which takes up to 2 minutes to 
render.  Posteriors from all selected events will be 
shown on the same plot.

## Skymap

Skymaps shows the reconstructed source position for an 
event.  These are created at runtime from the posterior 
samples using the python package `ligo.skymap`.

## Waveform

The app will select the maximum likelihood sample, and 
then construct the associated waveform using the `pycbc` 
wrappings `lalsimulation`.  The waveform may be listened 
to as an audio file and/or downloaded.  The waveform is 
projected onto each detector, and plotted along with the 
detector data, so that you can compare how the data 
looks against the theoretical waveform.

The waveform app will only work with the first selected event - events are ignored for this feature.



