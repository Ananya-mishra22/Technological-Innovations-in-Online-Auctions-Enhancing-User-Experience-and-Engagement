# tokens.py

from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils import six  # For Django versions < 3.0, remove if using Django 3+

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )

email_verification_token = EmailVerificationTokenGenerator()
