
import os

from .stack_tools import readRows, tags_re
from csv import DictWriter, DictReader

class PostTable():
  table = None

  def __init__(self, dir_addr, saveUrl=False):
    table = []
    id_table = {}
    
    for row in readRows(os.path.join(dir_addr, 'Posts.xml')):

      # Check authors ids:
      users = []
      owner = row.get('OwnerUserId')
      if owner:
        users.append(owner)
      editor = row.get('LastEditorUserId')
      if editor:
        users.append(editor)

      p_type = row.get('PostTypeId')
      id = row.get('Id') if p_type == "1" else row.get('ParentId')

      if id not in id_table:
        line = {
          'id': id,
          'title': "",
          'users': [],
          'tags': [], 
          'neg_score': None
        }

        # Save the line:
        table.append(line)
        id_table[id] = line
      else:
        line = id_table[id]

      if p_type == "1":
        line['title'] = row.get('Title')
        line['users'].extend(users)
        line['tags'] = tags_re.findall(row.get('Tags'))
        line['neg_score'] = (int( row.get('Score') ) < 0)
        if saveUrl:
          line['url'] = row.get('url')
      elif p_type == "2":
        line['users'].extend(users)

    self.table = table

  csvheader = [ 'id', 'title', 'users', 'tags', 'neg_score' ]
  def saveTable(self, addr):
    with open(addr, 'w') as file:
      w = DictWriter(file, self.csvheader, delimiter='\t')
      w.writeheader()
      w.writerows(self.table)

  def loadTable(self, addr):
    with open(addr) as file:
      table = list(DictReader(file, delimiter='\t'))
      self.table = table
      return table
















      

