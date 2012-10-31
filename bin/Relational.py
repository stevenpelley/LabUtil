#!/usr/bin/python
#
# Relational algebra operations operations
# cols: a tuple of strings representing the columns of this relation
# rows: a list of tuples, where each tuple is the values corresponding to cols

class Relation:
  def __init__(self, arg=None):
    if arg == None:
      self.rows = []
      self.cols = ()
    elif isinstance(arg, Relation):
      self.cols = tuple(arg.cols)
      self.rows = list(arg.rows)
    elif (
           isinstance(arg, tuple) and
           len(arg) == 2 and
           isinstance(arg[0], tuple) and
           isinstance(arg[1], list)
         ): # input is columns and rows to create relation
      self.cols = tuple(arg[0])
      for col in self.cols:
        assert isinstance(col, str)
      l = len(self.cols)
      self.rows = list(arg[1])
      for row in self.rows:
        assert len(row) == l
    else:
      assert False, "Relation input invalid: {!r}".format(arg)
    
  # helper
  # return a tuple of the given fields
  def projectRow(cols, row, projectFields):
    assert isinstance(projectFields, tuple), "Projection Fields must be a tuple"
    newRow = []
    for field in projectFields:
      assert f in cols, "Projection Field {!r} not in cols {!r}".format(f, cols)
      newRow.append(row[cols.index(f)])
    return tuple(newRow)

  # projection on relation
  # modifies the relation!
  def project(self, projectFields):
    newRows = []
    for row in self.rows:
      newRows.append(projectRow(self.cols, row, projectFields)
    self.cols = projectFields
    self.rows = newRows

  # perform a selection (essentially a filter)
  # selectFn takes in (row, tuple of vals) returns True to keep row, False to pass
  # selectFnColInputs determines which column values are the inputs to selectFn
  # modifies the relation!
  def select(self, selectFn, selectFnColInputs):
    innerSelectFn = lambda row: selectFn(row, projectRow(self.cols, row, selectFnColInputs))
    self.rows = filter(innerSelectFn, self.rows)

  # generate new column for each tuple
  # generateFn takes in (row, tuple of vals) returns new column value
  # generateFnColInputs determines which column values are inputs to selectFn
  # modifies the relation!
  def generateCol(self, colName, generateFn, generateFnColInputs):
    def innserGenerateMap(row):
      newVal = generateFn(row, projectRow(self.cols, row, generateFnColInputs))
      return row + (newVal,)
    self.rows = map(innerGenerateMap, self.rows)
    self.cols = self.cols + (colName,)

  # left hash join
  # relations 1 and 2, join on columns joinIndex
  # defaults to outer join, inner join if inner=True
  #   (for unmatched rows set the right relation's fields to None
  #
  # error if both relations have a common non-join index column name
  def leftHashJoin(self, otherRelation, joinIndex, inner=True):
    # determine non-index columns from each relation
    # assert that no names are shared
    myNonIndex = list(self.cols)
    otherNonIndex = list(otherRelation.cols)
    for c in joinIndex:
      if c in myNonIndex: myNonIndex.remove(c)
      if c in otherNonIndex: otherNonIndex.remove(c)
      intersection = set(myNonIndex) & set(otherNonIndex)
    assert len(intersection) == 0, "non-index fields in common while joining: {!r}".format(intersection)

    # hash relation 2 (put it in a dictionary by {index columns -> non index columns}
    import collections
    joinDict = collections.defaultDict(list)
    for row in otherRelation.rows:
      key = projectRow(otherRelation.cols, row, joinIndex)
      vals = projectRow(otherRelation.cols, row, nonIndex2)
      joinDict[key].append(vals)

    newCols = joinIndex + tuple(myNonIndex) + tuple(otherNonIndex)
    newRows = []
    for row in self.rows:
      key = projectRow(self.cols, row, joinIndex)
      vals = projectRow(self.cols, row, myNonIndex)
      if key in joinDict:
        for otherRelationVals in joinDict[key]:
          newRows.append( key + vals + otherRelationVals )
      elif inner == False: # outer join, include Nones
        newRows.append( key + vals + tuple([None] * len(otherNonIndex)) )

    self.cols = newCols
    self.rows = newRows

  # return True if the relation contains duplicate rows based off the columns in keyCols
  def hasDuplicates(self, keyCols):
    keySet = set()
    for row in self.rows:
      key = projectRow(self.cols, row, keyCols)
      if key in keySet: return True
      keySet.add(key)
    return False

  # return True if the relations contain the same set of keys based off keyCols
  # if assert then die if not true
  def keysMatch(self, otherRelation, keyCols, **kwargs):
    myKeySet = set()
    otherKeySet = set()
    for key in [projectRow(self.cols, r, keyCols) for r in self.rows]:
      myKeySet.add(key)
    for key in [projectRow(otherRelation.cols, r, keyCols) for r in otherRelation.rows]:
      otherKeySet.add(key)
    symDiff = myKeySet ^ otherKeySet
    if 'assert' in kwargs and kwargs['assert']:
      assert len(symDiff) == 0, "keys mismatched\nIn left but not right:\n{!r}\nIn right but not left:\n{!r}".format(myKeySet-otherKeySet, otherKeySet-myKeySet)
    return len(symDiff) == 0

  # convenience functions:

  # castDict is a dict of {column name -> cast function}
  def cast(self, castDict):
    newRows = []
    for row in self.rows:
      newRow = list(row)
      for (val, colName) in zip(row, self.cols):
        if colName in castDict:
          try:
            newVal = castDict[colName](val)
          except:
            print "error casting field: {!r}, value: {!r}, type: {!r}" % (field, val, type(val))
          newRow[i]
      newRows.append(tuple(newRow))
    self.rows = newRows

  # filterDict is dict of {column name -> bool function (true to keep)}
  def filter(self. filterDict
    newRows = []
    for row in self.rows:
      keep = True
      for (val, colName) in zip(row, self.cols):
        if colName in castDict:
          try:
            keep = filterDict[colName](val)
          except:
            print "error filtering field: {!r}, value: {!r}, type: {!r}" % (field, val, type(val))

        if not keep:
          break # next row
      newRows.append(tuple(newRow))
    self.rows = newRows


# joinIndex is a tuple of columns that every dataset shares
# dataSets is a list of Relations
# return a new Relation (do not modify input relations)
def joinDataSetsOrDie(Relations, joinIndex):
  for rel in Relations:
    assert not rel.hasDuplicates(joinIndex)

  assert len(Relations) > 0, "Must have at least 1 relation to join"
  newRel = Relation(Relations[0])
  if len(dataSets) > 1:
    for otherRelation in Relations[1:]:
      newRel.keysMatch(otherRelation, joinIndex, assert=True)
      newRel.leftHashJoin(otherRelation, joinIndex)
  return newRel
