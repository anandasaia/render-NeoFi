from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Note, Share, NoteHistory
from rest_framework.authtoken.models import Token

# Create your tests here.


class NoteOperationsTests_Basic(APITestCase):
    # Test Create Note

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_create_note(self):
        url = reverse("create-note")
        data = {"title": "Test Note", "content": "This is a test note."}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().title, "Test Note")

    # Retrieve, Update and Delete
    def test_retrieve_update_delete_note(self):
        note = Note.objects.create(
            owner=self.user, title="Initial Title", content="Initial Content"
        )
        # Retrieve
        url = reverse("get-note", kwargs={"id": note.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Initial Title")
        # Update
        update_data = {"title": "Updated Title", "content": "Updated Content"}
        response = self.client.put(
            reverse("update-note", kwargs={"id": note.id}), update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.title, "Updated Title")
        # Delete
        response = self.client.delete(
            reverse("delete-note", kwargs={"id": note.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)

    def test_share_note(self):
        # Create a user and authenticate
        if not User.objects.filter(username="testuser").exists():
            self.user = User.objects.create_user(
                username="testuser", password="password123"
            )
        else:
            self.user = User.objects.get(username="testuser")

        self.api_authentication()  # Implement this method to authenticate the request

        # Create a note owned by the authenticated user
        note = Note.objects.create(
            owner=self.user, title="Test Note", content="Test content"
        )

        # Create a user to share the note with
        shared_user = User.objects.create_user(
            username="shareduser", password="password123"
        )

        # Attempt to share the note
        url = reverse("share-note")
        data = {"note_id": note.id, "usernames": [shared_user.username]}
        response = self.client.post(url, data, format="json")

        # Check if the note was shared successfully
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, msg=response.data)

    # Note version history

    def test_note_version_history(self):
        note = Note.objects.create(
            owner=self.user, title="Version History Test", content="Initial Content"
        )
        NoteHistory.objects.create(
            note=note, content="First Edit", edited_by=self.user)
        NoteHistory.objects.create(
            note=note, content="Second Edit", edited_by=self.user
        )
        url = reverse("note-history", kwargs={"id": note.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Assuming two edits were made

    # unauthorized access
    def test_unauthorized_access(self):
        self.client.credentials()  # Clear any authentication credentials
        url = reverse("create-note")
        data = {"title": "Unauthorized Test",
                "content": "Should not be created."}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Sharing with non-existent user

    def test_share_note_nonexistent_user(self):
        note = Note.objects.create(
            owner=self.user, title="Non-existent Share Test", content="Content"
        )
        url = reverse("share-note")
        data = {"note_id": note.id, "usernames": ["ghost"]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Share.objects.filter(note=note).exists())


class AuthTests(APITestCase):
    def test_signup_success(self):
        """
        Ensure we can create a new user successfully.
        """
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertEqual(response.data["message"],
                         "User registered successfully")

    def test_signup_with_existing_username(self):
        """
        Ensure user cannot sign up with an already existing username.
        """
        User.objects.create_user(
            username="existinguser",
            password="testpassword123",
            email="user@example.com",
        )
        url = reverse("signup")
        data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "newpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """
        Ensure we can log in with a valid user.
        """
        username = "validuser"
        password = "validpassword123"
        User.objects.create_user(
            username=username, email="valid@example.com", password=password
        )
        url = reverse("login")
        data = {"username": username, "password": password}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("token" in response.data)

    def test_login_invalid_credentials(self):
        """
        Ensure user cannot log in with invalid credentials.
        """
        User.objects.create_user(
            username="user", email="user@example.com", password="correctpassword"
        )
        url = reverse("login")
        data = {"username": "user", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class NoteAPITests_Advanced(APITestCase):
    def setUp(self):
        # Create users for testing
        self.user1 = User.objects.create_user(
            username="user1", password="pass123")
        self.user2 = User.objects.create_user(
            username="user2", password="pass123")
        self.user1_token = Token.objects.create(user=self.user1).key
        self.user2_token = Token.objects.create(user=self.user2).key
        self.note = Note.objects.create(
            owner=self.user1, title="User1's Note", content="Hello World"
        )

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

    # Test Invalid Email Format on Signup

    def test_signup_invalid_email(self):
        url = reverse("signup")
        data = {"username": "user3",
                "email": "invalidemail", "password": "pass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Short password on signup
    def test_signup_short_password(self):
        url = reverse("signup")
        data = {"username": "user3",
                "email": "user3@example.com", "password": "short"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Login with unregistered user
    def test_login_unregistered_user(self):
        url = reverse("login")
        data = {"username": "nobody", "password": "nopass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Create note without authentication
    def test_create_note_without_auth(self):
        url = reverse("create-note")
        data = {"title": "No Auth Note", "content": "Should fail"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Retrieve note by non-owner
    def test_get_note_by_non_owner(self):
        self.api_authentication(self.user2_token)
        url = reverse("get-note", kwargs={"id": self.note.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Update note by non-owner

    def test_update_note_by_non_owner(self):
        self.api_authentication(self.user2_token)
        url = reverse("update-note", kwargs={"id": self.note.id})
        data = {"content": "Unauthorized update attempt"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Delete note by Non-owner

    def test_delete_note_by_non_owner(self):
        self.api_authentication(self.user2_token)
        url = reverse("delete-note", kwargs={"id": self.note.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Sharing note with invalid user
    def test_share_note_with_invalid_user(self):
        self.api_authentication(self.user1_token)
        url = reverse("share-note")
        data = {"note_id": self.note.id, "usernames": ["doesnotexist"]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Accessing version history with non-shared user
    def test_version_history_access_by_non_shared_user(self):
        self.api_authentication(self.user2_token)
        url = reverse("note-history", kwargs={"id": self.note.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_registration_with_existing_username(self):
        User.objects.create_user(
            'existinguser', 'existingemail@example.com', 'password123')
        url = reverse('signup')
        data = {'username': 'existinguser',
                'email': 'newemail@example.com', 'password': 'newpassword123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Username is already taken.', response.data['error'])

    def test_registration_with_existing_email(self):
        User.objects.create_user(
            'newuser', 'existingemail@example.com', 'password123')
        url = reverse('signup')
        data = {'username': 'newuser2',
                'email': 'existingemail@example.com', 'password': 'newpassword123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email is already in use.', response.data['error'])


class NoteAPITests_Advanced1(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', password='testpassword123')
        # Create a token for the test user
        self.token = Token.objects.create(user=self.user)
        # Authenticate the test client with the user's token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # Create a test note owned by the test user
        self.note = Note.objects.create(
            title="Test Note", content="Original Content", owner=self.user)

    def test_note_history(self):
        # Update the note to generate history
        update_data = {'title': 'Updated Test Note',
                       'content': 'Updated Content'}
        self.client.put(
            reverse('update-note', kwargs={'id': self.note.id}), update_data, format='json')

        # Attempt to fetch the note's history
        response = self.client.get(
            reverse('note-history', kwargs={'id': self.note.id}))

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert the history is not empty
        self.assertNotEqual(len(response.data), 0)
        # Assert the content of the history matches the update
        self.assertIn('Updated Content', response.data[0]['content'])
