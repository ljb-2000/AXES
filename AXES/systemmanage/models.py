from django.db import models

# Create your models here.


class Idc(models.Model):
    idc_name_cn = models.CharField(max_length=100, null=False)
    idc_name_py = models.CharField(max_length=100, null=False)
    proxy_name = models.CharField(max_length=100, blank=True)


class Game(models.Model):
    game_name_cn = models.CharField(max_length=100, null=False)
    game_name_py = models.CharField(max_length=100, null=False)
    game_system = models.CharField(max_length=100, blank=True)
