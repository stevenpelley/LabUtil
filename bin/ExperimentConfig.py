# ExperimentConfig
#
# define a set of parameters and values for an experiment
# easily iterate over and use the set of possible value combinations
# keep in mind that parameter values can be more than scalars.  Consider
# using lists, maps, or even functions as appropriate
#
# it is up to the user to make sure that all combinations are unique
# parameter values may not be hashable (and cannot be put in a set()), so
# we do not check for uniqueness
#
# input is defined by a list of parameters
# each parameter is a tuple of:
#   the parameter's name (string)
#   a tuple of parameters this might depend on (tuple of strings)
#   a function:
#     taking a map from the dependent parameters to their current values.
#     returning a list representing the values of this parameter
#     for the values of input dependent parameters.
#
###########################
# example: length in [1,2,3], height = [length,length+1] when length odd,
#            [2*length, 2*length + 1] when length even
#   (length, height) sets: (1,1), (1,2), (2,4), (2,5), (3,3), (3,4)
#
# EXAMPLE CONFIG:
#############
# parameters = []
# def Fn(vals):
#   return [1,2,3]
# parameters.append( ("length", (), Fn) )
#
# def Fn(vals):
#   length = vals["length"]
#   return [length, length+1] if length % 2 == 0 else [2*length, 2*length+1]
# parameters.append( ("height", ("length",), Fn) )
###########################

import types
import inspect
import collections
import sys

# once the ExperimentConfig object is created it is immutable
# create an ExperimentConfigIter to iterate over the config
class ExperimentConfig:
  # internal
  # need to make sure no cycles exist and determine a single order for params
  # determine the size of the config (number of combinations)
  # determine which parameters are sufficient to describe the experiment:
  #   if a parameter ever returns a list of size > 1 it describes the experiment
  #   otherwise it always matches another parameter 1:1
  def __init__(self, params):
    self.params = params
    self.paramToFn = self.initFns()
    self.assertInputParams()
    self.order = self.findOrderOrDie()
    self.describingParams = self.findDescribingParamsOrDie()
    self.setOriginalDisplayOrder()

  # return a map of param names to their functions
  def initFns(self):
    paramToFn = {}
    for param in self.params:
      paramToFn[param[0]] = param[2]
    return paramToFn

  # check that the input parameters are of the correct form
  # list of (name, tuple of dependencies, function)
  def assertInputParams(self):
    assert type(self.params) == list, repr(self.params)
    for i, param in enumerate(self.params):
      assert type(param) == tuple, "not tuple -- params[%d] = %s; type %s" % (i, repr(param), type(param))
      assert len(param) == 3, "not length 3 -- params[%d] = %s; length %d" % (i, repr(param), len(param))
      assert type(param[0]) == str, "not str -- params[%d] = %s; param[0] = %s; type = %s" % (i, repr(param), repr(param[0]), type(param[0]))
      assert type(param[1]) == tuple, "not tuple -- params[%d] = %s; param[1] = %s; type = %s" % (i, repr(param), repr(param[1]), type(param[1]))
      for j, dep in enumerate(param[1]):
        assert type(dep) == str, "not str -- params[%d] = %s; param[1] = %s; deps[%d] = %s; type = %s" % (i, repr(param), repr(param[1]), repr(dep), typeof(dep))
      assert inspect.isfunction(param[2]), "not function -- params[%d] = %s; param[2] = %s; type = %s" % (i, repr(param), repr(param[2]), type(param[2]))
      args = inspect.getargspec(param[2]).args
      assert len(args) == 1, "not length 1 -- params[%d] = %s; args = %s; length %d" % (i, repr(param), repr(args), len(args))

    # now make sure that all param dependencies actually exist
    paramList = map(lambda x: x[0], self.params)
    for param in self.params:
      for dep in param[1]:
        assert dep in paramList, "dependence '%s' from param '%s' does not exist" % (dep, param[0])

  # assert that there are no cycles in dependencies
  # return a list of param names in a usable order
  # performs a topological sort, and if it can't we fail
  def findOrderOrDie(self):
    # using Cormen/Tarjan algorithm
    # define the graph of dependencies
    # (if param A depends on param B there is an edge from A to B)
    # visit nodes that have no outgoing edges
    # visit(node, visitlist, outputlist, seen):
    #   fail if node in seen
    #   return if node has already been visited
    #   add node to visitlist
    #   for each node m pointing to this node:
    #     visit(m, visitlist, outputlist, seen + [m])
    #   add this node to the outputlist
    #
    # reverse list so we get nodes with no dependencies first

    def buildGraph(params):
      nameToNode = {}
      nodeToName = {}
      count = 0
      for param in params:
        nameToNode[param[0]] = count
        nodeToName[count] = param[0]
        count += 1
      # an edge implies a dependence - A points to B, A depends on B
      outgoingEdges = collections.defaultdict(list) # dict[i] -> [a,b,c] means i points to a,b,c
      incomingEdges = collections.defaultdict(list) # dict[i] -> [a,b,c] means a,b,c point to i
      for param in params:
        node = nameToNode[param[0]]
        if node not in outgoingEdges:
          outgoingEdges[node] = []
        if node not in incomingEdges:
          incomingEdges[node] = []
        for dep in param[1]:
          dependOn = nameToNode[dep]
          outgoingEdges[node].append(dependOn)
          incomingEdges[dependOn].append(node)
      return (nameToNode, nodeToName, outgoingEdges, incomingEdges)

    def visit(node, visitList, outputList, seen, incomingEdges):
      assert node not in seen, "cycle involving %s in %s" % (nodeToName[node], repr(seen))
      if node in visitList:
        return
      visitList.append(node)
      for dependsOnMe in incomingEdges[node]:
        visit(dependsOnMe, visitList, outputList, seen + [node], incomingEdges)
      outputList.append(node)

    (nameToNode, nodeToName, outgoingEdges, incomingEdges) = buildGraph(self.params)
    visitList = []
    outputList = []
    independentCount = 0
    for node, outgoing in outgoingEdges.items():
      if len(outgoing) == 0:
        independentCount += 1
        visit(node, visitList, outputList, [], incomingEdges)

    outputList.reverse()
    outputList = map(lambda node: nodeToName[node], outputList)
    assert independentCount > 0, "no independent params"
    if len(outputList) != len(self.params):
      assert len(self.params) > len(outputList), "no clue how we ended up with more than params"
      # get list of nodes that failed to appear
      outputSet = set(outputList)
      paramsSet = set(map(lambda x: x[0], self.params))
      missingSet = paramsSet - outputSet
      assert False, "did not use all params in DAG.\nCyclic subgraph may not point to independent params.\nLook at the following nodes for a cycle:\n%s" % str(sorted(missingSet))

    return outputList

  # iterate over the config
  # and determine which params ever return more than 1 element
  # these make the set of params and values that describe each run config
  # dies if some function does not return a list or dependence can't be matched
  def findDescribingParamsOrDie(self):
    paramsDescribe = {}
    for param in self.order:
      paramsDescribe[param] = False
    it = self.iter()
    try:
      while it.next():
        for param in self.order:
          if len(self.valList(param, it.allVals())) > 1:
            paramsDescribe[param] = True
    except:
      print "DIED IN FIRST ITERATOR READ"
      print "CHECK THAT ALL FUNCTIONS RETURN LISTS AND ALL DEPENDENCIES ARE SATISFIED"
      raise

    return map(lambda x: x[0], filter(lambda x: x[1], paramsDescribe.items()))

  def iter(self):
    return ExperimentConfigIter(self)

  def getDescribingParams(self):
    #return self.describingParams
    return self.displayOrder

  # given the current indices return the valList for param
  def valList(self, param, vals):
    return self.paramToFn[param](vals)

  def hasKey(self, param):
    return param in self.order

  # experiment labels will use this order for tags
  #  should match elements of describing params
  def setDisplayOrder(self, newOrder):
    self.displayOrder = filter(lambda x: x in self.describingParams, newOrder)
    
  # use the order params are defined to display them
  def setOriginalDisplayOrder(self):
    self.setDisplayOrder(map(lambda x: x[0], self.params))

# iterator object over a config
#
# create with ExperimentConfig.iter()
# get values with iterator.val("name")
# move iterator forward with: hasNext iterator.next()
# must call next before starting
# ex:
#   iter = config.iter()
#   while iter.next():
#     print iter.val("length")

class ExperimentConfigIter:
  # internal:
  # keep map of the current values for each param
  # keep map of indices for the value for each param
  # to iterate add 1 to last param, follow overflow
  # get new param value list by call to Config.paramList(name, vals)
  # determine when we are done when all indices are 0

  def __init__(self, config):
    self.config = config
    self.currentVals = {}
    self.currentIndices = {}
    self.started = False # distinguish between new and done

  def next(self):
    if not self.started:
      self.started = True
      self.initIndices()
      # do not increment
    else:
      self.inc()
      if self.done():
        return False
    self.update()
    return True

  # initialize currentIndices to start iteration
  def initIndices(self):
    self.currentIndices = {}
    for param in self.config.order:
      self.currentIndices[param] = 0

  # add 1 to the last index and follow overflow
  # currentIndices set to the next iteration when done
  def inc(self):
    # start by incrementing the last one
    paramNum = len(self.config.order) - 1
    while paramNum >= 0:
      param = self.config.order[paramNum]
      currentParamLen = len(self.config.valList(param, self.allVals()))
      incIDX = self.currentIndices[param]+1
      if incIDX < currentParamLen: # no overflow
        self.currentIndices[param] = incIDX
        break
      # else - overflow.  Reset this param index and go to next
      # no need to update val because the next param whos index we update
      # cannot have depended on this one
      self.currentIndices[param] = 0
      paramNum -= 1

  # given the current Indices
  # update currentVals
  # we update every param's value even though this isn't strictly necessary
  def update(self):
    for param in self.config.order:
      self.currentVals[param] = self.config.valList(param, self.allVals())[self.currentIndices[param]]

  # return the val for a particular param
  def val(self, param):
    assert self.started
    return self.currentVals[param]

  # return a map of all params to their current values
  def allVals(self):
    assert self.started
    return self.currentVals

  # return true if iterator is done
  def done(self):
    if not self.started:
      return False
    for param in self.config.order:
      if self.currentIndices[param] != 0:
        return False
    return True

  # get a label containing the values of the describingParams
  def experimentLabel(self):
    label = ""
    for i, param in enumerate(self.config.getDescribingParams()):
      label += "%s_%s" % (param, str(self.val(param)))
      if i < len(self.config.getDescribingParams())-1:
        label += "__"
    return label

  def hasKey(self, param):
    return self.config.hasKey(param)

def test1():
  params = []
  def Fn1(vals):
    return [0]
  def Fn2(vals):
    return [0,1]
  params.append(("p0", (), Fn2,))
  params.append(("p1", ("p0",), Fn2,))
  params.append(("p2", ("p1",), Fn1,))
  params.append(("p3", (), Fn1,))
  params.append(("p4", ("p2", "p3",), Fn2,))
  config = ExperimentConfig(params)
  print "order: " + str(config.order)
  print "describing params: " + str(config.getDescribingParams())
  print "running through iterator:"
  it = config.iter()
  while it.next():
    # print from iterator internal map
    print str(it.allVals())
    s = ""
    for i, param in enumerate(config.order):
      s += "%s = %s" % (param, str(it.val(param)))
      if i < len(config.order)-1:
        s += ", "
    print s
    print

def createConfig(fileName):
  subLocals = {}
  execfile(fileName, subLocals)
  params = subLocals["params"]
  config = ExperimentConfig(params)
  config.setOriginalDisplayOrder()
  it = config.iter()
  count = 0
  while it.next():
    count += 1
    print it.experimentLabel()
  print "order: " + str(config.order)
  print "describing params: " + str(config.getDescribingParams())
  print "total count: %d" % count

# test cases
if __name__ == "__main__":
  if len(sys.argv) > 1:
    createConfig(sys.argv[1])
  else:
    test1()

