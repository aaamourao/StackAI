# dataHandler/models.py -- This belongs to StackAI
# Model for handling anathomy's tables
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
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

encoding = 'utf-8'

@python_2_unicode_compatible
class User(models.Model):
    id = models.AutoField(primary_key=True)
    reputation = models.IntegerField()
    creationDate = models.DateTimeField()
    displayName = models.CharField(max_length=200)
    lastAccessDate = models.DateTimeField()
    webSiteURL = models.URLField(blank=True,null=True,default=None)
    location = models.CharField(max_length=1024)
    age = models.IntegerField(blank=True,null=True,default=None)
    aboutMe = models.TextField(blank=True,null=True,default=None)
    views = models.IntegerField()
    upVotes = models.IntegerField()
    downVotes = models.IntegerField()
    emailHash = models.CharField(max_length=200, blank=True,null=True,default=None)
    accountId = models.IntegerField(blank=True,null=True,default=None)
    def __str__(self):
        return unicode(self).encode(encoding)

# Post types allowed
POST_TYPES = (
        (1, 'Question'),
        (2, 'Answer'),
)

@python_2_unicode_compatible
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    postTypeId = models.IntegerField(choices=POST_TYPES,default=2)
    postId = models.ForeignKey('self', related_name='base_question',blank=True,null=True,default=None)
    acceptedAnswerId = models.ForeignKey('self', related_name='main_answer',blank=True,null=True,default=None)
    parentId = models.ForeignKey('self', related_name='target_question',blank=True,null=True,default=None)
    creationDate = models.DateTimeField()
    deletionDate = models.DateTimeField(blank=True,null=True,default=None)
    score = models.IntegerField()
    viewCount = models.IntegerField(blank=True,null=True,default=None)
    body = models.TextField()
    ownerUserId = models.ForeignKey(User, related_name='post_owner',blank=True,null=True,default=None)
    lastEditorUserId = models.ForeignKey(User, related_name='last_editor',blank=True,null=True,default=None)
    lastEditorDisplayName = models.CharField(max_length=200,blank=True,null=True,default=None)
    lastEditDate = models.DateTimeField(blank=True,null=True,default=None)
    lastActivityDate = models.DateTimeField()
    communityOwnedDate = models.DateTimeField(blank=True,null=True,default=None)
    title = models.CharField(max_length=1024,blank=True,null=True,default=None)
    tags = models.TextField(blank=True,null=True,default=None)
    answerCount = models.IntegerField(blank=True,null=True,default=None)
    commentCount = models.IntegerField()
    favoriteCount = models.IntegerField(blank=True,null=True,default=None)
    closedDate = models.DateTimeField(blank=True,null=True,default=None)
    def __str__(self):
        return unicode(self).encode(encoding)

@python_2_unicode_compatible
class Badge(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    date = models.DateTimeField()
    def __str__(self):
        return unicode(self).encode(encoding)

@python_2_unicode_compatible
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    score = models.IntegerField(blank=True,null=True,default=None)
    text = models.TextField()
    creationDate = models.DateTimeField()
    userId = models.ForeignKey(User,blank=True,null=True,default=None)
    userDisplayName = models.CharField(max_length=1024,blank=True,null=True,default=None)
    def __str__(self):
        return unicode(self).encode(encoding)

# Vote types allowed
VOTE_TYPES = (
        (1, 'AcceptedByOriginator'),
        (2, 'UpMod'),
        (3, 'DownMod'),
        (4, 'Offensive'),
        (5, 'Favorite'),
        (6, 'Close'),
        (7, 'Reopen'),
        (8, 'BountyStart'),
        (9, 'BountyClose'),
        (10, 'Deletion'),
        (11, 'Undeletion'),
        (12, 'Spam'),
        (13, 'InfoModerator'),
)

@python_2_unicode_compatible
class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    # TODO: Issue #21: set blank/null/default due that
    postId = models.ForeignKey(Post,on_delete=models.CASCADE,blank=True,null=True,default=None)
    userId = models.ForeignKey(User,blank=True,null=True,default=None)
    voteTypeId = models.IntegerField(choices=VOTE_TYPES)
    creationDate = models.DateTimeField()
    BountyAmount = models.IntegerField(blank=True,null=True,default=None)
    def __str__(self):
        return unicode(self).encode(encoding)
