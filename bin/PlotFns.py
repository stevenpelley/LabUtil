#!/usr/bin/python

#######################
#
# General Functions
#
#######################

import os
import os.path
import matplotlib
import matplotlib.pyplot as plt
import shutil
import numpy as np

def PlotFnInit(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Plot'
  plotVars['FigureCount'] = 1
  outDir = plotVars['OutputDir']
  if os.path.isdir(outDir):
    shutil.rmtree(outDir)
  elif os.path.isfile(outDir):
    os.remove(outDir)
  os.mkdir(outDir)

def PlotFnFini(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Plot'

def PlotFnBeforeFigure(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+figure'
  plotVars['Figure'] = plt.figure(plotVars['FigureCount'])
  plotVars['Figure'].clf()
  plotVars['FigureCount'] += 1
  plotVars['SubplotCount'] = 1
  plotVars['ExtraArtists'] = []
  if "Figure" in plotVars['Labels']:
    plotVars['FigureTitle'] = plotVars['Labels']['Figure'] % plotVars['ColumnToValue']
  # default subplot dimensions
  plotVars['SubplotDimensions'] = (len(plotVars['SubplotsInFigure'][plotVars['LayerValues']['Figure']]),1)

def PlotFnAfterFigure(plotVars):
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
  fig.savefig(plotVars['OutputDir'] + "/" + filename, format="pdf", transparent=True, bbox_inches="tight", bbox_extra_artists=extraArtists)

def PlotFnBeforeSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+subplot'
  # start a subplot and set up axes printing
  (x,y) = plotVars['SubplotDimensions']
  ax = plotVars['Figure'].add_subplot(x, y, plotVars['SubplotCount'])
  plotVars['SubplotCount'] += 1
  plotVars['Axes'] = ax
  x_ax = ax.get_xaxis()
  x_ax.tick_bottom()
  y_ax = ax.get_yaxis()
  y_ax.tick_left()
  ax.spines['top'].set_color('none')
  ax.spines['right'].set_color('none')

  if 'LegendLocation' not in plotVars:
    plotVars['LegendLocation'] = None

  # create titles for subplot, xaxis, yaxis, and legend
  if "Subplot" in plotVars['Labels']:
    plotVars['SubplotTitle'] = plotVars['Labels']['Subplot'] % plotVars['ColumnToValue']

  if "XAxis" in plotVars['Labels']:
    plotVars['XLabel'] = plotVars['Labels']['XAxis'] % plotVars['ColumnToValue']
    if 'XLabelOnLast' in plotVars and plotVars['XLabelOnLast']:
      if plotVars['SubplotCount'] - 1 != (x * y):
        del plotVars['XLabel']
  if "YAxis" in plotVars['Labels']:
    plotVars['YLabel'] = plotVars['Labels']['YAxis'] % plotVars['ColumnToValue']

  # start collecting limits on axes
  plotVars['XAxisLimits'] = [None, None]
  plotVars['YAxisLimits'] = [None, None]


def PlotFnAfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-subplot'
  if 'SubplotTitle' in plotVars:
    plotVars['Axes'].set_title(plotVars['SubplotTitle'])
  if 'LegendTitle' in plotVars:
    lg = plotVars['Axes'].legend(title=plotVars['LegendTitle'], loc=plotVars['LegendLocation'])
    if lg: 
      lg.draw_frame(False)
    plotVars['Legend'] = lg
  if 'XLabel' in plotVars:
    plotVars['Axes'].set_xlabel(plotVars['XLabel'])
  if 'YLabel' in plotVars:
    plotVars['Axes'].set_ylabel(plotVars['YLabel'])
  # TODO: enforce axes limits or leave to overriding

###############################
#
# Line
#
###############################

def PlotFnBeforeLineSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+LineSubplot'
  PlotFnBeforeSubplot(plotVars)

  if "Line" in plotVars['Labels']:
    plotVars['LegendTitle'] = plotVars['Labels']['Line'] % plotVars['ColumnToValue']
  plotVars['LineCount'] = 0

def PlotFnBeforeLine(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+line'
  lineStyles = ['-', '--', '-.', ":"]
  lineColors = ["b", "g", "r"]
  lineMarkers = ['o','^','s','*','D']

  # set line label
  label = ""
  vals = plotVars['LayerValues']['Line']
  for i, col in enumerate(plotVars['LayerGroups']['Line']):
    val = vals[i]
    label += "%s" % (str(val),)
    if i != len(vals)-1:
      label += " "
  plotVars['LineLabel'] = label

  # set linestyle, color, and marker
  plotVars['LineStyle'] = lineStyles[plotVars['LineCount'] % len(lineStyles)]
  plotVars['LineColor'] = lineColors[plotVars['LineCount'] % len(lineColors)]
  plotVars['LineMarker'] = 'None'

  plotVars['XVals'] = []
  plotVars['YVals'] = []

  plotVars['PlotFunction'] = plotVars['Axes'].plot

def PlotFnAfterLine(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-line'
  plotVars['PlotFunction'](plotVars['XVals'], plotVars['YVals'], label=plotVars['LineLabel'], linestyle=plotVars['LineStyle'], color=plotVars['LineColor'], marker=plotVars['LineMarker'])
  plotVars['LineCount'] += 1

def PlotFnLinePoint(plotVars):
  if plotVars['TraceFunctionCalls']:
    print ' point'
  plotVars['X'] = plotVars['ColumnToValue'][plotVars['LayerGroups']['Point'][0]]
  plotVars['Y'] = plotVars['ColumnToValue'][plotVars['LayerGroups']['Point'][1]]
  plotVars['XVals'].append(plotVars['X'])
  plotVars['YVals'].append(plotVars['Y'])

###################################
#
# Bar
#
###################################

def PlotFnBeforeBarSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+BarSubplot'
  PlotFnBeforeSubplot(plotVars)

  # remember everything and process entire plot at end of subplot
  # Groups = {group label : bars}
  # bars = [[stacks from bottom]] (list of bars, each bar a list of stacks)
  plotVars['BarStruct'] = []
  # keep a list of bars and stacks to keep order and labels consistent
  plotVars['Groups'] = []
  plotVars['Bars'] = []
  plotVars['Stacks'] = []

  plotVars['BarColors'] = ["b", "g", "r", "y",]
  plotVars['BarTextures'] = ['/', '\\', '//', '\\\\', 'x']

  plotVars['StackColor'] = True
  plotVars['StackHatch'] = True
  plotVars['BarColor']   = False
  plotVars['BarHatch']   = False
  plotVars['BarLabel']   = True

def PlotFnAfterBarSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-BarSubplot'

  ax = plotVars['Axes']
  groups = plotVars['Groups']
  bars = plotVars['Bars']
  stacks = plotVars['Stacks']
  barStruct = plotVars['BarStruct']
  barLabelType = plotVars['BarLabel']
  whiteSpace = plotVars['GroupWhiteSpace']
  numGroups = len(groups)
  numBars = len(bars)
  numStacks = len(stacks)

  # set up where to use labels, colors, and textures
  stackColor   = plotVars['StackColor']
  stackTexture = plotVars['StackHatch']
  barColor     = plotVars['BarColor']  
  barTexture   = plotVars['BarHatch']  
  barLabel     = plotVars['BarLabel']  
  assert not (stackColor and barColor)
  assert not (stackTexture and barTexture)

  # first transform into a list format [bar][stack] -> stacks of each group
  # example: byGroups[0][0] gives a list of stack heights in first bar, bottom stack each group
  byGroups = []
  for i, bar in enumerate(bars):
    byGroups.append([])
    for j, stack in enumerate(stacks):
      byGroups[-1].append([])
      for k, group in enumerate(groups):
        byGroups[-1][-1].append(barStruct[k][i][j])

  # width of each bar = (1-whiteSpace)/numBars
  barWidth = (1.0-whiteSpace)/float(numBars)

  # bars start at groupIDX + whiteSpace + barIDX*width
  # group labels at groupIDX + whitespace + (1.0-whitespace)/2.0
  # bar labels at barStart + width/2
  for barIDX in range(numBars):
    bottoms = np.zeros(numGroups)
    for stackIDX in range(numStacks):
      heights = np.array(byGroups[barIDX][stackIDX])
      # create array of bar start locations
      barStart = np.arange(numGroups) + whiteSpace + (barIDX*barWidth)

      # plot this stack across all groups
      # set a color and texture
      color = ''
      if stackColor or barColor:
        if stackColor:
          idx = stackIDX
        elif barColor:
          idx = barIDX
        color = plotVars['BarColors'][idx % len(plotVars['BarColors'])]
      texture = ''
      if stackTexture or barTexture:
        if stackTexture:
          idx = stackIDX
        elif barTexture:
          idx = barIDX
        texture = plotVars['BarTextures'][idx % len(plotVars['BarTextures'])]
      ax.bar(barStart, heights, barWidth, bottom=bottoms, color=color, hatch=texture)

      bottoms = bottoms + heights

  # set up the legend
  if stackColor or stackTexture or barColor or barTexture:
    # this is a custom legend using proxy artists
    # artists are generated for legend support but not drawn on the axes
    artists = []
    labels = []
    # bar artists
    if (barColor or barTexture) and numBars > 1:
      for barIDX in range(numBars):
        color = "None"
        hatch = "None"
        label = bars[barIDX]
        if barColor:
          color = plotVars['BarColors'][barIDX % len(plotVars['BarColors'])]
        if barTexture:
          hatch = plotVars['BarTextures'][barIDX % len(plotVars['BarTextures'])]
        artists.append(matplotlib.patches.Rectangle((0,0),1,1,color=color,hatch=hatch))
        labels.append(label)
    # stack artists - start at the last stacks to go top down
    if (stackColor or stackTexture) and numStacks > 1:
      for stackIDX in range(numStacks):
        color = "None"
        hatch = "None"
        label = stacks[stackIDX]
        if stackColor:
          color = plotVars['BarColors'][stackIDX % len(plotVars['BarColors'])]
        if stackTexture:
          hatch = plotVars['BarTextures'][stackIDX % len(plotVars['BarTextures'])]
          # BUG in matplotlib -- legend will not show both hatch and fill
          # default to hatch
          color = "None"
        artists.append(matplotlib.patches.Rectangle((0,0),1,1,color=color,hatch=hatch))
        labels.append(label)
    if len(artists) > 0:
      lg = ax.legend(artists, labels, title="", loc = plotVars['LegendLocation'])
      lg.draw_frame(False)
      plotVars['Legend'] = lg

  # set up labels for bars
  ax.minorticks_off()
  if barLabel:
    # set xticks and xticklabels
    ticks = []
    tickLabels = []
    for i, group in enumerate(groups):
      for j, bar in enumerate(bars):
        barStart = i + whiteSpace + (j*barWidth) + (barWidth/2.0)
        ticks.append(barStart)
        tickLabels.append(bars[j])
    ax.set_xticks(ticks)
    ax.set_xticklabels(tickLabels, rotation=30, va='top', ha='right')
    ax.tick_params(bottom=False)

  # set labels for groups
  (bottom, top) = ax.get_ylim()
  groupLabelY = -top*.2
  for i, group in enumerate(groups):
    groupLabelX = i + whiteSpace + (1.0-whiteSpace)/2.0
    plotVars['ExtraArtists'].append(ax.text(groupLabelX, groupLabelY, groups[i], va="top", ha="center"))

  PlotFnAfterSubplot(plotVars)

def PlotFnBeforeBarGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+BarGroup'
  if 'Labels' in plotVars and 'Group' in plotVars['Labels']:
    barGroup = plotVars['Labels']['Group'] % plotVars['ColumnToValue']
  else:
    barGroup = plotVars['LayerValues']['Group']
  assert barGroup not in plotVars['Groups']
  plotVars['Groups'].append(barGroup)
  plotVars['BarStruct'].append([])

def PlotFnAfterBarGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-BarGroup'

def PlotFnBeforeBar(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Bar'
  barGroup = plotVars['LayerValues']['Group']
  if 'Labels' in plotVars and 'Bar' in plotVars['Labels']:
    bar = plotVars['Labels']['Bar'] % plotVars['ColumnToValue']
  else:
    bar = plotVars['LayerValues']['Bar']
  barList = plotVars['BarStruct'][-1]
  if bar not in plotVars['Bars']:
    plotVars['Bars'].append(bar)
  # find index and add bar lists for empty bars and this one
  l = len(barList)
  idx = plotVars['Bars'].index(bar)
  for i in range(idx - l + 1): # +1 for this bar
    barList.append([])

def PlotFnAfterBar(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Bar'

def PlotFnBarStack(plotVars):
  if plotVars['TraceFunctionCalls']:
    print 'BarStack'
  barGroup = plotVars['LayerValues']['Group']
  stackList = plotVars['BarStruct'][-1][-1]
  if 'Labels' in plotVars and 'Stack' in plotVars['Labels']:
    stackVal = plotVars['Labels']['Stack'] % plotVars['ColumnToValue']
  else:
    stackVal = plotVars['LayerValues']['Stack'][0]
  stackHeight = plotVars['LayerValues']['Stack'][1]

  if stackVal not in plotVars['Stacks']:
    plotVars['Stacks'].append(stackVal)
  # find index and add 0.0 height stacks for empty stacks
  l = len(stackList)
  idx = plotVars['Stacks'].index(stackVal)
  for i in range(idx - l):
    stackList.append(0.0)
  # now add this height
  stackList.append(stackHeight)

defaultFns = {
  'Line' : {
    'Figure'  : (PlotFnBeforeFigure, PlotFnAfterFigure,),
    'Subplot' : (PlotFnBeforeLineSubplot, PlotFnAfterSubplot,),
    'Line'    : (PlotFnBeforeLine, PlotFnAfterLine,),
    'Point'   : (PlotFnLinePoint,),
    'Init'    : (PlotFnInit,),
    'Fini'    : (PlotFnFini,),
  },
  'Bar' : {
    'Figure'  : (PlotFnBeforeFigure, PlotFnAfterFigure,),
    'Subplot' : (PlotFnBeforeBarSubplot, PlotFnAfterBarSubplot,),
    'Group'   : (PlotFnBeforeBarGroup, PlotFnAfterBarGroup,),
    'Bar'     : (PlotFnBeforeBar, PlotFnAfterBar,),
    'Stack'   : (PlotFnBarStack,),
    'Init'    : (PlotFnInit,),
    'Fini'    : (PlotFnFini,),
  },
}
