# -*- coding: utf-8 -*-

from django.db import models


class TaskResultModel(models.Model):

    result = models.CharField(max_length=255)
