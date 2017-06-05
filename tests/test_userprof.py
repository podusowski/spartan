from tests.utils import ClientTestCase
from training import models


class UserProfileTestCase(ClientTestCase):
    def test_user_profile(self):
        with self.assertRaises(Exception):
            self.user.userprofile

        # page is accessible without post data
        self.get('/user_profile')

    def test_saving_timezone(self):
        self.post('/user_profile', {'timezone': 'Europe/Warsaw'})
        profile = models.UserProfile.objects.get(user=self.user)
        self.assertEqual('Europe/Warsaw', profile.timezone)

        self.post('/user_profile', {'timezone': 'Europe/Lisbon'})
        profile = models.UserProfile.objects.get(user=self.user)
        self.assertEqual('Europe/Lisbon', profile.timezone)

        form = self.get('/user_profile').context['form']
        self.assertEqual('Europe/Lisbon', form.initial['timezone'])

    def test_saving_invalid_timezone_falls_back_to_utc(self):
        self.post('/user_profile', {'timezone': 'invalid'})
        profile = models.UserProfile.objects.get(user=self.user)
        self.assertEqual('UTC', profile.timezone)

        form = self.get('/user_profile').context['form']
        self.assertEqual('UTC', form.initial['timezone'])
