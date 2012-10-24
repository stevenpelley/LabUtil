#!/usr/bin/python
#
# create a bar plot with 1 figure, 2 subplots, 3 groups, 4 bars, and 3 stacks per bar

# subplots can be clones
# each group represents a base
# each bar represents a multiplier
# each stack is an exponent
# so each stack is (multiplier * base**exponent)

import random

columns = ("Clone", "Base", "Multiplier", "Exponent", "Height",)
rows = []

clones = [1.0] # figures
#clones = [1.0,2.0] # figures
#bases = [1.0] # groups
bases = [1.0, 2.0, 3.0] # groups
exps = [1.0,2.0,3.0] # stacks
#exps = [1.0] # stacks
for clone in clones:
  for base in bases:
    for multiplier in [1.0, 2.0, 3.0,4.0]:
      for exp in exps:
        val = multiplier * (base**exp)
        rows.append( (clone, base, multiplier,exp,val,))

import sys
labUtilDir = '/home/spelley/work/LabUtil/bin'
#labUtilDir = '/home/sleimanf/tools/plot/LabUtil/bin'
sys.path.append(labUtilDir)
import Plot
import PlotFns

plotVars = {}
plotVars['Columns'] = columns
plotVars['Rows'] = rows

# define the role of each column
plotVars['Layers'] = ["Figure", "Subplot", "Group", "Bar", "Stack"]
plotVars['LayerGroups'] = {
  'Figure'  : [],
  'Subplot' : ["Clone"],
  'Group'   : ["Base"],
  'Bar'   : ["Multiplier"],
  'Stack'   : ["Exponent", "Height"],
}

# labels can only replace with column values
# for anything more complex must override
plotVars['Labels']= {
  'Figure'  : 'figure',
  'Subplot' : 'Clone: %(Clone)s',
  'Group'   : 'Base: %(Base).1f',
  'Bar'     : 'Bar: %(Multiplier).1f',
  'Stack'   : 'Exp: %(Exponent).1f',
  'YAxis'   : "Count?",
}

# Name, Number, Color, Texture
# Name = label under each bar
# Number = numbers and ticks on x-axis
# color, texture = each bar gets a color or texture with legend
plotVars['BarLabel'] = 'Name'

# percent of whitespace between groups
plotVars['GroupWhiteSpace'] = .2

plotVars['LegendLocation'] = 'upper left'

plotVars['OutputDir'] = 'Bar'
plotVars['DefaultFns'] = 'Bar'
#plotVars['XLabelOnLast'] = True

plotVars['TraceFunctionCalls'] = True

Plot.plot(plotVars)
