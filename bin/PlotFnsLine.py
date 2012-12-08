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
  plotVars['PlotFunctionKWArgs'] = {
    'label'     : plotVars['SeriesLabel'],
    'linestyle' : plotVars['SeriesStyle'],
    'color'     : plotVars['SeriesColor'],
    'marker'    : plotVars['SeriesMarker'],
  }
 
Common.defaultFns['Line'] = {
    'Figure'  : (Common.BeforeFigure, Common.AfterFigure,),
    'Subplot' : (Series.BeforeSubplot, Series.AfterSubplot,),
    'Series'  : (BeforeSeries, Series.AfterSeries,),
    'Point'   : (Series.Point,),
    'Init'    : (Common.Init,),
    'Fini'    : (Common.Fini,),
}