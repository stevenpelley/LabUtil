#!/usr/bin/python

import os
import os.path
import matplotlib
import matplotlib.pyplot as plt
import shutil
import numpy as np

import PlotFnsCommon as Common
import PlotFnsSeries as Series

###################################
#
# Common bar setup and functions
#
###################################

def BeforeSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Series (Bar)'

  Series.BeforeSeries(plotVars)

  plotVars['PlotFunction'] = plotVars['Axes'].bar
  plotVars['PlotFunctionKWArgs'] = {
    'label'     : plotVars['SeriesLabel'],
    'color'     : plotVars['SeriesColor'],
    'bottom'    : 0,
    'width'     : plotVars.get('BarWidth', 0.8),
  }

def StackBars(plotVars):
  #determine new bottoms
  if len(plotVars['SeriesInfo']) > 1:
    cumulativeBottom = []
    for si in plotVars['SeriesInfo']:
      y = si['y']
      add = len(y) - len(cumulativeBottom)
      if add > 0:
        cumulativeBottom += [0]*add

      si['kwargs']['bottom'] = cumulativeBottom[0:len(y)]

      for i,yval in enumerate(y):
        cumulativeBottom[i] += yval

def InterleaveBars(plotVars):
  if len(plotVars['SeriesInfo']) > 1:
    increment = plotVars['BarInterleaveOffset']
    for i,si in enumerate(plotVars['SeriesInfo']):
      si['x'] = np.array(si['x']) + i*increment

def InterleaveBarsAndAdjustX(plotVars):
  numSeries = len(plotVars['SeriesInfo'])
  if numSeries > 1:
    increment = plotVars['BarInterleaveOffset']
    offset = -increment*(numSeries-1)/2.0
    for i,si in enumerate(plotVars['SeriesInfo']):
      si['x'] = np.array(si['x']) + i*increment + offset - si['kwargs']['width']/2.0

#Adjusts xvals half of width to the left,
#so that center of bar corresponds to the original xval
def AdjustX(plotVars):
  for i,si in enumerate(plotVars['SeriesInfo']):
    si['x'] = np.array(si['x']) - si['kwargs']['width']/2.0

def OffsetX(plotVars,offset):
  for i,si in enumerate(plotVars['SeriesInfo']):
    si['x'] = np.array(si['x']) + offset

###################################
#
# Some useful combinations of bar fns
#
###################################

def InterleavedAfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (BarInterleaved)'

  Series.numerizeXVals(plotVars)
  InterleaveBarsAndAdjustX(plotVars)
  Series.plotAllSeries(plotVars)
  Common.AfterSubplot(plotVars)

def StackedAfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (BarStacked)'

  StackBars(plotVars)
  Series.numerizeXVals(plotVars)
  AdjustX(plotVars)
  Series.plotAllSeries(plotVars)
  Common.AfterSubplot(plotVars)

def Stacked100PctBeforeSubplot(plotVars):
  Series.BeforeSubplot(plotVars)
  Series.BeforeSubplotAdd100Pct(plotVars)

def Stacked100PctAfterSubplot(plotVars):
  Series.AfterSubplotAdd100Pct(plotVars)
  StackedAfterSubplot(plotVars)

###################################
#
# Bar groups
#
###################################

def GroupBeforeSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Subplot (Group)'

  Series.BeforeSubplot(plotVars)
  plotVars['GroupCount'] = 0
  plotVars['TotalPointsCount'] = 0

  if 'GroupSepartion' not in plotVars:
    plotVars['GroupSeparation'] = 1 #set a default

def BeforeGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Group'

  #Resetting some of the series variables for each group.
  #This is more frequent than for each subplot.
  #See PlotFnsSeries.BeforeSubplot() to compare.
  plotVars['SeriesInfo'] = []
  plotVars['SeriesCount'] = 0
  plotVars['XValsAreNumerical'] = False #Can no longer be treated numerically with grouping

  plotVars['GroupOffset'] = plotVars['GroupCount']*plotVars['GroupSeparation'] + plotVars['TotalPointsCount']
  plotVars['GroupUniqueXVals'] = set()
  plotVars['GroupCount'] += 1

def GroupNumerizeXVals(plotVars):
  xtoint = {}
  inttox = [] #group-specific inttox mapping
  #get labels according to "global order"
  for xlabel in plotVars['InttoX']:
    #GroupUniqueXVals may not contain some xlabels from other groups
    if xlabel in plotVars['GroupUniqueXVals']:
      xtoint[xlabel] = len(inttox)
      inttox.append(xlabel)

  #taken from Series.numerizeXVals()
  for si in plotVars['SeriesInfo']:
    si['xlabels'] = list(si['x'])
    xlabels = si['xlabels']
    x = map(lambda val: xtoint[val]+plotVars['GroupOffset'], xlabels) #replaces each xval by its int-value
    y = si['y']
    zipped = zip(x,y,xlabels)
    zipped.sort() #sorts by x int-values
    si['x'],si['y'],si['xlabels'] = zip(*zipped) #splits the zipped stuff back out

def AfterGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Group'

  #populate the set of unique XVals in this group of series
  for si in plotVars['SeriesInfo']:
    plotVars['GroupUniqueXVals'].update(si['x'])

  GroupNumerizeXVals(plotVars)

  plotVars['TotalPointsCount'] += len(plotVars['GroupUniqueXVals'])

def InterleavedAfterGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Group (BarInterleaved)'

  AfterGroup(plotVars)
  InterleaveBarsAndAdjustX(plotVars)
  Series.plotAllSeries(plotVars)

def StackedAfterGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Group (BarStacked)'

  AfterGroup(plotVars)
  StackBars(plotVars)
  AdjustX(plotVars)
  Series.plotAllSeries(plotVars)

def Stacked100PctAfterGroup(plotVars):
  Series.AfterSubplotAdd100Pct(plotVars)
  StackedAfterGroup(plotVars)

###################################
#
# Default Fns
#
###################################

#Stacked Bar chart
Common.defaultFns['BarStacked'] = {
    'Figure'  : (Common.BeforeFigure, Common.AfterFigure,),
    'Subplot' : (Series.BeforeSubplot, StackedAfterSubplot,),
    'Series'  : (BeforeSeries, Series.AfterSeries,),
    'Point'   : (Series.Point,),
    'Init'    : (Common.Init,),
    'Fini'    : (Common.Fini,),
}

#100% Stacked Bar chart
Common.defaultFns['BarStacked100Pct'] = dict(Common.defaultFns['BarStacked'])
Common.defaultFns['BarStacked100Pct']['Subplot'] = (Stacked100PctBeforeSubplot, Stacked100PctAfterSubplot,)
Common.defaultFns['BarStacked100Pct']['Point'] = (Series.Point100Pct,)

#Interleaved Bar chart
Common.defaultFns['BarInterleaved'] = dict(Common.defaultFns['BarStacked'])
Common.defaultFns['BarInterleaved']['Subplot'] = (Series.BeforeSubplot, InterleavedAfterSubplot,)

#Grouped Stacked Bar chart
Common.defaultFns['GroupedBarStacked'] = {
    'Figure'  : (Common.BeforeFigure, Common.AfterFigure,),
    'Subplot' : (GroupBeforeSubplot, Common.AfterSubplot,),
    'Group'   : (BeforeGroup, StackedAfterGroup,),
    'Series'  : (BeforeSeries, Series.AfterSeries,),
    'Point'   : (Series.Point,),
    'Init'    : (Common.Init,),
    'Fini'    : (Common.Fini,),
}

#Grouped 100% Stacked Bar chart
Common.defaultFns['GroupedBarStacked100Pct'] = dict(Common.defaultFns['GroupedBarStacked'])
Common.defaultFns['GroupedBarStacked100Pct']['Group'] = (Stacked100PctBeforeSubplot, Stacked100PctAfterGroup,)
Common.defaultFns['GroupedBarStacked100Pct']['Point'] = (Series.Point100Pct,)

#Grouped Interleaved Bar chart
Common.defaultFns['GroupedBarInterleaved'] = dict(Common.defaultFns['GroupedBarStacked'])
Common.defaultFns['GroupedBarInterleaved']['Group'] = (BeforeGroup, InterleavedAfterGroup,)
