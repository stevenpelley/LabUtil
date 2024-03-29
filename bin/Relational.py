#!/usr/bin/python
#
# Relational algebra operations operations
# cols: a tuple of strings representing the columns of this relation
# rows: a list of tuples, where each tuple is the values corresponding to cols

class Relation:
  # constructor
  # for now have:
  # default (empty relation)
  # copy (copies rows and cols)
  # (tuple(cols), list(tuple(rows)),)
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
  @staticmethod
  def projectRow(cols, row, projectFields):
    assert isinstance(projectFields, tuple), "Projection Fields must be a tuple"
    newRow = []
    for col in projectFields:
      assert col in cols, "Projection Field {!r} not in cols {!r}".format(f, cols)
      newRow.append(row[cols.index(col)])
    return tuple(newRow)

  # projection on relation
  # A projection collects the specified columns of each tuple in the relation
  # include only those fields listed in projectFields
  def project(self, projectCols):
    newRows = []
    for row in self.rows:
      newRows.append(Relation.projectRow(self.cols, row, projectCols))
    self.cols = projectCols
    self.rows = newRows

  # perform a selection (essentially a filter)
  # A selection collects all columns of specified rows
  # selectFn takes in (tuple of vals) returns True to keep row, False to pass
  # selectFnColInputs determines which column values are the inputs to selectFn
  def select(self, selectFn, selectFnColInputs):
    innerSelectFn = lambda row: selectFn(Relation.projectRow(self.cols, row, selectFnColInputs))
    self.rows = filter(innerSelectFn, self.rows)

  # generate new column for each tuple
  # generateFn takes in tuple of vals, returns new column value
  # generateFnColInputs determines which column values are inputs to generateFn
  # modifies the relation!
  def generateCol(self, colName, generateFn, generateFnColInputs):
    def innerGenerateMap(row):
      newVal = generateFn(Relation.projectRow(self.cols, row, generateFnColInputs))
      return row + (newVal,)
    self.rows = map(innerGenerateMap, self.rows)
    self.cols = self.cols + (colName,)

  # generate multiple new rows from each row
  # allows a number of new columns to be created
  # generateFn takes in (row, tuple of vals) returns list of tuples of new columns vals
  # generateFnColInputs determines which column values are inputs to generateFn
  # each new row will be oldRow + newColVals for newColVals in return value of generateFn
  def splitAndGenerateCols(self, colNames, generateFn, generateFnColInputs):
    newRows = []
    for row in self.rows:
      for newColVals in generateFn(row, projectRow(self.cols, row, generateFnColInputs)):
        assert len(newColVals) == len(colNames), "number of new values must match number of new columns"
        assert isinstance(newColVals, tuple), "new values must be in a tuple"
        newRows.append(row + newColVals)
    self.rows = newRows
    self.cols = self.cols + colNames

  # left hash join
  # relations 1 and 2, join on columns joinIndex
  # defaults to outer join, inner join if inner=True
  #   (for unmatched rows set the right relation's fields to None
  #
  # error if both relations have a common non-join index column name
  #
  # description: A join combines 2 relations into 1 by matching tuples
  # by the values of joinIndex.  The fields of joinIndex must exist in
  # both the left and right relations.  On a match, the non-joinIndex
  # column values will be included from the left and right tuples
  #
  # An outer join always includes all rows from the left relation
  # Rows in the left relation that do not match receive None for columns
  # from the right relation
  #
  # if multiple matches occur the cartesian product of rows with that
  # joinIndex key from the left and right relations is produced
  # (i.e.) all possible matches are created between left and right
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
  # if assert then die if not a match
  def keysMatch(self, otherRelation, keyCols, **kwargs):
    myKeySet = set()
    otherKeySet = set()
    for key in [projectRow(self.cols, r, keyCols) for r in self.rows]:
      myKeySet.add(key)
    for key in [projectRow(otherRelation.cols, r, keyCols) for r in otherRelation.rows]:
      otherKeySet.add(key)
    symDiff = myKeySet ^ otherKeySet
    if 'doAssert' in kwargs and kwargs['doAssert']:
      assert len(symDiff) == 0, "keys mismatched\nIn left but not right:\n{!r}\nIn right but not left:\n{!r}".format(myKeySet-otherKeySet, otherKeySet-myKeySet)
    return len(symDiff) == 0

  # convenience functions:

  # castDict is a dict of {column name -> cast function}
  def cast(self, castDict):
    newRows = []
    for row in self.rows:
      newRow = list(row)
      for i, (val, colName) in enumerate(zip(row, self.cols)):
        if colName in castDict:
          try:
            val = castDict[colName](val)
          except:
            print "error casting column: {!r}, value: {!r}, type: {!r}".format(colName, val, type(val))
          newRow[i] = val
      newRows.append(tuple(newRow))
    self.rows = newRows

  # filterDict is dict of {column name -> bool function (true to keep)}
  def filter(self, filterDict):
    newRows = []
    for row in self.rows:
      keep = True
      for (val, colName) in zip(row, self.cols):
        if colName in filterDict:
          try:
            keep = filterDict[colName](val)
          except:
            print "error filtering field: {!r}, value: {!r}, type: {!r}" % (field, val, type(val))

        if not keep:
          break # next row
      if keep:
        newRows.append(row)
    self.rows = newRows

  # calculate the mins of all rows
  def mins(self):
    import operator
    outputMins = [0] * len(self.cols)
    for i in range(len(self.cols)):
      l = map(operator.itemgetter(i), self.rows)
      outputMins[i] = min(l)
    return tuple(outputMins)

  def __str__(self):
    return self.toStr(5)

  def toStr(self, rowCount=-1):
    # convert so that we can properly add newlines
    rowCount = len(self.rows) if rowCount == -1 else rowCount
    out = (""
      + "relation\n"
      + "cols: {}\n".format(self.cols)
      + "# rows: {}\n".format(len(self.rows))
      + "rows:\n"
    )
    for i, t in enumerate(sorted(self.rows)[0:rowCount]):
      out += str(t)
      if i != rowCount-1:
        out += "\n"
    return out

# multi-way inner join between several relations
# relations is a list of Relations
# joinIndex is a tuple of columns that every dataset shares
# return a new Relation (do not modify input relations)
def joinDataSetsOrDie(relations, joinIndex):
  for rel in relations:
    assert not rel.hasDuplicates(joinIndex)

  assert len(relations) > 0, "Must have at least 1 relation to join"
  newRel = Relation(relations[0])
  if len(dataSets) > 1:
    for otherRelation in relations[1:]:
      newRel.keysMatch(otherRelation, joinIndex, doAssert=True)
      newRel.leftHashJoin(otherRelation, joinIndex)
  return newRel
