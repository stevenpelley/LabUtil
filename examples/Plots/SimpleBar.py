#!/usr/bin/python
#
# create a simple line plot (with multiple figures, subplots, and lines)

# first generate data
# 3 lines per subplot, 2 subplots per figure, 2 figures
# plotting y = mx^e + b
# each line has m in {1,2,3}
# each subplot has e in {1,2}
# each figure has b in {0, 5}
# x goes from 0 to 5 by 1
import random

alphabet = 'abcdefghijklmnopqrstuvwxyz'

columns = ("Offset", "Exponent", "Slope", "XValue", "YValue",)
rows = []
for offset in [0.0,5.0]:
  for exponent in [1.0, 2.0]:
    for slope in [1.0, 2.0, 3.0]:
      for i,x in enumerate(map(lambda val: val/2.0,range(0,12))):
        y = slope * (float(x)**exponent) + offset
        rows.append( (offset, exponent, slope, alphabet[i], y,) )

# randomize the column and row order (but keep consistent)
newColOrder = list(columns)
random.shuffle(newColOrder)
# reorder all rows to be same column order
newRows = []
for r in rows:
  rList = []
  for c in newColOrder:
    oldIDX = columns.index(c)
    rList.append(r[oldIDX])
  newRow = tuple(rList)
  newRows.append(newRow)

columns = newColOrder
rows = newRows

# now shuffle the row orders
random.shuffle(rows)

import sys
labUtilDir = '/home/spelley/work/LabUtil/bin'
#labUtilDir = '/home/sleimanf/tools/plot/LabUtil-groups/bin'
sys.path.append(labUtilDir)
import Plot
import PlotFnsBar

plotVars = {}
plotVars['Columns'] = columns
plotVars['Rows'] = rows

# define the role of each column
plotVars['Layers'] = ["Figure", "Subplot", "Series", "Point"]
plotVars['LayerGroups'] = {
  'Figure'  : ["Offset"],
  'Subplot' : ["Exponent"],
  'Series'   : ["Slope"],
  'Point'   : ["XValue", "YValue"],
}

# labels can only replace with column values
# for anything more complex must override
plotVars['Labels']= {
  'Figure'  : 'figure with offset: %(Offset)f',
  'Subplot' : 'subplot with exponent: %(Exponent)s',
  'Series'   : 'Slope',
  'XAxis'   : 'this is x',
  'YAxis'   : 'this is y',
}

plotVars['OutputDir'] = 'SimpleBar'
#plotVars['DefaultFns'] = 'BarStacked'
plotVars['DefaultFns'] = 'BarInterleaved'
plotVars['BarInterleaveOffset'] = 0.333
plotVars['BarWidth'] = 0.333
plotVars['XLabelOnLast'] = True

plotVars['TraceFunctionCalls'] = True

plotVars['LegendLocation'] = 'upper left'

Plot.plot(plotVars)
