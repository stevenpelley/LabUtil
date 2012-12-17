#!/usr/bin/python

import numpy as np
import matplotlib

import PlotFnsCommon as Common
import PlotFnsSeries as Series

###################################
#
# Common bar setup
#
###################################

def BeforeSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Series (Bar)'

  Series.BeforeSeries(plotVars)

  #PlotFunction and PlotFunctionKWArgs are used in PlotFnsSeries.AfterSeries()
  plotVars['PlotFunction'] = plotVars['Axes'].bar

  plotVars['BarKWArgs'] = {
    'bottom'    : 0,
    'align'     : 'center',
    'linewidth' : 0.5,
    'width'     : 0.8,
    'label'     : plotVars['SeriesLabel'],
    'color'     : plotVars['SeriesColor'],
  }
  if 'UserBarKWArgs' in plotVars:
    plotVars['BarKWArgs'].update(plotVars['UserBarKWArgs'])

  plotVars['PlotFunctionKWArgs'] = dict(plotVars['BarKWArgs'])

###################################
#
# These utility functions are to be called after all series are collected
# ie. At the end of a subplot, or at the end of a group
#
###################################

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

def InterleaveBarsCentered(plotVars):
  numSeries = len(plotVars['SeriesInfo'])
  if numSeries > 1:
    increment = plotVars['BarInterleaveOffset']
    offset = -increment*(numSeries-1)/2.0
    for i,si in enumerate(plotVars['SeriesInfo']):
      si['x'] = np.array(si['x']) + i*increment + offset

###################################
#
# Some useful combinations of bar fns
# for plots without groups
#
###################################

def InterleavedAfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (BarInterleaved)'

  Series.numerizeXVals(plotVars)
  InterleaveBarsCentered(plotVars)
  Series.plotAllSeries(plotVars)
  Series.cleanUpXTicks(plotVars)
  Common.AfterSubplot(plotVars)

def StackedAfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (BarStacked)'

  StackBars(plotVars)
  Series.numerizeXVals(plotVars)
  Series.plotAllSeries(plotVars)
  Series.cleanUpXTicks(plotVars)
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
#
# Important implementation notes:
# Previously, a subplot consisted of several series of bars, each with a color and/or hatch.
# These could be interleaved or stacked.
# Now, a group takes on the role of a subplot, and takes one section of the x-axis.
# To simplify things, we do not allow a numerical x-axis for groups. That is, the integer mapping
# of an xlabel is used to locate the xlabel on the x-axis.
# Groups are offset by plotVars['GroupSeparation']. Thus, xticks for a group of series are integer
# increments starting from the current plotVars['GroupOffset'] (see how this is calculated).
# The unique series index maintained at subplot granularity is still used to determine color and/or hatch.
# It is probably preferable to maintain this at the top level of the Init functions, since we want all
# corresponding series to have the same color/hatch/marker etc. We'll see.
#
# This sort of implementation benefits from a lot of code re-use. For example, setting the legend title
# to the "Series" label in PlotFnsSeries.BeforeSubplot() still works here.
###################################

def GroupBeforeSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Subplot (Group)'

  # do not allow XLabel because we will have group labels!
  if 'Labels' in plotVars and 'XAxis' in plotVars['Labels']: del plotVars['Labels']['XAxis']

  Series.BeforeSubplot(plotVars)
  plotVars['GroupCount'] = 0
  plotVars['TotalPointsCount'] = 0 #used in plotVars['GroupOffset'] -- number of bars observed

  #Aggregates the xticks and xticklabels across all groups in the subplot
  plotVars['AggregateXTicks'] = []
  plotVars['AggregateXTickLabels'] = []

  if 'GroupSeparation' not in plotVars:
    plotVars['GroupSeparation'] = 1 #set a default

def GroupCleanUpXTicks(plotVars):
    ax = plotVars['Axes']
    ax.minorticks_off()
    ax.set_xticks(plotVars['AggregateXTicks'])
    ax.set_xticklabels(plotVars['AggregateXTickLabels'])
    ax.tick_params(bottom='off')

def GroupSetXLim(plotVars):
  left = -.5 * plotVars['GroupSeparation']
  right = (plotVars['GroupCount']-.5) * plotVars['GroupSeparation'] + plotVars['TotalPointsCount']
  plotVars['Axes'].set_xlim(left,right)

def GroupAfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (Group)'

  GroupCleanUpXTicks(plotVars)
  GroupSetXLim(plotVars)

  Common.AfterSubplot(plotVars)

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

#perform once per group
def GroupNumerizeXVals(plotVars):
  xtoint = {}
  inttox = [] #group-specific inttox mapping
  #get labels according to "global order"
  for xlabel in plotVars['InttoX']:
    #GroupUniqueXVals may not contain some xlabels from other groups
    if xlabel in plotVars['GroupUniqueXVals']:
      xtoint[xlabel] = len(inttox)+plotVars['GroupOffset']
      inttox.append(xlabel)
 
  #These two lines ensure that xtick labels end up where they should be.
  #The rule for this implementation is that xticks are on integer increments starting from each group offset.
  #Notice that other functions are subsequently called to adjust x positions.
  #Eg. InterleaveBarsCentered... These end up doing the right thing, but users should be(a)ware.
  plotVars['AggregateXTicks'].extend(np.arange(len(inttox))+plotVars['GroupOffset'])
  plotVars['AggregateXTickLabels'].extend(inttox)

  #taken from Series.numerizeXVals()
  for si in plotVars['SeriesInfo']:
    si['xlabels'] = list(si['x'])
    xlabels = si['xlabels']
    x = map(lambda val: xtoint[val], xlabels) #replaces each xval by its int-value
    y = si['y']
    zipped = zip(x,y,xlabels)
    zipped.sort() #sorts by x int-values
    si['x'],si['y'],si['xlabels'] = zip(*zipped) #splits the zipped stuff back out

def GroupPlotAllSeries(plotVars):
  for si in plotVars['SeriesInfo']:
    si['fn']( si['x'],si['y'],**si['kwargs'] )

def PlotGroupLabel(plotVars, text, XOffset, y):
  ax = plotVars['Axes']
  trans = matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes)
  plotVars['ExtraArtists'].append(ax.text(XOffset, y, text, va="top", ha="center", transform=trans))

def AfterGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Group'

  #populate the set of unique XVals in this group of series
  for si in plotVars['SeriesInfo']:
    plotVars['GroupUniqueXVals'].update(si['x'])

  GroupNumerizeXVals(plotVars)

  # plot the group label
  groupLoc = plotVars['GroupOffset'] + ( (len(plotVars['GroupUniqueXVals'])-1.0) / 2.0)
  PlotGroupLabel(plotVars, Common.makeLayerLabel(plotVars, 'Group'), groupLoc, -.08)

  plotVars['TotalPointsCount'] += len(plotVars['GroupUniqueXVals'])

def InterleavedAfterGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Group (BarInterleaved)'

  AfterGroup(plotVars)
  InterleaveBarsCentered(plotVars)
  GroupPlotAllSeries(plotVars)

def StackedAfterGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Group (BarStacked)'

  AfterGroup(plotVars)
  StackBars(plotVars)
  GroupPlotAllSeries(plotVars)

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
    'Subplot' : (GroupBeforeSubplot, GroupAfterSubplot,),
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
