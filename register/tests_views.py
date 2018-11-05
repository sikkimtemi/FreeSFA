from django.test import TestCase
#from django.contrib.auth.models import AnonymousUser, User
from .models import User, Workspace
from django.test import RequestFactory
from .views import WorkspaceCreateView, WorkspaceUpdateView
from django.urls import reverse
from faker import Faker
fake = Faker('ja_JP')
fake_company = fake.company()


class WorkspaceCreateViewTests(TestCase):
    def setUp(self):

        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email=fake.email(), password=fake.password)
            
    def test_workspace_create_view_normal_1(self):
        """
        ワークスペース情報新規登録 正常系 1
        """
        request = self.factory.get('/register/workspace_create/')
        request.user = self.user
        
        request.GET = request.GET.copy()
        request.GET['workspace_name'] = fake_company

        session = self.client.session
        request.session = session
        request.session['query'] = request.GET
        
        response = WorkspaceCreateView.as_view()(request)
        
        self.assertEquals(request.GET['workspace_name'],fake_company)
        self.assertEquals(200, response.status_code)

