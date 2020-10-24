# -*- coding: utf-8 -*-

from django.core import signing
from django.utils.encoding import smart_str


class TokenGenerator:
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
        data.update({'uid': self._uid(user)})
        return signing.dumps(data, salt=__name__).replace(":", ".")

    def _load(self, signed_value):
        return signing.loads(signed_value.replace(".", ":"), salt=__name__)

    def is_valid(self, user, signed_value):
        try:
            self.data = self._load(signed_value)
        except signing.BadSignature:
            return False
        if 'uid' not in self.data:
            return False
        if self.data['uid'] != self._uid(user):
            return False
        return True


class UserActivationTokenGenerator(TokenGenerator):
    def _uid(self, user):
        return ";".join((smart_str(user.pk), smart_str(user.st.is_verified)))


class UserEmailChangeTokenGenerator(TokenGenerator):
    def _uid(self, user):
        return ";".join((smart_str(user.pk), smart_str(user.email)))

    def generate(self, user, new_email):
        return super().generate(user, {'new_email': new_email})

    def get_email(self):
        return self.data['new_email']


class UserUnsubTokenGenerator(TokenGenerator):
    def _uid(self, user_id):
        return smart_str(user_id)


def unsub_token(user_id):
    return UserUnsubTokenGenerator().generate(user_id)
