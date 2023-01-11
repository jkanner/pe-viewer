# PE Viewer

Make plots of waveforms, source parameters, and skymaps for gravitational-wave events.

Run app: [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pe-viewer.streamlit.app)

Source code: [jkanner/pe-viewer](https://github.com/jkanner/pe-viewer)

## Introduction

The gravitational-wave observatories LIGO, Virgo, and KAGRA are now recording signals from compact object mergers, including mergers of binary black holes and binary neutron stars.

This web app creates plots to display information about these mergers, such as the source mass and location.

## Context

This app makes use of data and software obtained from the Gravitational Wave Open Science 
Center, a service of LIGO Laboratory, the LIGO Scientific Collaboration, 
the Virgo Collaboration, and KAGRA.  Black hole image adopted from art by Aurore Simonnet at Sonoma State.

Learn more at [gwosc.org](https://gwosc.org).

## Event Selection

Each "event" is a compact object merger observed in gravitational waves.  The event list corresponds to all confident events in the 
[Gravitational Wave Transient Catalog](https://gwosc.org/GWTC).

From the sidebar at left, you can select one or more events.  After selecting an event, the app will find publicly available parameter estimation posterior samples and download them from zenodo.  All of the displayed plots will be derived from these samples.

## 2-D Plots

This feature shows a "triangle" plot that can reveal 
correlations between parameters.  Parameter probability distributions 
from all selected events will be shown on the same plot.

You can use the drop-down menu above the triangle plot to select which 
parameters you would like to plot.

Posterior samples are selected based on the `waveform_family` attribute
stored in the GWOSC Event Portal.  This typically corresponds to the samples
used to create tables in GWTC publications.

## Skymap

Skymaps shows the reconstructed source position for an 
event.  These are created at runtime from the posterior 
samples using the python package `ligo.skymap`.

## All Parameters

Selecting `All Parameters` will display one dimensional posterior plots for a large number of parameters for the selected events.  If two or more events are selected, then the values for different events will be displayed together.

Posterior samples are selected based on the `waveform_family` attribute
stored in the GWOSC Event Portal.  This typically corresponds to the samples
used to create tables in GWTC publications.

## Waveform

The app will select the maximum likelihood sample, and 
then construct the associated waveform using the `pycbc` 
wrappings to `lalsimulation`.  The waveform may be listened 
to as an audio file and/or downloaded.  The waveform is 
projected onto each detector, and plotted along with the 
detector data, so that you can compare how the data 
looks against the theoretical waveform.

The waveform app will only work with the first selected event - events are ignored for this feature.






