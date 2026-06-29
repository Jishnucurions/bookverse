from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from books.models import SavedBook

class BooksTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "Secr3tP@ssword!"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_saved_book_model_creation(self):
        book = SavedBook.objects.create(
            user=self.user,
            work_key="OL82586W",
            title="Dune",
            author_name="Frank Herbert",
            cover_id="12345",
            status="to_read"
        )
        self.assertEqual(SavedBook.objects.count(), 1)
        self.assertEqual(book.status, "to_read")
        self.assertEqual(str(book), "Dune - testuser (to_read)")

    def test_home_view(self):
        """Verify home page loads instantly and contains the shelf preview context."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/home.html')
        self.assertIn('shelf_preview', response.context)

    @patch('books.utils.requests.get')
    def test_subject_books_api(self, mock_get):
        """Verify the AJAX API view returns books correctly using mocked requests."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'works': [
                {
                    'key': '/works/OL12345W',
                    'title': 'Test Book SF',
                    'authors': [{'name': 'SF Author'}],
                    'first_publish_year': 2026,
                    'cover_id': 9999
                }
            ]
        }
        # Call the AJAX API
        response = self.client.get(reverse('subject_books_api', args=['science_fiction']))
        self.assertEqual(response.status_code, 200)
        
        # Verify JSON content
        data = response.json()
        self.assertIn('books', data)
        self.assertEqual(len(data['books']), 1)
        self.assertEqual(data['books'][0]['title'], 'Test Book SF')
        self.assertEqual(data['books'][0]['key'], 'OL12345W')

    @patch('books.utils.requests.get')
    def test_search_view(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'docs': [
                {
                    'key': '/works/OL98765W',
                    'title': 'Searched Book',
                    'author_name': ['Search Author'],
                    'first_publish_year': 1999,
                    'cover_i': 1234
                }
            ]
        }
        response = self.client.get(reverse('search') + '?q=test')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/search.html')
        self.assertIn('results', response.context)
        self.assertEqual(len(response.context['results']), 1)
        self.assertEqual(response.context['results'][0]['title'], 'Searched Book')

    def test_toggle_save_book(self):
        post_data = {
            'work_key': 'OL11111W',
            'title': 'Toggle Book',
            'author_name': 'Toggle Author',
            'cover_id': '111'
        }
        response = self.client.post(reverse('toggle_save_book'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SavedBook.objects.filter(work_key='OL11111W', user=self.user).exists())

        response = self.client.post(reverse('toggle_save_book'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SavedBook.objects.filter(work_key='OL11111W', user=self.user).exists())

    def test_update_book_status(self):
        book = SavedBook.objects.create(
            user=self.user,
            work_key="OL22222W",
            title="Status Book",
            author_name="Status Author",
            status="to_read"
        )
        post_data = {
            'status': 'reading'
        }
        response = self.client.post(reverse('update_book_status', args=[book.id]), post_data)
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.status, "reading")
