from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, email, timestamp):
        return (six.text_type(email))


account_activation_token = TokenGenerator()
