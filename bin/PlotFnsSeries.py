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

def BeforeSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+SubplotSeries'

  Common.BeforeSubplot(plotVars)

  plotVars['SeriesColors'] = ['k', 'r', 'b']
  plotVars['SeriesStyles'] = ['-', '--', '-.', ":"]
  plotVars['SeriesMarkers'] = ['o','^','s','*','D']
  plotVars['SeriesTextures'] = [' ', '/', '\\', '//', '\\\\', 'x']

  if "Series" in plotVars['Labels']:
    plotVars['LegendTitle'] = plotVars['Labels']['Series'] % plotVars['ColumnToValue']

  plotVars['PlotFunctionList'] = []

  plotVars['SeriesCount'] = 0
  plotVars['XValsAreNumerical'] = True
  plotVars['XtoInt'] = {} #Dict
  plotVars['InttoX'] = [] #List works as a mapper for 0..n -> XVals

def AfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-SubplotSeries'

  for f,x,y,kwargs in plotVars['PlotFunctionList']:
    if not plotVars['XValsAreNumerical'] == True:
      #so tempted to write the next three statements as one line
      x = map(lambda xval: plotVars['XtoInt'][xval], x) #replaces each x by its int-value
      xAndy = zip(x,y).sort() #sorts by x
      x,y = zip(*xAsIntsAndy) #splits x and y back up
    f(x,y,**kwargs)

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
  plotVars['SeriesLabel'] = label

  # set linestyle, color, and marker
  seriesColors   = plotVars['SeriesColors']
  seriesStyles   = plotVars['SeriesStyles']
  seriesMarkers  = plotVars['SeriesMarkers']
  seriesTextures = plotVars['SeriesTextures']

  plotVars['SeriesStyle'] = seriesStyles[plotVars['SeriesCount'] % len(seriesStyles)]
  plotVars['SeriesColor'] = seriesColors[plotVars['SeriesCount'] % len(seriesColors)]
  plotVars['SeriesMarker'] = seriesMarkers[plotVars['SeriesCount'] % len(seriesMarkers)]
  plotVars['SeriesTexture'] = seriesTextures[plotVars['SeriesCount'] % len(seriesTextures)]

  # initialize x-y arrays for the series
  plotVars['XVals'] = []
  plotVars['YVals'] = []
  
  plotVars['SeriesCount'] += 1

def AfterSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Series'

  plotVars['PlotFunctionList'].append( (plotVars['PlotFunction'],list(plotVars['XVals']),list(plotVars['YVals']),dict(plotVars['PlotFunctionKWArgs'])) ) #4-tuple

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
    print '+SubplotSeries100Pct'

  plotVars['YVals100Pct'] = []

def PointAdd100Pct(plotVars):
  if plotVars['TraceFunctionCalls']:
    print ' Point100Pct'

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

def AfterSubplotAdd100Pct(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-SubplotSeries100Pct'

  for f,x,y,kwargs in plotVars['PlotFunctionList']:
    for i,yval in enumerate(y):
      if plotVars['YVals100Pct'][i] == 0:
        y[i] = 0
      else:
        y[i] = yval * 100.0 / plotVars['YVals100Pct'][i]  
