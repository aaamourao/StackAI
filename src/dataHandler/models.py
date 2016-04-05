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

class User(models.Model):
    id = models.AutoField(primary_key=True)
    reputation = models.IntegerField()
    creationDate = models.DateTimeField()
    displayName = models.CharField(max_length=200)
    lastAccessDate = models.DateTimeField()
    webSiteURL = models.URLField()
    location = models.CharField(max_length=1024)
    age = models.IntegerField()
    aboutMe = models.TextField()
    upVotes = models.IntegerField()
    downVotes = models.IntegerField()
    emailHash = models.CharField(max_length=200)

# Post types allowed
POST_TYPES = (
        (1, 'Question'),
        (2, 'Answer'),
)

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    postTypeId = models.IntegerField(choices=POST_TYPES)
    # TODO: postId is defined only if postTypeId=2
    postId = models.ForeignKey('self', related_name='base_question')
    # TODO: acceptedAnswerId is defined only if postTypeId=1
    acceptedAnswerId = models.ForeignKey('self', related_name='main_answer')
    creationDate = models.DateTimeField()
    score = models.IntegerField()
    viewCount = models.IntegerField()
    body = models.TextField()
    # TODO: ownerUserId is present only if user has not been deleted
    ownerUserId = models.ForeignKey(User, related_name='post_owner')
    lastEditorUserId = models.ForeignKey(User, related_name='last_editor')
    lastEditorDisplayName = models.CharField(max_length=200)
    # TODO: insert default value
    lastEditDate = models.DateTimeField()
    # TODO: insert default value
    lastActivityDate = models.DateTimeField()
    # TODO: only exists if community wikied
    communityOwnedDate = models.DateTimeField()
    title = models.CharField(max_length=1024)
    tags = models.TextField()
    answerCount = models.IntegerField()
    commentCount = models.IntegerField()
    favoriteCount = models.IntegerField()
    closedDate = models.DateTimeField()

class Badge(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    date = models.DateTimeField()

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    score = models.IntegerField()
    text = models.TextField()
    creationDate = models.DateTimeField()
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

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

class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    postId = models.ForeignKey(Post, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    voteTypeId = models.IntegerField(choices=VOTE_TYPES)
    creationDate = models.DateTimeField()
    BountyAmount = models.IntegerField()
