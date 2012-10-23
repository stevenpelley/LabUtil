#!/usr/bin/python
# extensions to plotting framework to support stacked histograms
import matplotlib 
import matplotlib.pyplot as plt
import operator
import shutil
import os
import os.path
import collections

##################
#
# hist plot functions
#
##################

def PlotFnBeforeHist(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+hist'
#lineStyles = ['-', '--', '-.', ":"]
  histColors = ["b", "g", "r"]
#lineMarkers = ['o','^','s','*','D']
  histWidth = 0.8

  # set hist label
  label = ""
  vals = plotVars['LayerValues']['Hist']
  for i, col in enumerate(plotVars['LayerGroups']['Hist']):
    val = vals[i]
    label += "%s" % (str(val),)
    if i != len(vals)-1:
      label += " "
  plotVars['HistLabel'] = label

  # set linestyle, color, and marker
#plotVars['LineStyle'] = lineStyles[plotVars['LineCount'] % len(lineStyles)]
  plotVars['HistColor'] = histColors[plotVars['LineCount'] % len(histColors)]
  plotVars['HistWidth'] = histWidth
#plotVars['LineMarker'] = 'None'

  plotVars['XVals'] = []
  plotVars['YVals'] = []

  plotVars['PlotFunction'] = plotVars['Axes'].bar

def PlotFnAfterHist(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-hist'
  plotVars['PlotFunction'](plotVars['XVals'], plotVars['YVals'], width=plotVars['HistWidth'], bottom = 0, label=plotVars['HistLabel'], color=plotVars['HistColor'])
  plotVars['LineCount'] += 1

def PlotFnHistBar(plotVars):
  if plotVars['TraceFunctionCalls']:
    print ' point'
  plotVars['X'] = plotVars['ColumnToValue'][plotVars['LayerGroups']['Point'][0]]
  plotVars['Y'] = plotVars['ColumnToValue'][plotVars['LayerGroups']['Point'][1]]
  plotVars['XVals'].append(plotVars['X'])
  plotVars['YVals'].append(plotVars['Y'])

##################
#
# default functions for plot
# set plotVars['DefaultFns'] to a key in the following dict
# every layer has a tuple of functions
# 2 functions are taken as before and after
# 1 function as the single function for that point
#
# always consider the Init and Fini layers as point layers at start and end
#
##################

import Plot

Plot.defaultFns['Hist'] = {
    'Figure'  : (Plot.PlotFnBeforeFigure, Plot.PlotFnAfterFigure,),
    'Subplot' : (Plot.PlotFnBeforeSubplot, Plot.PlotFnAfterSubplot,),
    'Hist'    : (PlotFnBeforeHist, PlotFnAfterHist,),
    'Point'   : (PlotFnHistBar,),
    'Init'    : (Plot.PlotFnInit,),
    'Fini'    : (Plot.PlotFnFini,),
    }
