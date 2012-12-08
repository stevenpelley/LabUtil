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
# Bar
#
###################################

def BeforeSeries(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+SeriesBar'

  Series.BeforeSeries(plotVars)

  plotVars['PlotFunction'] = plotVars['Axes'].bar
  plotVars['PlotFunctionKWArgs'] = {
    'label'     : plotVars['SeriesLabel'],
    'color'     : plotVars['SeriesColor'],
    'bottom'    : 0,
    'width'     : 0.5,
  }

def StackBars(plotVars):
  #determine new bottoms
  if len(plotVars['PlotFunctionList']) > 1:
    cumulativeBottom = []
    for f,x,y,kwargs in plotVars['PlotFunctionList']:
      add = len(y) - len(cumulativeBottom)
      if add > 0:
        cumulativeBottom += [0]*add
      kwargs['bottom'] = cumulativeBottom[0:len(y)]
      for i,yval in enumerate(y):
        cumulativeBottom[i] += yval

#Adjusts xvals half of width to the left,
#so that center of bar corresponds to the original xval
def AdjustX(plotVars):
    for i,(f,x,y,kwargs) in enumerate(plotVars['PlotFunctionList']):
      x = np.array(x) - kwargs['width']
      plotVars['PlotFunctionList'][i] = (f,x,y,kwargs,)

def OffsetX(plotVars,offset):
    for i,(f,x,y,kwargs) in enumerate(plotVars['PlotFunctionList']):
      x = np.array(x) + offset
      plotVars['PlotFunctionList'][i] = (f,x,y,kwargs,)

def AfterSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-SubplotBar'

  StackBars(plotVars)
  AdjustX(plotVars)
  Series.AfterSubplot(plotVars)

###################################
#
# Bar groups
#
###################################

def GroupBeforeSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+SubplotGroup'

  Series.BeforeSubplot(plotVars)
  plotVars['GroupCount'] = 0
  plotVars['TotalSeriesCount'] = 0

def BeforeGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+Group'

  #These variables will now reset for each group too,
  #which is more frequent than for each subplot.
  #See PlotFnsSeries.BeforeSubplot() to compare.
  plotVars['SeriesCount'] = 0
  plotVars['XValsAreNumerical'] = False #Can no longer be treated numerically with grouping
  plotVars['XtoInt'] = {}
  plotVars['DistinctXCount'] = 0

  plotVars['GroupOffset'] = plotVars['GroupCount'] + plotVars['TotalSeriesCount']
  plotVars['GroupCount'] += 1
  
def AfterGroup(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-Group'

  plotVars['TotalSeriesCount'] += plotVars['SeriesCount']

###################################
#
# 100% Bar
#
###################################

def BeforeSubplot100Pct(plotVars):
    Series.BeforeSubplot(plotVars)
    Series.BeforeSubplotAdd100Pct(plotVars)

def AfterSubplot100Pct(plotVars):
  Series.AfterSubplotAdd100Pct(plotVars)
  AfterSubplot(plotVars)

Common.defaultFns['BarStacked'] = {
    'Figure'  : (Common.BeforeFigure, Common.AfterFigure,),
    'Subplot' : (Series.BeforeSubplot, AfterSubplot,),
    'Series'  : (BeforeSeries, Series.AfterSeries,),
    'Point'   : (Series.Point,),
    'Init'    : (Common.Init,),
    'Fini'    : (Common.Fini,),
}

Common.defaultFns['BarStacked100Pct'] = dict(Common.defaultFns['BarStacked'])
Common.defaultFns['BarStacked100Pct']['Subplot'] = (BeforeSubplot100Pct, AfterSubplot100Pct,)
Common.defaultFns['BarStacked100Pct']['Point'] = (Series.Point100Pct,)

###################################
#
# Bar Extras
#
###################################

def PlotFnBeforeBarSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+BarSubplot'
  if 'BeforeBarSubplot_super' not in plotVars:
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
  plotVars['BarTextures'] = [' ', '/', '\\', '//', '\\\\', 'x']

  plotVars['StackColor'] = True
  plotVars['StackHatch'] = True
  plotVars['BarColor']   = False
  plotVars['BarHatch']   = False
  plotVars['BarLabel']   = True

  plotVars['GroupWhiteSpace'] = .2
  plotVars['GroupLabelSpace'] = .2
  plotVars['BarLabelRotation'] = 30

  plotVars['YLim'] = (None, None)
  plotVars['XLim'] = (None, None)
  plotVars['BarLog'] = False

  plotVars['RelativeBarWidth'] = 1.0
  plotVars['BarOffset'] = 0.0

def PlotFnAfterBarSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-BarSubplot'

  ax = plotVars['Axes']
  groups = plotVars['Groups']
  bars = plotVars['Bars']
  stacks = plotVars['Stacks']
  barStruct = plotVars['BarStruct']
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

  if 'BarLog' not in plotVars:
    plotVars['BarLog'] = False

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
  topLim = None
  if 'YLim' in plotVars:
    topLim = plotVars['YLim'][1]
  for barIDX in range(numBars):
    thisBarLabel = bars[barIDX]
    bottoms = np.zeros(numGroups)
    realHeight = np.zeros(numGroups)
    barStart = np.arange(numGroups) + whiteSpace + (barIDX*barWidth)
    for stackIDX in range(numStacks):
      heights = np.array(byGroups[barIDX][stackIDX])
      # create array of bar start locations

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
      plotHeights = np.array(heights)
      if topLim != None:
        for i in range(len(plotHeights)):
          if plotHeights[i] + bottoms[i] > topLim:
            plotHeights[i] = topLim - bottoms[i]
      if stackIDX == 0 and plotVars['BarLog']:
        plotBottoms = None
      else:
        plotBottoms = bottoms
      ax.bar(barStart, plotHeights, barWidth * plotVars['RelativeBarWidth'], bottom=plotBottoms, color=color, hatch=texture, log=plotVars['BarLog'], label=thisBarLabel)
      bottoms = bottoms + plotHeights
      realHeight = realHeight + heights

    # find any bars that went over the y-axis limit and plot their actual height as text
    if topLim != None:
      for i, height in enumerate(realHeight):
        if height > topLim:
          # plot it!
          thisStart = barStart[i]
          plotStr = "{:.0f}".format(height)
          plotVars['ExtraArtists'].append(ax.text(thisStart+(barWidth/2.0), topLim*1.025, plotStr, va="bottom",ha="center"))

  # legend by hand
  lg = ax.legend(title=plotVars['LegendTitle'], loc = plotVars['LegendLocation'])
  plotVars['ExtraArtists'].append(lg)
  for item in lg.get_lines() + lg.get_patches() + lg.get_texts() + [lg.get_title()]:
    plotVars['ExtraArtists'].append(item)
  lg.draw_frame(False)
  plotVars['Legend'] = lg

  ## set up the legend
  #if 'LegendTitle' in plotVars and (stackColor or stackTexture or barColor or barTexture):
  #  # this is a custom legend using proxy artists
  #  # artists are generated for legend support but not drawn on the axes
  #  artists = []
  #  labels = []
  #  # bar artists
  #  if (barColor or barTexture) and numBars > 1:
  #    for barIDX in range(numBars):
  #      color = "None"
  #      hatch = "None"
  #      label = bars[barIDX]
  #      if barColor:
  #        color = plotVars['BarColors'][barIDX % len(plotVars['BarColors'])]
  #      if barTexture:
  #        hatch = plotVars['BarTextures'][barIDX % len(plotVars['BarTextures'])]
  #        # BUG in matplotlib -- legend will not show both hatch and fill
  #        # default to hatch
  #        color = "None"
  #      artists.append(matplotlib.patches.Rectangle((0,0),1,1,color=color,hatch=hatch))
  #      labels.append(label)
  #  # stack artists - start at the last stacks to go top down
  #  if (stackColor or stackTexture) and numStacks > 1:
  #    for stackIDX in range(numStacks-1,-1,-1):
  #      color = "None"
  #      hatch = "None"
  #      label = stacks[stackIDX]
  #      if stackColor:
  #        color = plotVars['BarColors'][stackIDX % len(plotVars['BarColors'])]
  #      if stackTexture:
  #        hatch = plotVars['BarTextures'][stackIDX % len(plotVars['BarTextures'])]
  #        # BUG in matplotlib -- legend will not show both hatch and fill
  #        # default to hatch
  #        color = "None"
  #      artists.append(matplotlib.patches.Rectangle((0,0),1,1,color=color,hatch=hatch))
  #      labels.append(label)
  #  if len(artists) > 0:
  #    if 'LegendBBox' in plotVars:
  #      bbox = plotVars['LegendBBox']
  #    else:
  #      bbox = None
  #    lg = ax.legend(artists, labels, title=plotVars['LegendTitle'], loc = plotVars['LegendLocation'], bbox_to_anchor=bbox)
  #    plotVars['ExtraArtists'].append(lg)
  #    for item in lg.get_lines() + lg.get_patches() + lg.get_texts() + [lg.get_title()]:
  #      plotVars['ExtraArtists'].append(item)
  #    lg.draw_frame(False)
  #    plotVars['Legend'] = lg

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
    ax.set_xticklabels(tickLabels, rotation=plotVars['BarLabelRotation'], va='top', ha='right')
    ax.tick_params(bottom=False)
  else:
    ax.get_xaxis().set_ticks([])

  # set labels for groups
  if 'Group' in plotVars['Labels']:
    # convert to axes coordinates
    # x in data, y in axes
    trans = matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes)
    (bottom, top) = ax.get_ylim()
    for i, group in enumerate(groups):
      groupLabelX = i + whiteSpace + (1.0-whiteSpace)/2.0
      plotVars['ExtraArtists'].append(ax.text(groupLabelX, -plotVars['GroupLabelSpace'], groups[i], va="top", ha="center", transform=trans))

  if 'XLim' in plotVars:
    (newLeft, newRight) = plotVars['XLim']
    [left, right] = plotVars['Axes'].get_xlim()
    if newLeft == None:
      newLeft = left
    if newRight == None:
      newRight = right
    plotVars['Axes'].set_xlim(newLeft, newRight)
  if 'YLim' in plotVars:
    (newBottom, newTop) = plotVars['YLim']
    [bottom, top] = plotVars['Axes'].get_ylim()
    if newBottom == None:
      newBottom = bottom
    if newTop == None:
      newTop = top
    plotVars['Axes'].set_ylim(newBottom, newTop)

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

