#!/usr/bin/python
#
# single figure, single plot
# 2 y-axes
# left axis contains 3 lines going up
# right axis contains 3 lines going down
import random

columns = ("LeftAxis", "Slope", "XValue", "YValue",)
rows = []
for leftaxis in [True, False]:
  for slope in [1.0, 2.0, 3.0]:
    for x in map(float,range(0,6)):
      if leftaxis:
        y = 2.0 * slope * float(x)
      else:
        y = -1.0 * slope * float(x) + 15.0
      rows.append( (leftaxis, slope, x, y,) )

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
sys.path.append(labUtilDir)
import Plot

plotVars = {}
plotVars['Columns'] = columns
plotVars['Rows'] = rows

# define the role of each column
plotVars['Layers'] = ["Figure", "Subplot", "MultiAxis", "Line", "Point"]
plotVars['LayerGroups'] = {
  'Figure' : [],
  'Subplot' : [],
  'Line'   : ["Slope"],
  'MultiAxis' : ["LeftAxis"],
  'Point'   : ["XValue", "YValue"],
}

# labels can only replace with column values
# for anything more complex must override
plotVars['Labels']= {
  'Figure'  : 'figure without a value',
  'Subplot' : 'subplot without a value',
  'Line'   : 'Slope:',
  'XAxis'   : 'this is x',
  'YAxis'   : 'this is y',
}

plotVars['OutputDir'] = 'MultiAxis'
plotVars['DefaultFns'] = 'Line'
plotVars['XLabelOnLast'] = True

def newBeforeSubplot(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+subplot new'
  Plot.PlotFnBeforeSubplot(plotVars)
  plotVars['LeftAxis'] = plotVars['Figure'].add_subplot(1,1,1)
  plotVars['RightAxis'] = plotVars['LeftAxis'].twinx()

  # turn the right axis back on
  plotVars['LeftAxis'].spines['right'].set_color('black')

def beforeMultiAxis(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '+multiaxis'
  if plotVars['ColumnToValue']['LeftAxis']:
    plotVars['Axes'] = plotVars['LeftAxis']
  else:
    plotVars['Axes'] = plotVars['RightAxis']

def afterMultiAxis(plotVars):
  if plotVars['TraceFunctionCalls']:
    print '-multiaxis'

plotVars['LayerFns'] = {
  'MultiAxis' : (beforeMultiAxis, afterMultiAxis),
  'Subplot' : (newBeforeSubplot, None),
}

plotVars['TraceFunctionCalls'] = True

Plot.plot(plotVars)
