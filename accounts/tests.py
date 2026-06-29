from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "Secr3tP@ssword!"
        self.email = "testuser@example.com"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )

    def test_profile_creation_signal(self):
        profile = Profile.objects.filter(user=self.user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, "")

    def test_signup_view_get(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_signup_view_post_success(self):
        signup_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Password987!',
            'password2': 'Password987!'
        }
        response = self.client.post(reverse('signup'), signup_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signin_view_post_success(self):
        login_data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(reverse('signin'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_signin_view_post_invalid(self):
        login_data = {
            'username': self.username,
            'password': 'WrongPassword!'
        }
        response = self.client.post(reverse('signin'), login_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signin.html')

    def test_profile_settings_view_requires_login(self):
        response = self.client.get(reverse('profile_settings'))
        self.assertEqual(response.status_code, 302)

    def test_profile_settings_view_get(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('profile_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_settings.html')
        self.assertIn('u_form', response.context)
        self.assertIn('p_form', response.context)
