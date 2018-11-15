from django.db import models

from django.urls import reverse # Used to generate URLs by reversing the URL patterns

import uuid

class Problem(models.Model):
    problemcode = models.CharField(max_length=200, help_text='Enter problem codes')
    def __str__(self):
        """String for representing the Model object."""
        return self.problemcode


class Contest(models.Model):
    
    name = models.CharField(max_length=200)
    contesttype = models.CharField(max_length=3)
    ContestCode = models.CharField(max_length=200)
    problemcode = models.ManyToManyField(Problem, help_text='Select Problems')
    startDate = models.DateTimeField(null=True, blank=True)
    endDate = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField()
    class Meta:
        ordering = ['-startDate', 'name']

    def __str__(self):
        """String for representing the Model object."""
        return self.ContestCode
    

class User(models.Model):
    userName = models.CharField(max_length=200, default = 'abc')
    def __str__(self):
        return self.userName

class Team(models.Model):
    teamname = models.CharField(max_length=100)
    teamid = models.CharField(max_length=100, default = 'ab')
    user1 = models.CharField(max_length=100, null = True, blank = True)
    user2 = models.CharField(max_length=100, null = True, blank = True)
    user3 = models.CharField(max_length=100, null = True, blank = True)

    def __str__(self):
        return self.teamid

class userContest(models.Model):
    ContestCode = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    startDate = models.DateTimeField(null=True, blank=True)
    endDate = models.DateTimeField(null=True, blank=True)
    user =  models.CharField(max_length=100,null=True, blank=True)
    team =  models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank = True)
    class Meta:
        ordering = ['-startDate']

    def __str__(self):
        return self.ContestCode

class pendingrequests(models.Model):
    userp = models.CharField(max_length=100, default = 'abcds')
    teamname = models.CharField(max_length=100, default = 'ab')
    teamidp = models.CharField(max_length=100)

    def __str__(self):
        return self.teamidp

class results(models.Model):
    contestid = models.IntegerField()
    problemcode = models.CharField(max_length=100)
    time = models.DateTimeField(null=True, blank = True)
    penalty = models.IntegerField(null=True, blank = True)