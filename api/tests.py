from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from .models import *

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
        self.assertRaises(IntegrityError, AuthUser.objects.create, **options)

class APIAccountTestCase(APITestCase):
    def test_create_account(self):
