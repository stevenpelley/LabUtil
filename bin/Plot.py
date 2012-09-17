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

##################
#
# line plot functions
#
##################

# objects:
# Figure
# FigureCount
# SubplotCount
# Axes
# XList
# YList
# Labels
# OutputDir
def PlotFnLineInit(plotVars):
  print '+Plot'
def PlotFnLineFini(plotVars):
  print '-Plot'
def PlotFnLineBeforeFigure(plotVars):
  print '+figure'
  if 'FigureCount' not in plotVars:
    plotVars['FigureCount'] = 1
  plotVars['Figure'] = plt.figure(plotVars['FigureCount'])
  plotVars['FigureCount'] += 1
  plotVars['SubplotCount'] = 1
def PlotFnLineAfterFigure(plotVars):
  print '-figure'
def PlotFnLineBeforeSubplot(plotVars):
  print '+subplot'
def PlotFnLineAfterSubplot(plotVars):
  print '-subplot'
def PlotFnLineBeforeLine(plotVars):
  print '+line'
def PlotFnLineAfterLine(plotVars):
  print '-line'
def PlotFnLinePoint(plotVars):
  print ' point'

##################
#
# plot function iterates over all groups
#
##################

# every layer has a tuple of functions
# 2 functions are taken as before and after
# 1 function as the single function for that point
#
# always consider the Init and Fini layers as point layers at start and end
defaultFns = {
  'Line' : {
    'Figure'  : (PlotFnLineBeforeFigure, PlotFnLineAfterFigure,),
    'Subplot' : (PlotFnLineBeforeSubplot, PlotFnLineAfterSubplot,),
    'Line'    : (PlotFnLineBeforeLine, PlotFnLineAfterLine,),
    'Point'   : (PlotFnLinePoint,),
    'Init'    : (PlotFnLineInit,),
    'Fini'    : (PlotFnLineFini,),
  },
}

# organize data and iterate over layers and data, calling necessary functions
# vars:
# all in reorder()
# keep sets of current values in ['LayerValues'][LayerName] as tuples
def plot(plotVars):
  # reorder columns and sort rows
  reorder(plotVars)

  setDefaultFns(plotVars)

  # iterate over layers and call necessary functions
  startAllLayers(plotVars)
  for i, row in enumerate(plotVars['Rows']):
    layers = getLayersToUpdate(plotVars, row)
    endLayers(plotVars, layers)
    # update plot state
    updateLayerState(plotVars, row)
    startLayers(plotVars, layers)
    # process point
    processPoint(plotVars)
  endAllLayers(plotVars)

# reorder columns and sort rows based on plot layers
# important vars:
#   Columns
#   Rows
#   Layers
#   LayerGroups
#   ReverseColumns
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

  elif plotVars['DefaultFns'] in defaultFns:
    defaults = defaultFns[plotVars['DefaultFns']]
    for layer in layersPlusInit:
      assert layer in defaults
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
          if plotVars['Layers'][0] == None:
            FnList[0] = defaults[layer][0]
          if plotVars['Layers'][1] == None:
            FnList[1] = defaults[layer][1]
          plotVars['LayerFns'][layer] = tuple(FnList)
        else:
          assert len(plotVars['LayerFns'][layer]) == 1
          if plotVars['Layers'][0] == None:
            plotVars['LayerFns'][layer] = (defaults[layer][0],)

  else:
    assert False, "Template not defined"

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
def getLayersToUpdate(plotVars, row):
  oldVals = plotVars['LayerValues']
  newVals = getCurrentLayerValues(plotVars, row)
  listOfChangedLayers = []
  for layer in plotVars['Layers']:
    if oldVals[layer] != newVals[layer] and layer != plotVars['Layers'][-1]:
      listOfChangedLayers.append(layer)
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

###def plotLine(subs, figureCount = 1):
###  lineTypes = ['-', '--', '-.', ":"]
###  lineColors = ["b", "g", "r"]
###  lineMarkers = ['o','^','s','*','D']
###
###  (tupNames, tups, axesRanges) = reorderTups(subs, ['figure', 'subplot', 'lines', 'xaxis', 'yaxis', 'error'])
###  haveError = axesRanges[5][1] > 0
###
###  if "subplot" in subs:
###    subplotRowCol = procSubplot(tupNames, tups, axesRanges, subs)
###    # figure out some subplot stuff
###
###  # add a dummy tuple to the beginning
###  tups.insert(0, 0)
###
###  # no need for an iterator now, just go through the list forward
###  for i,t in enumerate(tups):
###    first = i == 0
###    last = i == len(tups) - 1
###    if not first:
###      constList = setConstList(t, axesRanges)
###    if not last:
###      nextConstList = setConstList(tups[i+1], axesRanges)
###
###    if last or first:
###      doneFigure = True
###      doneSubplot = True
###      doneLine = True
###    else:
###      doneFigure = constList[0] != nextConstList[0]
###      doneSubplot = doneFigure or constList[1] != nextConstList[1]
###      doneLine = doneSubplot or constList[2] != nextConstList[2]
###
###    if not first:
###      if haveError:
###        xVal = t[-3]
###        yVal = t[-2]
###        eVal = t[-1]
###        elist.append(eVal)
###      else:
###        xVal = t[-2]
###        yVal = t[-1]
###      xlist.append(xVal)
###      ylist.append(yVal)
###
###      substringDict = {}
###      for j, tn in enumerate(tupNames):
###        substringDict[tn] = str(t[j])
###
###    ############################
###    #                          #
###    # finish up previous plot  #
###    #                          #
###    ############################
###
###    if doneLine and not first:
###      # plot
###      labelStr = ""
###      for j, val in enumerate(constList[2]):
###        labelStr += str(val)
###        if j != len(constList[2]) - 1:
###          labelStr += " "
###        
###      if 'useMarkers' in subs and subs['useMarkers']:
###        lineMarker = lineMarkers[lineCount % len(lineTypes)]
###      else:
###        lineMarker = 'None'
###
###      if 'useLineStyle' in subs and subs['useLineStyle']:
###        lineStyle = lineTypes[lineCount % len(lineTypes)] 
###      else:
###        lineStyle = 'None'
###      lineColor = lineColors[lineCount % len(lineColors)]
###
###      plotFn = ax.plot
###      if 'log' in subs:
###        if 'x' in subs['log'] and 'y' in subs['log']:
###          plotFn = ax.loglog
###        elif 'x' in subs['log']:
###          plotFn = ax.semilogx
###        elif 'y' in subs['log']:
###          plotFn = ax.semilogy
###
###      plotFn(xlist, ylist, label=labelStr, linestyle=lineStyle, color=lineColor, marker=lineMarker)
###      if haveError:
###        ax.errorbar(xlist,ylist,yerr=elist,ecolor=lineColor,fmt=None)
###      lineCount += 1
###
###    if doneSubplot and not first:
###      # labels and legend
###      legendTitle = None
###      # if XLabelOnLast only plot on last subplot
###      if 'XLabelOnLast' in subs and subs['XLabelOnLast'] and doneFigure:
###        if "xaxis" in subs["labels"]:
###          ax.set_xlabel(subs['labels']['xaxis'] % substringDict)
###      if "yaxis" in subs["labels"]:
###        ax.set_ylabel(subs['labels']['yaxis'] % substringDict)
###      # only do a subplot label if more than 1 subplot
###      if ('AlwaysSubplotLabel' in subs and subs['AlwaysSubplotLabel']) or ("subplot" in subs and max(subplotRowCol[constList[0]])) > 1:
###        if "subplot" in subs["labels"]:
###          ax.set_title(subs['labels']['subplot'] % substringDict)
###      if "lines" in subs["labels"]:
###        legendTitle = subs['labels']['lines'] % substringDict
###
###      # legend
###      if axesRanges[2][1] > 0 and lineCount > 1: # have lines
###        legendLoc = None
###        if 'legendLoc' in subs:
###          legendLoc = subs['legendLoc']
###        lg = ax.legend(title=legendTitle, loc=legendLoc)
###        lg.draw_frame(False)
###
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
###
###    if doneFigure and not first:
###      # figure title
###      extraArtists = []
###      if "figure" in subs["labels"]:
###        extraArtists.append(fig.suptitle(subs['labels']['figure'] % substringDict))
###
###      # save figure
###      # first create a name
###      if "figName" in subs:
###        figName = subs['figName']
###      else:
###        figName = ""
###        # j starts at axesRanges for figure
###        for j, val in enumerate(t[axesRanges[0][0]:axesRanges[0][0] + axesRanges[0][1]], axesRanges[0][0]):
###          figName += "%s_%s" % (tupNames[j], str(val))
###          if j != axesRanges[0][0] + axesRanges[0][1] - 1:
###            figName += "__"
###        if figName == "":
###          figName = "plot"
###      fig.savefig(subs['plotDir'] + "/" + figName + ".pdf", format="pdf", transparent=True, bbox_inches="tight", bbox_extra_artists=extraArtists)
###
###      # reset params
###      matplotlib.rc_file_defaults()
###
###    #############################
###    #                           #
###    #    now create new things  #
###    #                           #
###    #############################
###
###    if doneFigure and not last:
###      # apply params
###      if 'Params' in subs:
###        paramsKey= ShoreDataPicker.getFields(tupNames, tups[i+1], subs['ParamsKey'])
###        d = subs['Params'][paramsKey]
###        for k,v in d.items():
###          matplotlib.rcParams[k] = v
###
###      fig = plt.figure(figureCount)
###      figureCount += 1
###      subplotCount = 1
###
###    if doneSubplot and not last:
###      if 'subplot' in subs:
###        ax = fig.add_subplot(subplotRowCol[nextConstList[0]][0], subplotRowCol[nextConstList[0]][1], subplotCount)
###        subplotCount += 1
###      else:
###        ax = fig.add_subplot(1,1,1)
###      lineCount = 0
###
###      # set some defaults
###      x_ax = ax.get_xaxis()
###      x_ax.tick_bottom()
###      y_ax = ax.get_yaxis()
###      y_ax.tick_left()
###      ax.spines['top'].set_color('none')
###      ax.spines['right'].set_color('none')
###    
###    if doneLine and not last:
###      # start the new line
###      xlist = []
###      ylist = []
###      if haveError:
###        elist = []
###
###  return figureCount

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
#def plotPie(subs):
#  pass
#
#def plotBar(subs, figureCount = 1):
#  lineColors = ["b", "g", "r"]
#
#  (tupNames, tups, axesRanges) = reorderTups(subs, ['figure', 'subplot', 'lines', 'xaxis', 'yaxis', 'error'])
#  haveError = axesRanges[5][1] > 0
#
#  if "subplot" in subs:
#    subplotRowCol = procSubplot(tupNames, tups, axesRanges, subs)
#
#  # add a dummy tuple to the beginning
#  tups.insert(0, 0)
#
#  # no need for an iterator now, just go through the list forward
#  for i,t in enumerate(tups):
#    first = i == 0
#    last = i == len(tups) - 1
#    if not first:
#      constList = setConstList(t, axesRanges)
#    if not last:
#      nextConstList = setConstList(tups[i+1], axesRanges)
#
#    if last or first:
#      doneFigure = True
#      doneSubplot = True
#      doneLine = True
#    else:
#      doneFigure = constList[0] != nextConstList[0]
#      doneSubplot = doneFigure or constList[1] != nextConstList[1]
#      doneLine = doneSubplot or constList[2] != nextConstList[2]
#
#    if not first:
#      if haveError:
#        xVal = t[-3]
#        yVal = t[-2]
#        eVal = t[-1]
#        elist.append(eVal)
#      else:
#        xVal = t[-2]
#        yVal = t[-1]
#      xlist.append(xVal)
#      ylist.append(yVal)
#
#      substringDict = {}
#      for j, tn in enumerate(tupNames):
#        substringDict[tn] = str(t[j])
#
#    ############################
#    #                          #
#    # finish up previous plot  #
#    #                          #
#    ############################
#
#    if doneLine and not first:
#      # plot
#      labelStr = ""
#      for j, val in enumerate(constList[2]):
#        labelStr += str(val)
#        if j != len(constList[2]) - 1:
#          labelStr += " "
#        
#      lineColor = lineColors[lineCount % len(lineColors)]
#
#      plotFn = ax.bar
#      #if 'log' in subs:
#      #  if 'x' in subs['log'] and 'y' in subs['log']:
#      #    plotFn = ax.loglog
#      #  elif 'x' in subs['log']:
#      #    plotFn = ax.semilogx
#      #  elif 'y' in subs['log']:
#      #    plotFn = ax.semilogy
#
#      plotFn(xlist, ylist, label=labelStr, color=lineColor)
#      if haveError:
#        ax.errorbar(xlist,ylist,yerr=elist,ecolor=lineColor,fmt=None)
#      lineCount += 1
#
#    if doneSubplot and not first:
#      # labels and legend
#      legendTitle = None
#      # if XLabelOnLast only plot on last subplot
#      if 'XLabelOnLast' in subs and subs['XLabelOnLast'] and doneFigure:
#        if "xaxis" in subs["labels"]:
#          ax.set_xlabel(subs['labels']['xaxis'] % substringDict)
#      if "yaxis" in subs["labels"]:
#        ax.set_ylabel(subs['labels']['yaxis'] % substringDict)
#      # only do a subplot label if more than 1 subplot
#      if ('AlwaysSubplotLabel' in subs and subs['AlwaysSubplotLabel']) or ("subplot" in subs and max(subplotRowCol[constList[0]])) > 1:
#        if "subplot" in subs["labels"]:
#          ax.set_title(subs['labels']['subplot'] % substringDict)
#      if "lines" in subs["labels"]:
#        legendTitle = subs['labels']['lines'] % substringDict
#
#      # legend
#      if axesRanges[2][1] > 0 and lineCount > 1: # have lines
#        legendLoc = None
#        if 'legendLoc' in subs:
#          legendLoc = subs['legendLoc']
#        lg = ax.legend(title=legendTitle, loc=legendLoc)
#        lg.draw_frame(False)
#
#      # fix any axes limits
#      # if None given keep the old one
#      if 'xlim' in subs:
#        lim = list(ax.get_xlim())
#        for j in [0,1]:
#          if subs['xlim'][j] != None:
#            lim[j] = subs['xlim'][j]
#        ax.set_xlim(lim)
#      if 'ylim' in subs:
#        lim = list(ax.get_ylim())
#        for j in [0,1]:
#          if subs['ylim'][j] != None:
#            lim[j] = subs['ylim'][j]
#        ax.set_ylim(lim)
#
#    if doneFigure and not first:
#      # figure title
#      extraArtists = []
#      if "figure" in subs["labels"]:
#        extraArtists.append(fig.suptitle(subs['labels']['figure'] % substringDict))
#
#      # save figure
#      # first create a name
#      if "figName" in subs:
#        figName = subs['figName']
#      else:
#        figName = ""
#        # j starts at axesRanges for figure
#        for j, val in enumerate(t[axesRanges[0][0]:axesRanges[0][0] + axesRanges[0][1]], axesRanges[0][0]):
#          figName += "%s_%s" % (tupNames[j], str(val))
#          if j != axesRanges[0][0] + axesRanges[0][1] - 1:
#            figName += "__"
#        if figName == "":
#          figName = "plot"
#      fig.savefig(subs['plotDir'] + "/" + figName + ".pdf", format="pdf", transparent=True, bbox_inches="tight", bbox_extra_artists=extraArtists)
#
#      # reset params
#      matplotlib.rc_file_defaults()
#
#    #############################
#    #                           #
#    #    now create new things  #
#    #                           #
#    #############################
#
#    if doneFigure and not last:
#      # apply params
#      if 'Params' in subs:
#        paramsKey= ShoreDataPicker.getFields(tupNames, tups[i+1], subs['ParamsKey'])
#        d = subs['Params'][paramsKey]
#        for k,v in d.items():
#          matplotlib.rcParams[k] = v
#
#      fig = plt.figure(figureCount)
#      figureCount += 1
#      subplotCount = 1
#
#    if doneSubplot and not last:
#      if 'subplot' in subs:
#        ax = fig.add_subplot(subplotRowCol[nextConstList[0]][0], subplotRowCol[nextConstList[0]][1], subplotCount)
#        subplotCount += 1
#      else:
#        ax = fig.add_subplot(1,1,1)
#      lineCount = 0
#
#      # set some defaults
#      x_ax = ax.get_xaxis()
#      x_ax.tick_bottom()
#      y_ax = ax.get_yaxis()
#      y_ax.tick_left()
#      ax.spines['top'].set_color('none')
#      ax.spines['right'].set_color('none')
#    
#    if doneLine and not last:
#      # start the new line
#      xlist = []
#      ylist = []
#      if haveError:
#        elist = []
#
#  return figureCount
#
#def plotHist(subs, figureCount = 1):
#  lineColors = ["b", "g", "r"]
#
#  (tupNames, tups, axesRanges) = reorderTups(subs, ['figure', 'subplot', 'lines', 'xaxis', 'yaxis', 'error'])
#  haveError = axesRanges[5][1] > 0
#
#  if "subplot" in subs:
#    subplotRowCol = procSubplot(tupNames, tups, axesRanges, subs)
#
#  # add a dummy tuple to the beginning
#  tups.insert(0, 0)
#
#  # no need for an iterator now, just go through the list forward
#  for i,t in enumerate(tups):
#    first = i == 0
#    last = i == len(tups) - 1
#    if not first:
#      constList = setConstList(t, axesRanges)
#    if not last:
#      nextConstList = setConstList(tups[i+1], axesRanges)
#
#    if last or first:
#      doneFigure = True
#      doneSubplot = True
#      doneLine = True
#    else:
#      doneFigure = constList[0] != nextConstList[0]
#      doneSubplot = doneFigure or constList[1] != nextConstList[1]
#      doneLine = doneSubplot or constList[2] != nextConstList[2]
#
#    if not first:
#      if haveError:
#        xVal = t[-3]
#        yVal = t[-2]
#        eVal = t[-1]
#        elist.append(eVal)
#      else:
#        xVal = t[-1]
#      xlist.append(xVal)
#
#      substringDict = {}
#      for j, tn in enumerate(tupNames):
#        substringDict[tn] = str(t[j])
#
#    ############################
#    #                          #
#    # finish up previous plot  #
#    #                          #
#    ############################
#
#    if doneLine and not first:
#      # plot
#      labelStr = ""
#      for j, val in enumerate(constList[2]):
#        labelStr += str(val)
#        if j != len(constList[2]) - 1:
#          labelStr += " "
#        
#      lineColor = lineColors[lineCount % len(lineColors)]
#
#      plotFn = ax.hist
#      normed = "normed" in subs and subs['normed']
#      log = 'log' in subs
#      bins = 'bins' in subs
#      bins = int(subs["bins"]) if bins else 50
#      plotFn(xlist, label=labelStr, bins=bins, log=log, normed=normed)
#      if haveError:
#        ax.errorbar(xlist,ylist,yerr=elist,ecolor=lineColor,fmt=None)
#      lineCount += 1
#
#    if doneSubplot and not first:
#      # labels and legend
#      legendTitle = None
#      # if XLabelOnLast only plot on last subplot
#      if 'XLabelOnLast' in subs and subs['XLabelOnLast'] and doneFigure:
#        if "xaxis" in subs["labels"]:
#          ax.set_xlabel(subs['labels']['xaxis'] % substringDict)
#      if "yaxis" in subs["labels"]:
#        ax.set_ylabel(subs['labels']['yaxis'] % substringDict)
#      # only do a subplot label if more than 1 subplot
#      if ('AlwaysSubplotLabel' in subs and subs['AlwaysSubplotLabel']) or ("subplot" in subs and max(subplotRowCol[constList[0]])) > 1:
#        if "subplot" in subs["labels"]:
#          ax.set_title(subs['labels']['subplot'] % substringDict)
#      if "lines" in subs["labels"]:
#        legendTitle = subs['labels']['lines'] % substringDict
#
#      # legend
#      if axesRanges[2][1] > 0 and lineCount > 1: # have lines
#        legendLoc = None
#        if 'legendLoc' in subs:
#          legendLoc = subs['legendLoc']
#        lg = ax.legend(title=legendTitle, loc=legendLoc)
#        lg.draw_frame(False)
#
#      # fix any axes limits
#      # if None given keep the old one
#      if 'xlim' in subs:
#        lim = list(ax.get_xlim())
#        for j in [0,1]:
#          if subs['xlim'][j] != None:
#            lim[j] = subs['xlim'][j]
#        ax.set_xlim(lim)
#      if 'ylim' in subs:
#        lim = list(ax.get_ylim())
#        for j in [0,1]:
#          if subs['ylim'][j] != None:
#            lim[j] = subs['ylim'][j]
#        ax.set_ylim(lim)
#
#    if doneFigure and not first:
#      # figure title
#      extraArtists = []
#      if "figure" in subs["labels"]:
#        extraArtists.append(fig.suptitle(subs['labels']['figure'] % substringDict))
#
#      # save figure
#      # first create a name
#      if "figName" in subs:
#        figName = subs['figName']
#      else:
#        figName = ""
#        # j starts at axesRanges for figure
#        for j, val in enumerate(t[axesRanges[0][0]:axesRanges[0][0] + axesRanges[0][1]], axesRanges[0][0]):
#          figName += "%s_%s" % (tupNames[j], str(val))
#          if j != axesRanges[0][0] + axesRanges[0][1] - 1:
#            figName += "__"
#        if figName == "":
#          figName = "plot"
#      fig.savefig(subs['plotDir'] + "/" + figName + ".pdf", format="pdf", transparent=True, bbox_inches="tight", bbox_extra_artists=extraArtists)
#
#      # reset params
#      matplotlib.rc_file_defaults()
#
#    #############################
#    #                           #
#    #    now create new things  #
#    #                           #
#    #############################
#
#    if doneFigure and not last:
#      # apply params
#      if 'Params' in subs:
#        paramsKey= ShoreDataPicker.getFields(tupNames, tups[i+1], subs['ParamsKey'])
#        d = subs['Params'][paramsKey]
#        for k,v in d.items():
#          matplotlib.rcParams[k] = v
#
#      fig = plt.figure(figureCount)
#      figureCount += 1
#      subplotCount = 1
#
#    if doneSubplot and not last:
#      if 'subplot' in subs:
#        ax = fig.add_subplot(subplotRowCol[nextConstList[0]][0], subplotRowCol[nextConstList[0]][1], subplotCount)
#        subplotCount += 1
#      else:
#        ax = fig.add_subplot(1,1,1)
#      lineCount = 0
#
#      # set some defaults
#      x_ax = ax.get_xaxis()
#      x_ax.tick_bottom()
#      y_ax = ax.get_yaxis()
#      y_ax.tick_left()
#      ax.spines['top'].set_color('none')
#      ax.spines['right'].set_color('none')
#    
#    if doneLine and not last:
#      # start the new line
#      xlist = []
#      ylist = []
#      if haveError:
#        elist = []
#
#  return figureCount

# reorder and sort the tuples based off of the axes parameters
# return (tupNames, tups, axesRanges)
def reorderTups(subs, axesTypes):
  # change the tuple order to (figures, subplots, lines, x, y)
  #   this way the (x,y) at the end is already set
  #   we will sort by each in order since sort is stable.  Reverse when necessary
  tups = subs['tups']
  tupNames = subs['tupNames']
  newTupNames = []
  axes = subs['axes']
  axesRanges = []
  axesRangeCounter = 0
  for axis in axesTypes:
    if axis == 'subplot' and 'subplotOrder' in subs:
      subplotOrder = subs['subplotOrder']
      for item in subplotOrder:
        # make sure this was listed as subplot in axes
        if item not in axes or axes[item] != 'subplot':
          print "problem with subplot item: %s" % str(item)
          sys.exit(1)
        newTupNames.append(item)
    # find all fields with this axis type
    numInAxes = 0
    for field, dimension in axes.items():
      if dimension == axis and field not in newTupNames: # the not in is for subplotOrders
        numInAxes += 1
        newTupNames.append(field)
    axesRanges.append( (axesRangeCounter, numInAxes) )
    axesRangeCounter += numInAxes

  newTups = []
  for t in tups:
    newTups.append(ShoreDataPicker.getFields(tupNames, t, newTupNames))
  tupNames = tuple(newTupNames)
  tups = newTups

  # now determine if any of these need to be reversed
  reverseList = [False] * len(tupNames)
  if 'reverse' in subs:
    for item in subs['reverse']:
      reverseList[tupNames.index(item)] = True

  # sort each field at a time in reverse order
  # remember that python sort is stable
  # we end up sorted by figures, then by lines, x, and y
  for i in range(len(tupNames)-1,-1,-1):
    tups.sort(reverse=reverseList[i])

  return (tupNames, tups, axesRanges)


def setConstList(t, clRanges):
  cl = []
  for (start, num) in clRanges:
    cl.append( tuple(t[start:(start+num)]) )
  return cl

def procSubplot(tupNames, tups, axesRanges, subs):
  # figure out some subplot stuff

  # can't both be None
  spRow = subs['subplot'][0]
  spCol = subs['subplot'][1]
  assert spRow or spCol

  # create a dict of {(figure vals) : set(subplot vals)} to get a count of distinct values
  subplotCounters = collections.defaultdict(set)
  # sets for each dimension of the subplot
  subplotCountersRow = collections.defaultdict(set)
  subplotCountersCol = collections.defaultdict(set)
  for t in tups:
    constList = setConstList(t, axesRanges)
    figureTup = constList[0]
    subplotTup = constList[1]
    subplotCounters[figureTup].add(subplotTup)
    if spRow:
      subplotCountersRow[figureTup].add(ShoreDataPicker.getFields(tupNames, t, (spRow,))[0])
    if spCol:
      subplotCountersCol[figureTup].add(ShoreDataPicker.getFields(tupNames, t, (spCol,))[0])

  # subplotRowCol is {(figure vals) : (Row, Col)} subplot width and height
  subplotRowCol = {}
  for figureTup in subplotCounters.keys():
    num = len(subplotCounters[figureTup])
    if spRow:
      numRow = len(subplotCountersRow[figureTup])
    if spCol:
      numCol = len(subplotCountersCol[figureTup])
    if not spRow:
      numRow = int(math.ceil(float(num) / float(numCol)))
    if not spCol:
      numCol = int(math.ceil(float(num) / float(numRow)))

    subplotRowCol[figureTup] = (numRow, numCol)
  return subplotRowCol
