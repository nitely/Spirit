# -*- coding: utf-8 -*-

from haystack import signals

from spirit.core.conf import settings
from spirit.core.signals import search_index_update
from spirit.topic.models import Topic


class RealtimeSignalProcessor(signals.RealtimeSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        if isinstance(instance, Topic):
            if instance.category_id == settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
                return
        super().handle_save(sender, instance, **kwargs)

    def setup(self):
        search_index_update.connect(
            self.handle_save,
            dispatch_uid='signals.search')

    def teardown(self):
        search_index_update.disconnect(
            self.handle_save,
            dispatch_uid='signals.search')
