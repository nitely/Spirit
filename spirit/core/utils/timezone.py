# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
import logging
import datetime

import pytz

logger = logging.getLogger('django')

TIMEZONE_CHOICES = []


def is_standard_time(time_zone, date_time):
    try:
        dst_delta = time_zone.dst(date_time, is_dst=False)
    except TypeError:
        dst_delta = time_zone.dst(date_time)

    return dst_delta == datetime.timedelta(0)


def utc_offset(time_zone, fixed_dt=None):
    tz = pytz.timezone(time_zone)
    now = fixed_dt or datetime.datetime.now()

    for __ in range(72):
        if is_standard_time(time_zone=tz, date_time=now):
            break

        now += datetime.timedelta(days=30)
    else:
        logger.warning(
            'Standard Time not found for %s, will use DST.' % time_zone)

    return tz.localize(now, is_dst=False).strftime('%z')


def offset_to_int(offset):
    assert offset[0] in ('-', '+')

    sign, hour, minutes = offset[0], offset[1:3], offset[3:5]
    utc_offset_int = int(hour) + int(minutes) / 100

    if sign == '-':
        utc_offset_int *= -1

    return utc_offset_int


def timezones_by_offset():
    return sorted(
        list((utc_offset(tz), tz)
             for tz in pytz.common_timezones),
        key=lambda x: offset_to_int(x[0]))


def _populate_timezone():
    """
    Result format::

        [
            ("Africa", [
                ("Africa/Abidjan", "(UTC...) Abidjan"),
                ("Africa/Accra", "(UTC...) Accra"),
                #...
            ]),
            ("America", [
                ("America/Argentina/Buenos_Aires",
                 "(UTC...) Argentina, Buenos Aires"),
                #...
            ]),
            #...
        ]
    """
    timezones_tree = {}

    for offset, tz in timezones_by_offset():
        zone_parts = tz.split('/')
        zone = zone_parts[0]
        zone_list = timezones_tree.get(zone, [])

        if not zone_list:
            TIMEZONE_CHOICES.append((zone, zone_list))

        if len(zone_parts) > 1:
            zone_label = ', '.join(zone_parts[1:]).replace('_', ' ')
        else:
            zone_label = zone

        zone_list.append((tz, '(UTC{}) {}'.format(offset, zone_label)))
        timezones_tree[zone] = zone_list

    TIMEZONE_CHOICES.sort(key=lambda x: x[0])

_populate_timezone()
