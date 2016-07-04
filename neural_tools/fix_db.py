import re

from lxml import etree
from time import clock

getId_re = re.compile('Id="(-?[0-9]+)"')
getOwner_re = re.compile('OwnerUserId="(-?[0-9]+)"')
getInfo_re = re.compile('Id="(-?[0-9]+).*OwnerUserId="(-?[0-9]+)"')

def getId(line):
  match = getId_re.search(line)
  return match.group(1) if match else None

def getOwner(line):
  match = getOwner_re.search(line)
  return match.group(1) if match else None

def getInfo(line):
  match = getInfo_re.search(line)
  return match.groups() if match else None

def replaceId():
  success = 0
  fail_user = 0
  fail_post = 0
  start = clock()
  for line in readRows('../stackexchange/Posts.xml'):

    #info = getInfo(line)
    #p1, u1 = post_id, user_id = info if info else [ None, None ]

    xml = etree.XML(line)
    u2 = user_id = xml.get('OwnerUserId')
    p2 = post_id = xml.get('Id')

    #u3 = user_id = getOwner(line)
    #p3 = post_id = getId(line)

    if not user_id:
      #print "Could not recover OwnerUserId or Id from row:\n%s" % etree.tostring(xml)
      #fail_user += 1
      continue
    if not post_id:
      #fail_post += 1
      continue
    user_id = int(user_id)
    post_id = int(post_id)

    user = (User.objects.filter(pk=user_id) or [None])[0]
    post = (Post.objects.filter(pk=post_id) or [None])[0]
    if user == None:
      #print "No user found with id: %s" % user_id
      fail_user += 1
      continue
    if post == None:
      #print "No post found with id: %s" % post_id
      fail_post += 1
      continue

    success += 1
    #post.ownerUserId=user
    #post.save()

  return success, fail_user, fail_post, "%s seconds" % (clock()-start)

