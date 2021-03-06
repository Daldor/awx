import pytest
import string
import random
import StringIO
from django.contrib.auth.models import User
from django.core.management import call_command
from awx.main.models.oauth import OAuth2AccessToken


@pytest.mark.django_db
@pytest.mark.inventory_import
class TestOAuth2CreateCommand:
    def test_no_user_option(self):
        out = StringIO.StringIO()
        call_command('create_oauth2_token', stdout=out)
        assert 'Username not supplied.' in out.getvalue()
        out.close()

    def test_non_existing_user(self):
        out = StringIO.StringIO()
        fake_username = ''
        while fake_username == '' or User.objects.filter(username=fake_username).exists():
            fake_username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        arg = '--user=' + fake_username
        call_command('create_oauth2_token', arg, stdout=out)
        assert 'The user does not exist.' == out.getvalue().strip()
        out.close()

    def test_correct_user(self, alice):
        out = StringIO.StringIO()
        arg = '--user=' + 'alice'
        call_command('create_oauth2_token', arg, stdout=out)
        generated_token = out.getvalue().strip()
        assert OAuth2AccessToken.objects.filter(user=alice, token=generated_token).count() == 1
        assert OAuth2AccessToken.objects.get(user=alice, token=generated_token).scope == 'write'
        out.close()
