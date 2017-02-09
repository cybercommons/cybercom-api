from django.test import TestCase, Client
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager

from rest_framework.test import APIClient, APITestCase, APIRequestFactory, force_authenticate
from .models import *
from .views import UserProfile


class AuthUserTestCase(TestCase):
    def setUp(self):
        User(username="admin", is_staff=True, is_superuser=True, is_active=True).save()  # create admin user
        User(username="staff", is_staff=True, is_superuser=False, is_active=True).save()  # create staff user
        User(username="user", is_staff=False, is_superuser=False, is_active=True).save()  # create non-privileged user
        User(username="inactiveadmin", is_staff=True, is_superuser=True, is_active=False).save()  # create inactive admin user
        User(username="inactivestaff", is_staff=True, is_superuser=False, is_active=False).save()  # create inactive staff user
        User(username="inactiveuser", is_staff=False, is_superuser=False, is_active=False).save()  # create inactive non-privileged user

        for user in User.objects.all():
            user.set_password('password')
            user.save()

    def test_user_exists(self):
        admin = AuthUser.objects.get(username="admin")
        staff = AuthUser.objects.get(username="staff")
        user = AuthUser.objects.get(username="user")
        inactiveadmin = AuthUser.objects.get(username="inactiveadmin")
        inactivestaff = AuthUser.objects.get(username="inactivestaff")
        inactiveuser = AuthUser.objects.get(username="inactiveuser")

        # Confirm correct assignment
        self.assertEqual(admin.username, "admin")
        self.assertEqual(staff.username, "staff")
        self.assertEqual(user.username, "user")
        self.assertEqual(inactiveadmin.username, "inactiveadmin")
        self.assertEqual(inactivestaff.username, "inactivestaff")
        self.assertEqual(inactiveuser.username, "inactiveuser")

        # Assert True statements
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
        self.assertTrue(inactiveadmin.is_staff)
        self.assertTrue(inactiveadmin.is_superuser)
        self.assertTrue(staff.is_staff)
        self.assertTrue(staff.is_active)
        self.assertTrue(inactivestaff.is_staff)
        self.assertTrue(user.is_active)

        # Assert False statements
        self.assertFalse(inactiveadmin.is_active)
        self.assertFalse(staff.is_superuser)
        self.assertFalse(inactivestaff.is_superuser)
        self.assertFalse(inactivestaff.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(inactiveuser.is_staff)
        self.assertFalse(inactiveuser.is_superuser)
        self.assertFalse(inactiveuser.is_active)

        # Accounts have associated primary key
        self.assertIsNotNone(admin.pk)
        self.assertIsNotNone(staff.pk)
        self.assertIsNotNone(user.pk)
        self.assertIsNotNone(inactiveadmin.pk)
        self.assertIsNotNone(inactivestaff.pk)
        self.assertIsNotNone(inactiveuser.pk)

        # No prior logins
        self.assertIsNone(admin.last_login)
        self.assertIsNone(staff.last_login)
        self.assertIsNone(user.last_login)
        self.assertIsNone(inactiveadmin.last_login)
        self.assertIsNone(inactivestaff.last_login)
        self.assertIsNone(inactiveuser.last_login)

    def test_creat_new_user_with_existing_username(self):
        options = {"username": "admin",  # This is the same username as created in setUp()
                   "first_name": "John",
                   "last_name": "Smith",
                   "email": "admin@example.org"}
        with self.assertRaises(IntegrityError):
            AuthUser.objects.create(**options)

    def test_login(self):
        admin = User.objects.get(username="admin")

        # password is set and not stored in clear text
        self.assertIsNotNone(admin.password)
        self.assertNotEqual(admin.password, "password")

        csrf_client = APIClient(enforce_csrf_checks=True)

        # login with incorrect password
        self.assertFalse(csrf_client.login(username='admin', password='wrongpassword'))

        # login with correct password
        self.assertTrue(csrf_client.login(username='admin', password='password'))
        csrf_client.logout()
