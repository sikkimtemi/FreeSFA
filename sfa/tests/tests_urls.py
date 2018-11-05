from django.test import TestCase
from django.urls import resolve
from sfa.views import WelcomeView, CustomerInfoFilterView, CustomerInfoDetailView, CustomerInfoCreateView, CustomerInfoUpdateView, CustomerInfoDeleteView

class UrlsTests(TestCase):
    
    def test_index(self):
        """
        /でWelcomeViewが呼び出されることを確認
        """
        reverse_match = resolve('/')
        self.assertEqual(reverse_match.func.__name__, WelcomeView.as_view().__name__)

    def test_detail(self):
        """
        /detail/1/でCustomerInfoDetailViewが呼び出されることを確認
        """
        reverse_match = resolve('/detail/1/')
        self.assertEqual(reverse_match.func.__name__, CustomerInfoDetailView.as_view().__name__)

    def test_create(self):
        """
        /create/でCustomerInfoCreateViewが呼び出されることを確認
        """
        reverse_match = resolve('/create/')
        self.assertEqual(reverse_match.func.__name__, CustomerInfoCreateView.as_view().__name__)

    def test_update(self):
        """
        /update/1/でCustomerInfoUpdateViewが呼び出されることを確認
        """
        reverse_match = resolve('/update/1/')
        self.assertEqual(reverse_match.func.__name__, CustomerInfoUpdateView.as_view().__name__)

    def test_delete(self):
        """
        /delete/1/でCustomerInfoDeleteViewが呼び出されることを確認
        """
        reverse_match = resolve('/delete/1/')
        self.assertEqual(reverse_match.func.__name__, CustomerInfoDeleteView.as_view().__name__)
