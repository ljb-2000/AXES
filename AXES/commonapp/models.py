from django.db import models
from systemmanage.models import Game
from django.contrib.auth.models import User

# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Permission(models.Model):
    name = models.CharField(max_length=255)
    project = models.ManyToManyField(Game)

    def __unicode__(self):
        return self.name


class Host(models.Model):
    host = models.CharField(max_length=255)

    def __unicode__(self):
        return self.host


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    role = models.ManyToManyField(Role)
    permission = models.ManyToManyField(Permission, blank=True)
    host = models.ManyToManyField(Host, blank=True)

    def __unicode__(self):
        return self.user.username
