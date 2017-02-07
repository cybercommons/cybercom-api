from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User
#from rest_framework import status
from rest_framework.test import APIClient, APITestCase, APIRequestFactory, force_authenticate
from .models import *
from .views import UserProfile


class AuthUserTestCase(TestCase):
    def setUp(self):
        AuthUser.objects.create(password="testingpassword",
                                username="testinguser",
                                first_name="testing",
                                last_name="user",
                                email="testinguser@example.org")

    def test_user_exists(self):
        testuser = AuthUser.objects.get(username="testinguser")
        self.assertEqual(testuser.username, "testinguser")
        self.assertTrue(testuser.is_active)
        self.assertFalse(testuser.is_superuser)
        self.assertFalse(testuser.is_staff)
        self.assertIsNotNone(testuser.date_joined)
        self.assertIsNone(testuser.last_login)  # no prior login

    def test_creat_new_user_with_existing_username(self):
        options = {"password": "anotherpassword",
                   "username": "testinguser",  # This is the same username as created in setUp()
                   "first_name": "John",
                   "last_name": "Smith",
                   "email": "jsmith@example.org"}
        with self.assertRaises(IntegrityError):
            AuthUser.objects.create(**options)


class APIAccountTestCase(APITestCase):
    def setUp(self):
        User(username="admin", is_staff=True, is_superuser=True, is_active=True).save()  # create admin user
        User(username="staff", is_staff=True, is_superuser=False, is_active=True).save()  # create staff user
        User(username="user", is_staff=False, is_superuser=False, is_active=True).save()  # create non-privileged user
        User(username="inactiveadmin", is_staff=True, is_superuser=True, is_active=False).save()  # create inactive admin user
        User(username="inactivestaff", is_staff=True, is_superuser=False, is_active=False).save()  # create inactive staff user
        User(username="inactiveuser", is_staff=False, is_superuser=False, is_active=False).save()  # create inactive non-privileged user

    def test_account_existance(self):
        self.assertIsNotNone(User.objects.get(username="admin").pk)
        self.assertIsNotNone(User.objects.get(username="staff").pk)
        self.assertIsNotNone(User.objects.get(username="user").pk)
        self.assertIsNotNone(User.objects.get(username="inactiveadmin").pk)
        self.assertIsNotNone(User.objects.get(username="inactivestaff").pk)
        self.assertIsNotNone(User.objects.get(username="inactiveuser").pk)

        self.assertTrue(User.objects.get(username="admin").is_staff)
        self.assertTrue(User.objects.get(username="admin").is_superuser)
        self.assertTrue(User.objects.get(username="admin").is_active)
        self.assertTrue(User.objects.get(username="inactiveadmin").is_staff)
        self.assertTrue(User.objects.get(username="inactiveadmin").is_superuser)
        self.assertFalse(User.objects.get(username="inactiveadmin").is_active)

        self.assertTrue(User.objects.get(username="staff").is_staff)
        self.assertTrue(User.objects.get(username="staff").is_active)
        self.assertFalse(User.objects.get(username="staff").is_superuser)
        self.assertTrue(User.objects.get(username="inactivestaff").is_staff)
        self.assertFalse(User.objects.get(username="inactivestaff").is_superuser)
        self.assertFalse(User.objects.get(username="inactivestaff").is_active)

        self.assertTrue(User.objects.get(username="user").is_active)
        self.assertFalse(User.objects.get(username="user").is_staff)
        self.assertFalse(User.objects.get(username="user").is_superuser)
        self.assertFalse(User.objects.get(username="inactiveuser").is_staff)
        self.assertFalse(User.objects.get(username="inactiveuser").is_superuser)
        self.assertFalse(User.objects.get(username="inactiveuser").is_active)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="doesnotexist")
            User.objects.get(pk=100)

    def test_create_account_view_from_admin(self):
        """ test view """
        admin = User.objects.get(username='admin')
        data = {"username": "testinguserAPI",
                "password1": "testingpassword",
                "password2": "testingpassword"}
        factory = APIRequestFactory(enforce_csrf_checks=True)
        request = factory.post(reverse('user-list'), format='json', data=data)
        request.user = admin
        force_authenticate(request, user=admin)
        view = UserProfile.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_login_REST_API(self):
        admin = User.objects.get(username='admin')
        admin.password = "testpassword"
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(admin.is_active)
        self.assertTrue(client.login(username='admin', password='testpassword'))

    def test_token_login_REST_API(self):
        pass

    def test_create_account_from_REST_API(self):
        admin = User.objects.get(username='admin')
        data = {"username": "testinguserAPI",
                "password1": "testingpassword",
                "password2": "testingpassword"}
        client = APIClient(enforce_csrf_checks=True)
        client.force_authenticate(user=admin)
        response = client.post('/api/admin/auth/user/add/', format='json', data=data)

        self.assertEqual(response.status_code, 200)
