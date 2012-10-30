
# just plot it the old fashion way
import matplotlib
import matplotlib.pyplot as plt
import sys
fig = plt.figure(1)
ax = fig.add_subplot(111)

ax.bar([1,2,3], [.5,2,3], width=0.5, bottom=None, log=True)
ax.bar([1,2,3], [100, 1000, 10000], width=0.5, bottom=[.5,2,3], log=True)
#ax.set_ylim(.1, 20000)
#plt.show()

extraArtists=[]
fig.savefig('plot_by_hand.pdf', transparent=True, bbox_inches="tight", bbox_extra_artists=extraArtists)
#sys.exit(0)

# now plot with our infrastructure


cols = ('bar', 'source', 'height',)
rows = [
  (1,'bottom', 10,),
  (1,'top', 1000,),
  (2,'bottom', 1,),
  (2,'top', 10000,),
]

sourceVals = ['bottom', 'top']
def sortSource(x,y):
  assert x in sourceVals
  assert y in sourceVals
  xIDX = sourceVals.index(x)
  yIDX = sourceVals.index(y)
  if xIDX < yIDX:
    return -1
  elif xIDX == yIDX:
    return 0
  else:
    return 1

def afterSubplot(plotVars):
  plotVars['BarLog'] = True
  plotVars['BarLabel'] = True
  #plotVars['YLim'] = (.01, None)
  import PlotFns
  PlotFns.PlotFnAfterBarSubplot(plotVars)

labUtilDir = '/home/spelley/work/LabUtil/bin'
#labUtilDir = '/home/sleimanf/tools/plot/LabUtil/bin'
sys.path.append(labUtilDir)
import Plot
import PlotFns

plotVars = {}
plotVars['Columns'] = cols
plotVars['Rows'] = rows

# define the role of each column
plotVars['Layers'] = ["Figure", "Subplot", "Group", "Bar", "Stack"]
plotVars['LayerGroups'] = {
  'Figure'  : [],
  'Subplot' : [],
  'Group'   : [],
  'Bar'   : ["bar"],
  'Stack'   : ["source", "height"],
}

# labels can only replace with column values
# for anything more complex must override
plotVars['Labels']= {
  'Figure'  : 'figure',
  #'Subplot' : 'Clone: %(Clone)s',
  'Group'   : 'Group',
  'Bar'     : 'Bar: %(bar)d',
  'Stack'   : 'Exp: %(source)s',
  'YAxis'   : "Count",
}

#plotVars['LegendLocation'] = 'upper right'

plotVars['OutputDir'] = 'BarLog'
plotVars['DefaultFns'] = 'Bar'
#plotVars['XLabelOnLast'] = True

plotVars['TraceFunctionCalls'] = True

plotVars['SortColumns'] = {
  'Source' : sortSource,
}

plotVars['LayerFns'] = {
  'Subplot' : (None, afterSubplot),
}

Plot.plot(plotVars)
