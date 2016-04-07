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

defaultFolder = "../stackexchange/" 
dataPattern = '.7z'
tmpFolder = "./tmp"

def insertVote(table):
    for elem in table.getchildren():
        # create rows on foreignkey tables, if necessary
        try:
            newPost = Post.objects.get(id=elem.attrib['PostId'])
        except Post.DoesNotExist:
            newPost = Post(id=elem.attrib['PostId'])
            newPost.save()

        newVote = Vote( 
                id = elem.attrib['Id'],
                postId = newPost,
                voteTypeId = elem.attrib['VoteTypeId'],
                creationDate = elem.attrib['CreationDate'],
        )
        # optional attributes
        if elem.attrib.has_key('UserId'):
            # create rows on foreignkey tables, if necessary
            try:
                newUser = User.objects.get(id=elem.attrib['UserId'])
            except User.DoesNotExist:
                newUser = User(id=elem.attrib['UserId'])
                newUser.save()
            newVote.userId = newUser

        if elem.attrib.has_key('BountyAmount'):
            newVote.bountyAmount = elem.attrib['BountyAmount']
            
        newVote.save()
        print 'Vote saved. Id = ' + newVote.id

def insertBadge(table):
    print 'NaN'

insertRow = {
        'votes': insertVote,
        'badges': insertBadge,
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

                    print 'Inserting ' + table.tag + ' from ' + tmpFolder + '/' + fileXML
                    insertRow[table.tag](table)
                    # dev break!!!!!
                    break
                # dev break!!!!!
                break
        shutil.rmtree(tmpFolder)
