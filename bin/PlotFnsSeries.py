#!/usr/bin/python

import os
import os.path
import matplotlib
import matplotlib.pyplot as plt
import shutil
import numpy as np

import PlotFnsCommon as Common

###############################
#
# Series
#
###############################

#defined here so that other PlotFns can reuse it if need be
def ResetSeriesVars(plotVars):
  plotVars['SeriesInfo'] = []
  plotVars['SeriesCount'] = 0
  plotVars['XValsAreNumerical'] = True
  plotVars['XtoInt'] = {} #Dict
  plotVars['InttoX'] = [] #List works as a mapper for 0..n -> XVals

def BeforeSubplot(plotVars):
  Common.BeforeSubplot(plotVars)

  if plotVars['TraceFunctionCalls']:
    print '+Subplot (Series)'

  plotVars['SeriesColors'] = ['k', 'r', 'b']
  plotVars['SeriesStyles'] = ['-', '--', '-.', ":"]
  plotVars['SeriesMarkers'] = ['o','^','s','*','D']
  plotVars['SeriesTextures'] = [' ', '/', '\\', '//', '\\\\', 'x']
  plotVars['SeriestoInt'] = {}

  if "Series" in plotVars['Labels']:
    plotVars['LegendTitle'] = plotVars['Labels']['Series'] % plotVars['ColumnToValue']

  ResetSeriesVars(plotVars)

def numerizeXVals(plotVars):
  for si in plotVars['SeriesInfo']:
    si['xlabels'] = list(si['x'])
    if plotVars['XValsAreNumerical'] == True:
      continue
    
    xlabels = si['xlabels']
    x = map(lambda val: plotVars['XtoInt'][val], xlabels) #replaces each xval by its int-value
    y = si['y']
    zipped = zip(x,y,xlabels)
    zipped.sort() #sorts by x int-values
    si['x'],si['y'],si['xlabels'] = zip(*zipped) #splits the zipped stuff back out

def plotAllSeries(plotVars):
  for si in plotVars['SeriesInfo']:
    si['fn']( si['x'],si['y'],**si['kwargs'] )

def cleanUpXTicks(plotVars):
  if plotVars['XValsAreNumerical'] == False:
    ax = plotVars['Axes']
    ax.minorticks_off()
    ax.set_xticks( range(len(plotVars['InttoX'])) )
    ax.set_xticklabels(plotVars['InttoX'])
    ax.tick_params(bottom=True)

def AfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (Series)'

  numerizeXVals(plotVars)
  plotAllSeries(plotVars)
  cleanUpXTicks(plotVars)

  Common.AfterSubplot(plotVars)

def BeforeSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Series'

  # set series label
  label = ""
  vals = plotVars['LayerValues']['Series']
  for i, col in enumerate(plotVars['LayerGroups']['Series']):
    val = vals[i]
    label += "%s" % (str(val),)
    if i != len(vals)-1:
      label += " "

  if label in plotVars['SeriestoInt']:
    plotVars['SeriesLabel'] = None
    plotVars['SeriesIntValue'] = plotVars['SeriestoInt'][label]
  else:
    plotVars['SeriesLabel'] = label
    plotVars['SeriesIntValue'] = len(plotVars['SeriestoInt'])
    plotVars['SeriestoInt'][label] = plotVars['SeriesIntValue']


  # set linestyle, color, and marker
  seriesColors   = plotVars['SeriesColors']
  seriesStyles   = plotVars['SeriesStyles']
  seriesMarkers  = plotVars['SeriesMarkers']
  seriesTextures = plotVars['SeriesTextures']

  plotVars['SeriesStyle'] = seriesStyles[plotVars['SeriesIntValue'] % len(seriesStyles)]
  plotVars['SeriesColor'] = seriesColors[plotVars['SeriesIntValue'] % len(seriesColors)]
  plotVars['SeriesMarker'] = seriesMarkers[plotVars['SeriesIntValue'] % len(seriesMarkers)]
  plotVars['SeriesTexture'] = seriesTextures[plotVars['SeriesIntValue'] % len(seriesTextures)]

  # initialize x-y arrays for the series
  plotVars['XVals'] = []
  plotVars['YVals'] = []
  
  plotVars['SeriesCount'] += 1

def AfterSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Series'

  plotVars['SeriesInfo'].append( {
    'fn' : plotVars['PlotFunction'],
    'x'  : list(plotVars['XVals']),
    'y'  : list(plotVars['YVals']),
    'kwargs' : dict(plotVars['PlotFunctionKWArgs']),
    'intvalue' : plotVars['SeriesIntValue'],
    'label' : plotVars['SeriesLabel'],
    } )

def Point(plotVars):
  if plotVars['TraceFunctionCalls']:
    print ' Point'

  plotVars['X'] = plotVars['ColumnToValue'][plotVars['LayerGroups']['Point'][0]]
  plotVars['Y'] = plotVars['ColumnToValue'][plotVars['LayerGroups']['Point'][1]]
  plotVars['XVals'].append(plotVars['X'])
  plotVars['YVals'].append(plotVars['Y'])

  if not plotVars['X'] in plotVars['XtoInt']:
    plotVars['XtoInt'][plotVars['X']] = len(plotVars['InttoX'])
    plotVars['InttoX'].append(plotVars['X'])

  if not isinstance(plotVars['X'], (int, long, float,)):
    plotVars['XValsAreNumerical'] = False
 
###################################
#
# Cumulative series
#
###################################

def BeforeSeriesAddCumulative(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+SeriesCumulative'

  plotVars['YValCumulative'] = 0

def PointAddCumulative(plotVars):
  if plotVars['TraceFunctionCalls']:
    print ' PointCumulative'

  #assumed to be called after Point
  #so, just appended a point

  plotVars['YValCumulative']+=plotVars['YVals'][-1]
  plotVars['YVals'][-1] = plotVars['YValCumulative']

###################################
#
# 100 percent stack
#
###################################

def BeforeSubplotAdd100Pct(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Subplot (100Pct)'

  plotVars['YVals100Pct'] = []

def AfterSubplotAdd100Pct(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (100Pct)'

  for si in plotVars['SeriesInfo']:
    y = si['y']
    for i,yval in enumerate(y):
      if plotVars['YVals100Pct'][i] == 0:
        y[i] = 0
      else:
        y[i] = yval * 100.0 / plotVars['YVals100Pct'][i]  

def PointAdd100Pct(plotVars):
  if plotVars['TraceFunctionCalls']:
    print ' Point (100Pct)'

  #assumed to be called after Point
  #so, just appended a point

  lenYVal = len(plotVars['YVals'])
  if lenYVal > len(plotVars['YVals100Pct']):
    plotVars['YVals100Pct'].append(plotVars['YVals'][-1])
  else:
    plotVars['YVals100Pct'][lenYVal-1] += plotVars['YVals'][-1]

def Point100Pct(plotVars):
  Point(plotVars)
  PointAdd100Pct(plotVars)
