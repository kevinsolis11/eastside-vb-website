from django.test import TestCase, Client
from django.utils import timezone
from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import timedelta

from team.models import AccessCode


class AccessCodeTests(TestCase):

    def test_signup_rejects_expired_code(self):
        ac = AccessCode.objects.create(code='PLR-EXPIRED', role=AccessCode.ROLE_PLAYER,
                                       expires_at=timezone.now() - timedelta(days=1))
        resp = self.client.post(reverse('signup'), {
            'username': 'u1', 'email': 'u1@example.com', 'password1': 'passw0rd', 'password2': 'passw0rd',
            'access_code': 'PLR-EXPIRED'
        })
        # form should not redirect; page reload with errors
        self.assertContains(resp, 'This access code has expired.', status_code=200)

    def test_generate_code_with_email_sends_invite(self):
        staff = User.objects.create_user('staff', 'staff@example.com', 'pw')
        staff.is_staff = True
        staff.save()

        client = Client()
        client.force_login(staff)

        url = reverse('team:coach_codes')
        resp = client.post(url, {'role': AccessCode.ROLE_PLAYER, 'count': 1, 'email': 'player@example.com'})
        # check code created and email sent
        ac = AccessCode.objects.filter(allowed_email='player@example.com').first()
        self.assertIsNotNone(ac)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(ac.code, mail.outbox[0].body)

    def test_cleanup_command_removes_old_used_codes(self):
        old_used = AccessCode.objects.create(code='PLR-OLD', role=AccessCode.ROLE_PLAYER, is_used=True,
                                             created_at=timezone.now() - timedelta(days=90))
        # run management command
        from django.core.management import call_command
        call_command('cleanup_accesscodes', '--days', '30')
        self.assertFalse(AccessCode.objects.filter(code='PLR-OLD').exists())
