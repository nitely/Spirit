# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core import signing
from django.utils.encoding import smart_text


class TokenGenerator(object):

    def _uid(self, user):
        raise NotImplementedError

    def generate(self, user, data=None):
        """
        Django signer uses colon (:) for components separation
        JSON_object:hash_first_component:hash_secret, all base64 encoded
        that aint so url-safe, so Im replacing them by dots (.)

        base64 encode characters ref: 0-9, A-Z, a-z, _, -
        """
        data = data or {}
        data.update({'uid': self._uid(user), })
        return signing.dumps(data, salt=__name__).replace(":", ".")

    def is_valid(self, user, signed_value):
        try:
            self.data = signing.loads(signed_value.replace(".", ":"), salt=__name__)
        except signing.BadSignature:
            return False

        if self.data['uid'] != self._uid(user):
            return False

        return True


class UserActivationTokenGenerator(TokenGenerator):

    def _uid(self, user):
        return ";".join((smart_text(user.pk), smart_text(user.is_verified)))


class UserEmailChangeTokenGenerator(TokenGenerator):

    def _uid(self, user):
        return ";".join((smart_text(user.pk), smart_text(user.email)))

    def generate(self, user, new_email):
        return super(UserEmailChangeTokenGenerator, self).generate(user, {'new_email': new_email, })

    def get_email(self):
        return self.data['new_email']
