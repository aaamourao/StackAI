from collections import Counter

class Tags():
  count = None
  table = None
  ndim = 0

  _delim = None
  _col = None
  def __init__(self, table, col='tags', min_count=0, ban_tags=[], filter=False):
    count = Counter()
    self.table = table
    self._col = col
    self._ban_tags = ban_tags

    for line in table:
      count.update(line[col])
    del count[""]
    for tag in ban_tags:
      del count[tag]

    self.count = count

    self.dropUncommon(min_count)

    if filter:
      self.filterSelf()

    self.ndim = len(self.count)

  def dropUncommon(self, min_count=0):
    if min_count == 0:
      return

    count = self.count

    count = Counter({
      tag:count[tag] for tag in count if count[tag] >= min_count
    })

    self.count = count
    self.ndim = len(self.count)

  def getTags(self):
    return self.count.keys()

  def filterSelf(self):
    self.table, self.count = self.filterTable()
    self.ndim = len(self.count)

  def filterTable(self, table=None):
    table = table if table else self.table

    if table == None:
      raise Exception("Please provide a table to filter!")

    new_table = []
    new_count = Counter()
    count = self.count
    ban = self._ban_tags
    
    for line in table:
      tags = []
      for tag in line[self._col]:
        if tag in count and tag not in ban:
          tags.append(tag)

      if len(tags) != 0:
        line[self._col] = tags
        new_table.append(line)
        new_count.update(line[self._col])

    return new_table, new_count

  def saveTags(self, addr, save_counts=True):
    with open(addr, 'w') as file:
      file.write('\t'.join( self.count.keys() ))

      if save_counts:
        file.write('\n' + '\t'.join( self.count.values() ))

  def loadTags(self, addr):
    with open(addr) as file:
      tags = file.readline().split('\t')
      counts = file.readline().split('\t')

      if counts:
        count = Counter(zip(tags,counts))
      else:
        count = Counter(tags)

    self.count = count
    self.ndim = len(self.count)

  # Return a vector with sum == 1 indicating the tag distribution of a user
  def makeFeatureVector(self, tags_list):
    tags = Counter(tags_list)
    total = len(tags_list)
    if total == 0:
      return [0] * len(self.count)
    return [ tags[k]/total for k in self.count ]

  # Return a binary list X where Xi indicates the presence
  # or abscence of the tag i on tags_list
  def makeBinaryVector(self, tags_list):
    return [ int(k in tags_list) for k in self.count ]














          
          
