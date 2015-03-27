# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.paginator import InvalidPage
from django.conf import settings


class YTPaginator(object):
    """
    It'll limit the page list to a given limit
    """

    def __init__(self, object_list, per_page, allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = per_page
        self.allow_empty_first_page = allow_empty_first_page

    def validate_number(self, number):
        """Validates the given 1-based page number."""
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise InvalidPage("That page number is not an integer")

        if number < 1:
            raise InvalidPage("That page number is less than 1")

        return number

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        offset = (number - 1) * self.per_page
        limit = offset + self.per_page

        object_list = self.object_list[offset:limit]
        page = YTPage(object_list, number, self)

        if not page.num_pages:
            if number != 1 or not self.allow_empty_first_page:
                raise InvalidPage("That page contains no results")

        return page


class YTPage(object):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator
        self._num_pages = None
        self._max_pages = settings.ST_YT_PAGINATOR_PAGE_RANGE * 2 + 1

    def __repr__(self):
        return '<Page %s>' % self.number

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(self.object_list, list):
            self.object_list = list(self.object_list)

        return self.object_list[index]

    @property
    def num_pages(self):
        """
        Return the number of pages
        relative to the current page
        limited by max_pages
        """
        if self._num_pages is not None:
            return self._num_pages

        offset = (self.number - 1) * self.paginator.per_page
        limit = offset + self.paginator.per_page * self._max_pages

        try:
            count = self.paginator.object_list[offset:limit].count()
        except (AttributeError, TypeError):
            # If has no count() method or requires arguments
            count = len(self.paginator.object_list[offset:limit])

        if not count:
            self._num_pages = 0
        else:
            offset_pages = (-count // self.paginator.per_page) * -1  # ceil
            self._num_pages = self.number - 1 + offset_pages

        return self._num_pages

    @property
    def page_range(self):
        pages_range = settings.ST_YT_PAGINATOR_PAGE_RANGE

        first_page = self.number - pages_range
        last_page = self.number + pages_range

        if last_page < self._max_pages:
            last_page = self._max_pages

        if last_page > self.num_pages:
            last_page = self.num_pages

        if last_page - first_page < self._max_pages:
            first_page = last_page - self._max_pages + 1

        if first_page < 1:
            first_page = 1

        return range(first_page, last_page + 1)

    def next_page_number(self):
        return self.paginator.validate_number(self.number + 1)

    def previous_page_number(self):
        return self.paginator.validate_number(self.number - 1)


__all__ = [YTPaginator, YTPage, InvalidPage]
