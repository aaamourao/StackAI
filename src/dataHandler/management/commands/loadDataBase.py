# loadDataBase.py -- This belongs to StackAI
# Discompress data from StackExchange and load it into django database
# 
# StackAI project intends to use machine learning approaches to find out
# patterns and make predictions on StackExchange dumped data.
# 
# Copyright (C) 2016 Adriano Mourao
# <mourao.aaa@gmail.com>
# 
# Copyright (C) 2016 Vinicius Garcia
# <vingarcia00@gmail.com>
#
# Copyright (C) 2016 Juliana Nunes
# <juliananunescomp@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys
import pyunpack
import shutil
from lxml import objectify
from lxml.etree import XMLParser
from django.core.management.base import BaseCommand, CommandError
from dataHandler.models import *
from progressbar import ProgressBar

defaultFolder = "../stackexchange/" 
dataPattern = '.7z'
tmpFolder = "./tmp"

def insertVote(elem):
    # create rows on foreignkey tables, if necessary
    try:
        relatedPost = Post.objects.get(id=elem.attrib['PostId'])
    except Post.DoesNotExist:
        relatedPost = Post(id=elem.attrib['PostId'])
        relatedPost.save()

    newVote = Vote(
            id = elem.attrib['Id'],
            postId = relatedPost,
            voteTypeId = elem.attrib['VoteTypeId'],
            creationDate = elem.attrib['CreationDate'],
    )
    # optional attributes
    if elem.attrib.has_key('UserId'):
        # create rows on foreignkey tables, if necessary
        try:
            voter = User.objects.get(id=elem.attrib['UserId'])
        except User.DoesNotExist:
            voter  = User(id=elem.attrib['UserId'])
            voter.save()
        newVote.userId = voter

    if elem.attrib.has_key('BountyAmount'):
        newVote.bountyAmount = elem.attrib['BountyAmount']
        
    newVote.save()

def insertBadge(elem):
    try:
        badgeOwner = User.objects.get(id=elem.attrib['UserId'])
    except User.DoesNotExist:
        badgeOwner = User(id=elem.attrib['UserId'])
        badgeOwner.save()
    newBadge = Badge(
            id = elem.attrib['Id'],
            userId = badgeOwner,
            name = elem.attrib['Name'],
            date = elem.attrib['Date'],
    )
    newBadge.save()

def insertPost(elem):
    newPost = Post(
            id = elem.attrib['Id'],
            postTypeId = elem.attrib['PostTypeId'],
            creationDate = elem.attrib['CreationDate'],
            score = elem.attrib['Score'],
            body = elem.attrib['Body'],
            lastActivityDate = elem.attrib['LastActivityDate'],
            commentCount = elem.attrib['CommentCount'],
    )
    if elem.attrib.has_key('DeletionDate'):
        newPost.deletionDate = elem.attrib['DeletionDate']
    if elem.attrib.has_key('ViewCount'):
        newPost.viewCount = elem.attrib['ViewCount']
    if elem.attrib.has_key('FavoriteCount'):
        newPost.favoriteCount = elem.attrib['FavoriteCount']
    if newPost.postTypeId == 1:
        newPost.acceptedAnswerId = Post.object.get(id=elem.attrib['AcceptedAnswerId'])
    if newPost.postTypeId == 2:
        newPost.parentId = Post.object.get(id=elem.attrib['ParentId'])
    newPost.save()

insertRow = {
        'votes': insertVote,
        'badges': insertBadge,
        'posts': insertPost,
}

class Command(BaseCommand):
    help = 'Load data dump on DataBase'

    def handle(self, *args, **options):
        # TODO: Handle user inputs and load it on data structures
        folder = defaultFolder

        # create temporary dir for descompressing data
        if os.path.exists(tmpFolder):
            print 'Warning: removing existent folder ' + tmpFolder
            shutil.rmtree(tmpFolder)
        os.makedirs(tmpFolder)

        print 'Generating .tz files list from ' + defaultFolder
        for root,_,files in os.walk(folder):
            gen7z = (file7z for file7z in files if file7z.endswith(dataPattern))
            for file7z in gen7z:
                dataPath = os.path.join(root, file7z)
                pyunpack.Archive(dataPath).extractall(tmpFolder)
                genXML = (fileXML for fileXML in os.listdir(tmpFolder))
                for fileXML in genXML:
                    print 'Loading data from ' + fileXML + ' extracted from ' + root + file7z
                    with open(os.path.join(tmpFolder, fileXML)) as f:
                        xml = f.read()

                    # huge_tree=True is a workaround for the bug #1285592 on lxml library
                    parser = XMLParser(huge_tree=True)
                    table = objectify.fromstring(xml, parser=parser)
                    ###devared2a###
                    if table.tag == 'posts':
                    ###enddev###

                        print 'Inserting ' + table.tag + ' from ' + fileXML
                        elemList = table.getchildren()
                        # progress bar initial setup
                        with ProgressBar(max_value=len(elemList)) as progress:
                            progUpdt = 0
                            for elem in elemList:
                                insertRow[table.tag](elem)
                                # update and increment progress
                                progress.update(progUpdt)
                                progUpdt += 1
                        # dev break!!!!!
                        break
                # dev break!!!!!
                break
            # dev break!!!!!
            break
        shutil.rmtree(tmpFolder)
