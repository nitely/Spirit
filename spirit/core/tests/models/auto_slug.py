# -*- coding: utf-8 -*-

from django.db import models

from ...utils.models import AutoSlugField


class AutoSlugModel(models.Model):

    slug = AutoSlugField(max_length=50)


class AutoSlugDefaultModel(models.Model):

    slug = AutoSlugField(max_length=50, default="foo")


class AutoSlugPopulateFromModel(models.Model):

    title = models.CharField(max_length=255, blank=True)
    slug = AutoSlugField(populate_from='title', max_length=50)


class AutoSlugBadPopulateFromModel(models.Model):

    slug = AutoSlugField(populate_from='bad', max_length=50)
