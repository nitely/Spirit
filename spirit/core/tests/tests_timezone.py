# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytz
import datetime

from django.test import TestCase
from django.utils import timezone

from ..utils import timezone as utils_timezone
from ..utils.timezone import timezones


class UtilsTimezoneTests(TestCase):

    def test_timezones(self):
        """
        Should be ready to be use as choices
        """
        time_zones_dict = dict(timezones())
        self.assertTrue('America', time_zones_dict)
        time_zones_america_dict = dict(time_zones_dict['America'])
        self.assertTrue(
            'America/Argentina/Buenos_Aires' in time_zones_america_dict)
        self.assertEqual(
            time_zones_america_dict['America/Argentina/Buenos_Aires'],
            '(UTC-0300) Argentina, Buenos Aires')

    def test_timezones_are_valid(self):
        """
        Should be valid timezones
        """
        time_zones = timezones()
        self.assertTrue(bool(time_zones))

        for zone, time_zone_list in time_zones:
            for tz, text in time_zone_list:
                timezone.activate(tz)

        self.assertRaises(Exception, timezone.activate, "badtimezone")

    def test_is_standard_time(self):
        """
        Should return whether a timezone + datetime is in DST or not
        """
        tz = pytz.timezone('America/St_Johns')
        no_dst = datetime.datetime(2012, 3, 9, 22, 30)
        dst_normal = datetime.datetime(2009, 9, 1)
        dst_ambiguous = datetime.datetime(2009, 10, 31, 23, 30)
        self.assertTrue(utils_timezone.is_standard_time(tz, no_dst))
        self.assertFalse(utils_timezone.is_standard_time(tz, dst_normal))
        self.assertTrue(utils_timezone.is_standard_time(tz, dst_ambiguous))

        tz = pytz.timezone('UTC')
        self.assertTrue(utils_timezone.is_standard_time(tz, no_dst))

    def test_utc_offset(self):
        """
        Should return the offset for a given timezone
        """
        tz = 'America/St_Johns'
        no_dst = datetime.datetime(2012, 3, 9, 22, 30)
        dst_normal = datetime.datetime(2009, 9, 1)
        dst_ambiguous = datetime.datetime(2009, 10, 31, 23, 30)
        self.assertEqual(utils_timezone.utc_offset(tz, no_dst), '-0330')
        self.assertEqual(utils_timezone.utc_offset(tz, dst_normal), '-0330')
        self.assertEqual(utils_timezone.utc_offset(tz, dst_ambiguous), '-0330')
        self.assertEqual(utils_timezone.utc_offset(tz), '-0330')

        tz = 'UTC'
        self.assertEqual(utils_timezone.utc_offset(tz, no_dst), '+0000')

    def test_offset_to_int(self):
        """
        Should convert an offset into its equivalent number
        """
        self.assertEqual(utils_timezone.offset_to_int('-0330'), -3.3)
        self.assertEqual(utils_timezone.offset_to_int('+0000'), 0.0)
        self.assertEqual(utils_timezone.offset_to_int('+0130'), 1.3)
        self.assertEqual(utils_timezone.offset_to_int('+0135'), 1.35)
        self.assertEqual(utils_timezone.offset_to_int('+1135'), 11.35)

    def test_timezones_by_offset(self):
        """
        Should sort all timezones by offset and then by timezone name
        """
        fake_timezones_tup = (
            ('aaaa', '+0000'),
            ('bbbb', '+0000'),
            ('cccc', '-0300'),
            ('dddd', '+0300'))
        fake_timezones_dict = dict(fake_timezones_tup)
        fake_timezones = [
            tz for tz, offset in reversed(fake_timezones_tup)]

        def fake_utc_offset(tz):
            return fake_timezones_dict[tz]

        (common_timezones_org, utils_timezone.pytz.common_timezones,
         utc_offset_org, utils_timezone.utc_offset) = (
            utils_timezone.pytz.common_timezones, fake_timezones,
            utils_timezone.utc_offset, fake_utc_offset)
        try:
            self.assertEqual(
                utils_timezone.timezones_by_offset(),
                [
                    ('-0300', 'cccc'),
                    ('+0000', 'aaaa'),
                    ('+0000', 'bbbb'),
                    ('+0300', 'dddd')])
        finally:
            utils_timezone.pytz.common_timezones = common_timezones_org
            utils_timezone.utc_offset = utc_offset_org

    def test_timezone_format(self):
        """
        Should return the zone and the timezone description
        """
        self.assertEqual(
            utils_timezone.timezone_format('UTC', '+0000'),
            ('UTC', '(UTC+0000) UTC'))
        self.assertEqual(
            utils_timezone.timezone_format(
                'America/Argentina/Buenos_Aires', '-0300'),
            ('America', '(UTC-0300) Argentina, Buenos Aires'))
