#!/usr/bin/env python
#
# run.py -- This belongs to StackAI
# Execute data uncompress, trainnings and validation over StackExchange data
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

defaultFolder = "../stackexchange/" 
dataPattern = '*.7z'
tempFolder = "./tmp"

def main(args=defaultFolder):
    # TODO: Handle user inputs and load it on data structures
    folder = defaultFolder

    # create temporary dir for descompressing data
    if os.path.exists(tempFolder):
        print 'Warning: removing existent folder ' + tmpFolder
        shutil.rmtree(tmpFolder)
    os.makedirs(tempFolder)

    print 'Generating .tz files list from ' + defaultFolder
    for root,_,files in os.walk(folder):
        gen = (data for data in files if data.endswith(".7z"))
        for data in gen:
            dataPath = os.path.join(root, data)
            pyunpack.Archive(dataPath).extractall(tempFolder)
    shutil.rmtree(tempFolder)

if __name__ == '__main__':
    main(sys.argv)
