# createDataBase.py -- This belongs to StackAI
# Create mysql database
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
from django.core.management.base import BaseCommand, CommandError
import mysql.connector
import getpass

class Command(BaseCommand):
    help = 'Create django user and DataBase'

    def handle(self, *args, **options):
        print '**Create MySQL database**'
        print 'Type MySQL root password. It will not be stored.'
        rootPasswd = getpass.getpass(prompt='> root@localhost password:')

        # connect to mysql database
        cnx = mysql.connector.connect(user='root', passwd=rootPasswd)
        print 'Succesfully connected to MySQL as root' 
        print 'Creating StackAI host @localhost'
        print 'Type MySQL password for StackAI user. It will be stored on local file'
        stackAIPasswd = getpass.getpass(prompt='> StackAI@localhost password:')
        reStackAIPasswd = getpass.getpass(prompt='> Type StackAI password again:')

        if stackAIPasswd != reStackAIPasswd:
            raise NameError("Passwords don't match")

        cursor = cnx.cursor()
        cursor.execute("create user 'StackAI'@'localhost' identified by '" + stackAIPasswd + "'i;")
        print 'Succesfully created StackAI user\n'
        print 'Creating stackexchange database'
        cursor.execute('create database stackexchange')
        print 'Succesfully created stackexchange database\n'
        cursor.execute("grant all privileges on stackexchange . * to 'StackAI'@'localhost'")
        cursor.execute("flush privileges")
        print 'Success! StackAI has stackexchange database privileges\n'
        print 'Now execute: python manage.py migrate'
