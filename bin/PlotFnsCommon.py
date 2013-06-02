#!/usr/bin/python

import os
import os.path
import matplotlib
import matplotlib.pyplot as plt
import shutil
import numpy as np

#######################
#
# General Functions
#
#######################

defaultFns = {}

def Init(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Plot'

  outDir = plotVars['OutputDir']
  if os.path.isdir(outDir):
    shutil.rmtree(outDir)
  elif os.path.isfile(outDir):
    os.remove(outDir)
  os.mkdir(outDir)
  
  plotVars['FigureCount'] = 0

def Fini(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Plot'

def BeforeFigure(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+figure'

  plotVars['FigureCount'] += 1
  plotVars['Figure'] = plt.figure(plotVars['FigureCount'])
  plotVars['Figure'].clf()
  plotVars['ExtraArtists'] = []

  if "Figure" in plotVars['Labels']:
    plotVars['FigureTitle'] = plotVars['Labels']['Figure'] % plotVars['ColumnToValue']
  # default subplot dimensions
  plotVars['SubplotDimensions'] = (len(plotVars['SubplotsInFigure'][plotVars['LayerValues']['Figure']]),1)
  plotVars['Axes'] = None
  plotVars['SubplotCount'] = 0

def AfterFigure(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-figure'

  fig = plotVars['Figure']
  extraArtists = plotVars['ExtraArtists']

  #### set up figure title
  if 'FigureTitle' in plotVars:
    extraArtists.append(fig.suptitle(plotVars['FigureTitle']))

  # create the filename and save figure
  if 'Figure' not in plotVars['LayerGroups'] or len(plotVars['LayerGroups']['Figure']) == 0:
    filename = "plot"
  else:
    filename = ""
    figVals = plotVars['LayerValues']['Figure']
    for i, layer in enumerate(plotVars['LayerGroups']['Figure']):
      layerVal = figVals[i]
      filename += "%s_%s" % (str(layer), str(layerVal))
      if i != len(plotVars['LayerGroups']['Figure'])-1: # not last
        filename += "__"
  filename += ".pdf"
  fig.savefig(plotVars['OutputDir'] + "/" + filename, transparent=True, bbox_inches="tight", bbox_extra_artists=extraArtists)

def BeforeSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+subplot'
  # start a subplot and set up axes printing
  plotVars['SubplotCount'] += 1
  (x,y) = plotVars['SubplotDimensions']
  ax = plotVars['Figure'].add_subplot(x, y, plotVars['SubplotCount'])
  plotVars['Axes'] = ax

  x_ax = ax.get_xaxis()
  x_ax.tick_bottom()
  y_ax = ax.get_yaxis()
  y_ax.tick_left()
  ax.spines['top'].set_color('none')
  ax.spines['right'].set_color('none')

  # Set up plotVars['LegendKWargs'], a dict
  plotVars['LegendKWArgs'] = {
      'loc'     : None,
      'frameon' : False,
  }
  if 'UserLegendKWArgs' in plotVars:
    plotVars['LegendKWArgs'].update(plotVars['UserLegendKWArgs'])

  # create titles for subplot, xaxis, yaxis, and legend
  if 'Subplot' in plotVars['Labels']:
    plotVars['SubplotTitle'] = plotVars['Labels']['Subplot'] % plotVars['ColumnToValue']

  if 'XAxis' in plotVars['Labels']:
    plotVars['XLabel'] = plotVars['Labels']['XAxis'] % plotVars['ColumnToValue']
    if 'XLabelOnLast' in plotVars and plotVars['XLabelOnLast']:
      if plotVars['SubplotCount'] != (x * y):
        del plotVars['XLabel']
  if 'YAxis' in plotVars['Labels']:
    plotVars['YLabel'] = plotVars['Labels']['YAxis'] % plotVars['ColumnToValue']

  # start collecting limits on axes
  plotVars['XAxisLimits'] = [None, None]
  plotVars['YAxisLimits'] = [None, None]


def AfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-subplot'

  if 'SubplotTitle' in plotVars:
    plotVars['Axes'].set_title(plotVars['SubplotTitle'])
  if 'LegendTitle' in plotVars:
    plotVars['Legend'] = plotVars['Axes'].legend(title=plotVars['LegendTitle'], **plotVars['LegendKWArgs'])
    plotVars['ExtraArtists'].append(plotVars['Legend'])
  if 'XLabel' in plotVars:
    plotVars['Axes'].set_xlabel(plotVars['XLabel'])
  if 'YLabel' in plotVars:
    plotVars['Axes'].set_ylabel(plotVars['YLabel'])
  # TODO: enforce axes limits or leave to overriding

# return the string label for the layer
# each plotVars['Labels'] may be a string or function
def makeLayerLabel(plotVars, layer):
  if layer in plotVars['Labels']:
    entry = plotVars['Labels'][layer]
    import types
    assert isinstance(entry, str) or isinstance(entry, types.FunctionType), "Layer label inputs must be string or function"
    if isinstance(entry, str):
      return entry.format(**plotVars['ColumnToValue'])
    elif isinstance(entry, types.FunctionType):
      ret = entry(plotVars['ColumnToValue'])
      assert isinstance(ret, str), "return of layer label function must be str"
      return ret
  else:
    return str(plotVars['LayerValues'][layer])
