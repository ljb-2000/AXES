from django.db import models
from systemmanage.models import Game
from django.contrib.auth.models import User

# Create your models here.


class Url(models.Model):
    url = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.url


class Role(models.Model):
    name = models.CharField(max_length=255)
    role = models.IntegerField(null=True)
    url = models.ManyToManyField(Url, null=True, blank=True)

    def __unicode__(self):
        return self.name


#  class Permission(models.Model):
    #  name = models.CharField(max_length=255)
    #  project = models.ForeignKey(Game, null=True, blank=True)

    #  def __unicode__(self):
        #  return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    role = models.ForeignKey(Role, null=True, blank=True)
    permission = models.ManyToManyField(Game, blank=True)

    def __unicode__(self):
        return self.user.username
