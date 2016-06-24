
from dateutil.parser import parse
from lxml import etree

# Iterate over all the file rows
# Yield an etree.Element of the line.
def readRows(addr):
  with open(addr) as file:
    line = file.readline()

    while line:
      if line[:6] == '  <row':
        yield etree.XML(line)
      line = file.readline()

latest_dump_date = parse("2016-06-13")

# Post types allowed
post_types = {
  '1': 'Question',
  '2': 'Answer'
}

# Vote types allowed
vote_types = {
  '1': 'AcceptedByOriginator',
  '2': 'UpMod',
  '3': 'DownMod',
  '4': 'Offensive',
  '5': 'Favorite',
  '6': 'Close',
  '7': 'Reopen',
  '8': 'BountyStart',
  '9': 'BountyClose',
  '10': 'Deletion',
  '11': 'Undeletion',
  '12': 'Spam',
  '13': 'InfoModerator'
}
