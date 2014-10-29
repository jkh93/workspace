# coding: utf-8
from django.db import models
from main import models as qm


class WashStep(models.Model):
    name = models.CharField(max_length=50)
    position = models.IntegerField()
    template = models.BooleanField(default=False)
    #ingredients manytomany

    def __unicode__(self):
        return self.name


class WashType(models.Model):
    name = models.CharField(max_length=50)
    wash_steps = models.ManyToManyField(WashStep, through='WashTypeStep',
        null=True, blank=True)
    position = models.IntegerField()
    template = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class WashTypeStep(models.Model):
    wash_step = models.ForeignKey(WashStep)
    wash_type = models.ForeignKey(WashType)
    position = models.IntegerField()


class Wash(models.Model):
    wash_date = models.DateTimeField()
    wash_type = models.ForeignKey(WashType)
    tanks = models.ManyToManyField(qm.Tank, null=True)


class KegWash(models.Model):
    wash = models.ForeignKey(Wash)
    keg = models.IntegerField()

