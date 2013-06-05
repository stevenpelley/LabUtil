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
# Line
#
###################################

def BeforeSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+SeriesLine'

  Series.BeforeSeries(plotVars)

  plotVars['PlotFunction'] = plotVars['Axes'].plot

  plotVars['LineKWArgs'] = {
    'label'     : plotVars['SeriesLabel'],
    'linestyle' : plotVars['SeriesStyle'],
    'color'     : plotVars['SeriesColor'],
    'marker'    : plotVars['SeriesMarker'],
  }
  if 'UserLineKWArgs' in plotVars:
    plotVars['LineKWArgs'].update(plotVars['UserLineKWArgs'])

  plotVars['PlotFunctionKWArgs'] = dict(plotVars['LineKWArgs'])

###################################
#
# Stacked Line
#
###################################
#
# stacks and shades the different series
# requires that all series are defined over the same domain
#
###################################

def StackLineBeforeSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+SeriesStackLine'

  Series.BeforeSeries(plotVars)
  plotVars['PlotFunction'] = plotVars['Axes'].stackplot
  plotVars['LineKWArgs'] = {
    'colors'     : plotVars['SeriesColors'],
  }
  if 'UserLineKWArgs' in plotVars:
    plotVars['LineKWArgs'].update(plotVars['UserLineKWArgs'])

  plotVars['PlotFunctionKWArgs'] = dict(plotVars['LineKWArgs'])

def StackLineAfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Subplot (StackLine)'
  Series.numerizeXVals(plotVars)

  # combine and check series info
  assert len(plotVars['SeriesInfo']) > 0
  si0 = plotVars['SeriesInfo'][0]
  fn = si0['fn']
  xs = si0['x']
  ys = []
  stack_kwargs = si0['kwargs']

  # NOTE: have to make legend by hand
  legendExtra = {'handles' : [], 'labels' : []}
  for si in plotVars['SeriesInfo']:
    assert len(set(xs) ^ set(si['x'])) == 0, "All series must be defined over same domain! (x values)" # same xs
    ys.append(si['y'])
    legendExtra['labels'].append(si['label'])
  poly_collection = fn(xs, ys, **stack_kwargs)
  for i,p in enumerate(poly_collection):
    dummy = matplotlib.patches.Rectangle((0,0),1,1, fc=plotVars['SeriesColors'][i])
    legendExtra['handles'].append(dummy)
  plotVars['LegendExtraSeries'] = legendExtra

  Series.cleanUpXTicks(plotVars)
  Common.AfterSubplot(plotVars)

###################################
#
# Default Fns
#
###################################
 
Common.defaultFns['Line'] = {
    'Figure'  : (Common.BeforeFigure, Common.AfterFigure,),
    'Subplot' : (Series.BeforeSubplot, Series.AfterSubplot,),
    'Series'  : (BeforeSeries, Series.AfterSeries,),
    'Point'   : (Series.Point,),
    'Init'    : (Common.Init,),
    'Fini'    : (Common.Fini,),
}

Common.defaultFns['StackLine'] = dict(Common.defaultFns['Line'])
Common.defaultFns['StackLine']['Series'] = (StackLineBeforeSeries, Series.AfterSeries,)
Common.defaultFns['StackLine']['Subplot'] = (Series.BeforeSubplot, StackLineAfterSubplot,)
