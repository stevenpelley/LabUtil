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
for clone in [1.0,2.0]:
  for base in [1.0,2.0,3.0]:
    for multiplier in [1.0, 2.0, 3.0,4.0]:
      for exp in [1.0,2.0,3.0]:
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
  'Group'   : 'Base',
  'Bar'     : 'Bar',
  'Stacks'  : 'Stack',
}

plotVars['OutputDir'] = 'Bar'
plotVars['DefaultFns'] = 'Bar'
#plotVars['XLabelOnLast'] = True

plotVars['TraceFunctionCalls'] = True

Plot.plot(plotVars)
