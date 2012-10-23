#!/usr/bin/python
# generic plotting framework based on matplotlib
# goals:
#   provide templates to quickly prototype plots without copying code
#   change graph details with specific knowledge of matplotlib by overriding only the necessary portion
#   implement new graph types by defining layers and their functions
#
# for each function and template list important variables
#
# general data is expected to have fields given by tuple "Columns"
# and rows of values as a list of tuples in "Rows"
import matplotlib 
import matplotlib.pyplot as plt
import operator
import shutil
import os
import os.path
import collections

##################
#
# line plot functions
#
##################

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

  # create titles for subplot, xaxis, yaxis, and legend
  if "Subplot" in plotVars['Labels']:
    plotVars['SubplotTitle'] = plotVars['Labels']['Subplot'] % plotVars['ColumnToValue']
  if "Line" in plotVars['Labels']:
    plotVars['LegendTitle'] = plotVars['Labels']['Line'] % plotVars['ColumnToValue']
  if "XAxis" in plotVars['Labels']:
    plotVars['XLabel'] = plotVars['Labels']['XAxis'] % plotVars['ColumnToValue']
    if 'XLabelOnLast' in plotVars and plotVars['XLabelOnLast']:
      if plotVars['SubplotCount'] - 1 != (x * y):
        del plotVars['XLabel']
  if "YAxis" in plotVars['Labels']:
    plotVars['YLabel'] = plotVars['Labels']['YAxis'] % plotVars['ColumnToValue']

  if 'LegendLocation' not in plotVars:
    plotVars['LegendLocation'] = None

  # start collecting limits on axes
  plotVars['XAxisLimits'] = [None, None]
  plotVars['YAxisLimits'] = [None, None]

  plotVars['LineCount'] = 0

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

defaultFns = {
  'Line' : {
    'Figure'  : (PlotFnBeforeFigure, PlotFnAfterFigure,),
    'Subplot' : (PlotFnBeforeSubplot, PlotFnAfterSubplot,),
    'Line'    : (PlotFnBeforeLine, PlotFnAfterLine,),
    'Point'   : (PlotFnLinePoint,),
    'Init'    : (PlotFnInit,),
    'Fini'    : (PlotFnFini,),
  },
}

##################
#
# plot function iterates over all groups
#
##################

# organize data and iterate over layers and data, calling necessary functions
# vars:
# all in reorder()
# keep sets of current values in ['LayerValues'][LayerName] as tuples
def plot(plotVars):
  reorder(plotVars) # reorder columns and rows
  setDefaultFns(plotVars) # make sure all layer functions are set
  setupFigureSubplots(plotVars) # determines the number of subplots per figure

  # iterate over layers and call necessary functions
  startAllLayers(plotVars)
  for i, row in enumerate(plotVars['Rows']):
    layers = getLayersToUpdate(plotVars, row)
    endLayers(plotVars, layers)
    # update plot state
    plotVars['RowIndex'] = i
    updateLayerState(plotVars, row)
    startLayers(plotVars, layers)
    # process point
    processPoint(plotVars)
  endAllLayers(plotVars)

# reorder columns and sort rows based on plot layers
def reorder(plotVars):
  # order columns
  columnsList = []
  for layer in plotVars['Layers']:
    for item in plotVars['LayerGroups'][layer]:
      assert item in plotVars['Columns']
      columnsList.append(item)

  # reorder columns within tuples
  newRows = []
  for r in plotVars['Rows']:
    rList = []
    for c in columnsList:
      oldIDX = plotVars['Columns'].index(c)
      rList.append(r[oldIDX])
    newRow = tuple(rList)
    newRows.append(newRow)

  plotVars['Columns'] = tuple(columnsList)
  plotVars['Rows'] = newRows

  # sort tuples appropriately
  for i in range(len(plotVars['Columns'])-1, -1, -1):
    columnName = plotVars['Columns'][i]
    reverse = 'ReverseColumns' in plotVars and columnName in plotVars['ReverseColumns']
    plotVars['Rows'].sort(reverse=reverse, key=operator.itemgetter(i))

# any layer without an entry in plotVars['LayerFns'] or when a value is None
# should take the default function
#
# Take default functions from plotVars['DefaultFns'] (e.g. 'Line', 'Histogram')
def setDefaultFns(plotVars):
  singleFunctionLayers = [plotVars['Layers'][-1], "Init", "Fini"]
  layersPlusInit = plotVars['Layers'] + ['Init', 'Fini']
  if 'DefaultFns' not in plotVars:
    # verify that all layers have functions
    assert 'LayerFns' in plotVars
    for layer in layersPlusInit:
      assert layer in plotVars['layerFns']
      FnTup = plotVars['layerFns'][layer]
      assert isinstance(FnTup, tuple)
      if layer not in singleFunctionLayers: # start and end
        assert len(FnTup) == 2
        assert FnTup[0] != None
        assert FnTup[1] != None
      else:
        assert len(FnTup) == 1
        assert FnTup[0] != None

  else:
    assert plotVars['DefaultFns'] in defaultFns, "don't have applicable default functions"
    defaults = defaultFns[plotVars['DefaultFns']]
    for layer in layersPlusInit:
      if layer in defaults:
        if layer not in singleFunctionLayers: # start and end
          assert len(defaults[layer]) == 2
        else:
          assert len(defaults[layer]) == 1
    
    # fill in defaults for any missing functions in LayerFns
    if 'LayerFns' not in plotVars: # use all defaults
      plotVars['LayerFns'] = {}
    for layer in layersPlusInit:
      if layer not in plotVars['LayerFns']: # fill defaults
        plotVars['LayerFns'][layer] = defaults[layer]
      else: # fill in for None
        assert isinstance(plotVars['LayerFns'][layer], tuple)
        if layer not in singleFunctionLayers: # start and end
          assert len(plotVars['LayerFns'][layer]) == 2
          FnList = list(plotVars['LayerFns'][layer])
          if plotVars['LayerFns'][layer][0] == None:
            FnList[0] = defaults[layer][0]
          if plotVars['LayerFns'][layer][1] == None:
            FnList[1] = defaults[layer][1]
          plotVars['LayerFns'][layer] = tuple(FnList)
        else:
          assert len(plotVars['LayerFns'][layer]) == 1
          if plotVars['Layers'][0] == None:
            plotVars['LayerFns'][layer] = (defaults[layer][0],)

# at the beginning of the plot loop start every layer and set LayerValues
# do not process the first point
def startAllLayers(plotVars):
  updateLayerState(plotVars, plotVars['Rows'][0])
  plotVars['LayerFns']['Init'][0](plotVars)
  for layer in plotVars['Layers']:
    if layer != plotVars['Layers'][-1]: # start and end
      startLayer(plotVars, layer)

def endAllLayers(plotVars):
  # state already at the end
  for layer in reversed(plotVars['Layers']):
    if layer != plotVars['Layers'][-1]: # start and end
      endLayer(plotVars, layer)

  plotVars['LayerFns']['Fini'][0](plotVars)

# return all layers who's value has changed since the last row
# never return the "Point" layer
# make sure to account for empty layer groups:
#   an empty layer changes if the layer above changes
#   (e.g. empty subplot changes when figure changes)
def getLayersToUpdate(plotVars, row):
  oldVals = plotVars['LayerValues']
  newVals = getCurrentLayerValues(plotVars, row)
  listOfChangedLayers = []
  lastChanged = False
  for layer in plotVars['Layers']:
    layerEmpty = len(newVals[layer]) == 0
    if (oldVals[layer] != newVals[layer] or (layerEmpty and lastChanged)) and layer != plotVars['Layers'][-1]:
      listOfChangedLayers.append(layer)
      lastChanged = True
    else:
      lastChanged = False
  return listOfChangedLayers

def startLayers(plotVars, layers):
  for layer in plotVars['Layers']:
    if layer != plotVars['Layers'][-1] and layer in layers: # start and end
      startLayer(plotVars, layer)

def endLayers(plotVars, layers):
  for layer in reversed(plotVars['Layers']):
    if layer != plotVars['Layers'][-1] and layer in layers: # start and end
      endLayer(plotVars, layer)

def updateLayerState(plotVars, row):
  plotVars['LayerValues'] = getCurrentLayerValues(plotVars, row)
  plotVars['Row'] = row
  colToVal = {}
  for i, col in enumerate(plotVars['Columns']):
    colToVal[col] = row[i]
  plotVars['ColumnToValue'] = colToVal

def processPoint(plotVars):
  plotVars['LayerFns']['Point'][0](plotVars)

# returns {layer -> tuple of values in layer}
def getCurrentLayerValues(plotVars, row):
  currentValues = {}
  for layer in plotVars['Layers']:
    currentLayerList = []
    for item in plotVars['LayerGroups'][layer]:
      currentLayerList.append(row[plotVars['Columns'].index(item)])
    currentValues[layer] = tuple(currentLayerList)
  return currentValues

def startLayer(plotVars, layer):
  plotVars['LayerFns'][layer][0](plotVars)

def endLayer(plotVars, layer):
  plotVars['LayerFns'][layer][1](plotVars)

# create dict 'SubplotsInFigure'
# {(tuple of figure values) -> set(tuple of subplot values)}
# thus len(SubplotsInFigure[figure vals]) is the number of subplots in figure
def setupFigureSubplots(plotVars):
  if 'Subplot' not in plotVars['Layers']: return
  haveFigure = 'Figure' in plotVars['Layers']
  subplotsInFigure = collections.defaultdict(set)
  layerValues = getCurrentLayerValues(plotVars, plotVars['Rows'][0])
  for row in plotVars['Rows']:
    oldValues = layerValues
    layerValues = getCurrentLayerValues(plotVars, row)
    if haveFigure:
      figureChanged = oldValues['Figure'] != layerValues['Figure']
    else:
      figureChanged = False
    subplotChanged = oldValues['Subplot'] != layerValues['Subplot']
    if figureChanged or subplotChanged:
      subplotsInFigure[oldValues['Figure']].add(oldValues['Subplot'])
  # last  needs to be added
  subplotsInFigure[layerValues['Figure']].add(layerValues['Subplot'])
  plotVars['SubplotsInFigure'] = subplotsInFigure

###      # fix any axes limits
###      # if None given keep the old one
###      if 'xlim' in subs:
###        lim = list(ax.get_xlim())
###        for j in [0,1]:
###          if subs['xlim'][j] != None:
###            lim[j] = subs['xlim'][j]
###        ax.set_xlim(lim)
###      if 'ylim' in subs:
###        lim = list(ax.get_ylim())
###        for j in [0,1]:
###          if subs['ylim'][j] != None:
###            lim[j] = subs['ylim'][j]
###        ax.set_ylim(lim)

#def plotExplodingPie(subs, figureCount = 1):
#  wedgeColors = ['b', 'g', 'r', 'c', 'm', 'y']
#
#  (tupNames, tups, axesRanges) = reorderTups(subs, ('figure', 'explode', 'wedge', 'count'))
#  # add a dummy tuple to the beginning
#  tups.insert(0, 0)
#
#  for i,t in enumerate(tups):
#    first = i == 0
#    last = i == len(tups) - 1
#    if not first:
#      constList = setConstList(t, axesRanges)
#    if last or first:
#      doneFigure = True
#      doneExplode = True
#    else:
#      nextConstList = setConstList(tups[i+1], axesRanges)
#      doneFigure = constList[0] != nextConstList[0]
#      doneExplode = doneFigure or constList[1] != nextConstList[1]
#
#    # we do not know the sizes yet so we can't plot the correct white space
#    # need to keep track of everything and plot when entire figure is done
#
#    substringDict = {}
#    if not first:
#      for j, tn in enumerate(tupNames):
#        substringDict[tn] = str(t[j])
#
#      wedgeLabel = ""
#      for (j, val) in enumerate(constList[2]):
#        wedgeLabel += str(val)
#        if j != axesRanges[2][1]-1:
#          wedgeLabel += " "
#      if wedgeLabel not in wedgeLabels:
#        wedgeLabels.append(wedgeLabel)
#
#      for j, field in enumerate(tupNames[axesRanges[3][0]:axesRanges[3][0] + axesRanges[3][1]]):
#        # constList[3] has the tuple of values
#        val = constList[3][j]
#        if 'hatches' in subs and field in subs['hatches']:
#          hatch = subs['hatches'][field]
#        else:
#          hatch = ""
#        wedges[-1].append(val)
#        wedgeNum = wedgeLabels.index(wedgeLabel)
#        colors[-1].append( wedgeColors[wedgeNum % len(wedgeColors)] )
#        hatches[-1].append(hatch)
#
#        #print constList[2][0]
#        #print colors[-1][-1]
#
#      wedgeCount += 1
#
#    ############################
#    #                          #
#    # finish up previous plot  #
#    #                          #
#    ############################
#
#    if doneExplode and not first:
#      if 'explode' in subs['labels']:
#        explodeLabels.append(subs['labels']['explode'] % substringDict)
#      if 'explosion' in subs and constList[1][0] in subs['explosion']:
#        thisExplosion = subs['explosion'][constList[1][0]]
#      elif 'defaultExplosion' in subs:
#        thisExplosion = subs['defaultExplosion']
#      else:
#        thisExplosion = 0.0
#      explosion.append(thisExplosion)
#
#    if doneFigure and not first:
#      wedgeNums = range(len(wedges))
#
#      # now we have all the data we need.  Plot the graph
#      left = 0.15
#      bottom = 0.15
#      width = 0.7
#      height = 0.7
#
#      totalSum = 0.0
#      #for j in range(len(wedges)):
#      for j in wedgeNums:
#        l = wedges[j]
#        totalSum += sum(l)
#      fig = plt.figure(figureCount, figsize=(8,8))
#      figureCount += 1
#
#      # iterate over the exploded wedges
#      whitespace = 0.0
#      for j in wedgeNums:
#        theseWedges = wedges[j]
#        theseColors = ["b"] + colors[j] + ["b"]
#        theseHatches = [""] + hatches[j] + [""]
#
#        offset = explosion[j]
#        rotation = (whitespace + .5*sum(theseWedges)) / totalSum
#        radians = rotation*2.0*math.pi
#        ax = fig.add_axes([left+offset*math.cos(radians), bottom+offset*math.sin(radians), width, height], frameon=False)
#        trailing = totalSum - (whitespace + sum(theseWedges))
#        x = [whitespace] + list(theseWedges) + [trailing]
#
#        patches, texts = ax.pie(x, colors=theseColors)
#        for k in [0, len(x)-1]:
#          patches[k].set_visible(False)
#        for k in range(len(theseHatches)):
#          patches[k].set_hatch(theseHatches[k])
#
#        # new axis for the wedge label
#        if len(wedges) > 1:
#          ax = fig.add_axes([left+offset*math.cos(radians), bottom+offset*math.sin(radians), width, height], frameon=False)
#          x = [whitespace] + [sum(theseWedges)] + [trailing]
#          theseExplodeLabels = ["", explodeLabels[j], ""]
#          patches, texts = ax.pie(x, labels=theseExplodeLabels)
#          for text in texts:
#            extraArtists.append(text)
#          for p in patches:
#            p.set_visible(False)
#
#        whitespace += sum(theseWedges)
#
#      # create a totally transparent large centered pie graph to make the legend
#      ax = fig.add_axes([0,0,1,1], frameon=False)
#      x = [1] * len(wedgeLabels)
#      theseHatches = [""] * len(wedgeLabels)
#      theseColors = []
#      theseLabels = list(wedgeLabels)
#      for j in range(len(wedgeLabels)):
#        theseColors.append(wedgeColors[j % len(wedgeColors)])
#
#      # add plots for hatches.  Make the color white
#      # first for any wedges without hatches
#      wedgeNames = tupNames[axesRanges[3][0]:axesRanges[3][0]+axesRanges[3][1]]
#      for wn in wedgeNames:
#        if 'hatches' not in subs or ('hatches' in subs and wn not in subs['hatches']):
#          x.append(1)
#          theseHatches.append("")
#          theseColors.append("w")
#          theseLabels.append(wn)
#      if 'hatches' in subs:
#        for name, hatch in subs['hatches'].items():
#          x.append(1)
#          theseHatches.append(hatch)
#          theseColors.append("w")
#          theseLabels.append(name)
#
#      patches,texts = ax.pie(x,labels=theseLabels,colors=theseColors)
#      for j, hatch in enumerate(theseHatches):
#        patches[j].set_hatch(hatch)
#
#      legendLoc = None
#      if 'legendLoc' in subs:
#        legendLoc = subs['legendLoc']
#      legendTitle = subs['labels']['wedge'] % substringDict
#      lg = ax.legend(title=legendTitle, loc=legendLoc)
#      for l in lg.get_children():
#        extraArtists.append(l)
#      lg.draw_frame(False)
#      for p in patches:
#        p.set_visible(False)
#      for t in texts:
#        t.set_visible(False)
#
#      # figure title
#      if "figure" in subs["labels"]:
#        s = subs['labels']['figure'] % substringDict
#        if len(wedges) == 1:
#          explodeField = tupNames[axesRanges[1][0]]
#          s += ", %s: %s" % (explodeField, substringDict[explodeField])
#        extraArtists.append(fig.suptitle(s))
#
#      figName = ""
#      # j starts at axesRanges for figure
#      for j, val in enumerate(constList[0]):
#        figName += "%s_%s" % (tupNames[j], str(val))
#        if j != len(constList[0]) - 1:
#          figName += "__"
#      saveFormat = "pdf" # default
#      if "saveFormat" in subs:
#        saveFormat = subs['saveFormat']
#      fig.savefig(subs['plotDir'] + "/" + figName + "." + saveFormat, format=saveFormat, transparent=True, bbox_extra_artists=extraArtists, bbox_inches="tight")
#        
#
#    #############################
#    #                           #
#    #    now create new things  #
#    #                           #
#    #############################
#
#    if doneFigure and not last:
#      wedges = []
#      colors = []
#      hatches = []
#      explodeLabels = []
#      explosion = []
#      wedgeLabels = [] # whenever we add a new wedge add to this if we haven't seen it yet
#      extraArtists = []
#
#    if doneExplode and not last:
#      wedges.append([])
#      colors.append([])
#      hatches.append([])
#      wedgeCount = 0
#

