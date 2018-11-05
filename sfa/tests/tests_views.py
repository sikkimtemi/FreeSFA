from django.test import RequestFactory
from django.test import TestCase
from django.urls import resolve
from faker import Faker
from register.models import User, Workspace
from sfa.models import CustomerInfo
from sfa.views import CustomerInfoFilterView, CustomerInfoCreateView

class CustomerInfoFilterViewTests(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        fake = Faker('ja_JP')
        self.factory = RequestFactory()
        self.workspace = Workspace.objects.create(workspace_name=fake.company())
        self.user = User.objects.create_user(
            email=fake.email(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            workspace = self.workspace,
            is_workspace_active = True,
        )
            
    def test_customerinfo_filter_view_normal_1(self):
        """
        顧客情報一覧検索フォーム 正常系 1
        """
        # 半角のみ。
        request = self.factory.get('customer_list_user/')
        request.user = self.user
        
        request.GET = request.GET.copy()
        request.GET['corporate_number'] = '1234567890123'
        request.GET['tel_number1'] = '099-123-4567'
        request.GET['tel_number2'] = '(03)1234-5678'
        request.GET['tel_number3'] = '0120-123-456'
        request.GET['fax_number'] = '(099)123-4567'
        request.GET['zip_code'] = '123-4567'

        session = self.client.session
        request.session = session
        request.session['query'] = request.GET
        
        response = CustomerInfoFilterView.as_view()(request)
        
        self.assertEquals('1234567890123', request.GET['corporate_number'])
        self.assertEquals('0991234567', request.GET['tel_number1'])
        self.assertEquals('0312345678', request.GET['tel_number2'])
        self.assertEquals('0120123456', request.GET['tel_number3'])
        self.assertEquals('0991234567', request.GET['fax_number'])
        self.assertEquals('1234567', request.GET['zip_code'])
        self.assertEquals(200, response.status_code)


    def test_customerinfo_filter_view_normal_2(self):
        """
        顧客情報一覧検索フォーム 正常系 2
        """
        # 全角混在。
        request = self.factory.get('customer_list_user/')
        request.user = self.user
        
        request.GET = request.GET.copy()
        request.GET['corporate_number'] = '12３４567890123'
        request.GET['tel_number1'] = '099-１２３-4567'
        request.GET['tel_number2'] = '(03)1234-5６７８'
        request.GET['tel_number3'] = '０１２０-123-456'
        request.GET['fax_number'] = '（０９９）123-4567'
        request.GET['zip_code'] = '123−４567'

        session = self.client.session
        request.session = session
        request.session['query'] = request.GET
        
        response = CustomerInfoFilterView.as_view()(request)
        
        self.assertEquals('1234567890123', request.GET['corporate_number'])
        self.assertEquals('0991234567', request.GET['tel_number1'])
        self.assertEquals('0312345678', request.GET['tel_number2'])
        self.assertEquals('0120123456', request.GET['tel_number3'])
        self.assertEquals('0991234567', request.GET['fax_number'])
        self.assertEquals('1234567', request.GET['zip_code'])
        self.assertEquals(200, response.status_code)

    def test_customerinfo_filter_view_normal_3(self):
        """
        顧客情報一覧検索フォーム 正常系 3
        """
        # すべて省略
        request = self.factory.get('/')
        request.user = self.user
        
        request.GET = request.GET.copy()
        request.GET['corporate_number'] = ''
        request.GET['tel_number1'] = ''
        request.GET['tel_number2'] = ''
        request.GET['tel_number3'] = ''
        request.GET['fax_number'] = ''
        request.GET['zip_code'] = ''

        session = self.client.session
        request.session = session
        request.session['query'] = request.GET
        
        response = CustomerInfoFilterView.as_view()(request)
        
        self.assertEquals('', request.GET['corporate_number'])
        self.assertEquals('', request.GET['tel_number1'])
        self.assertEquals('', request.GET['tel_number2'])
        self.assertEquals('', request.GET['tel_number3'])
        self.assertEquals('', request.GET['fax_number'])
        self.assertEquals('', request.GET['zip_code'])
        self.assertEquals(200, response.status_code)


class CommonRedirectTests(TestCase):
    """
    ワークスペースに所属していないユーザーがアクセスしたらindexへリダイレクトされることをまとめて確認
    """
    def setUp(self):
        # Every test needs access to the request factory.
        fake = Faker('ja_JP')
        self.factory = RequestFactory()
        self.workspace = Workspace.objects.create(workspace_name=fake.company())
        # ワークスペースに所属しているが、仮登録中のユーザー
        self.nonactive_user = User.objects.create_user(
            email=fake.email(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            workspace = self.workspace,
            is_workspace_active = False,
            workspace_role = '0',
        )
        # ワークスペースに所属し、有効になっているユーザー（権限はオーナー）
        self.active_user = User.objects.create_user(
            email=fake.email(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            workspace = self.workspace,
            is_workspace_active = True,
            workspace_role = '2',
        )

    def test_redirect(self):
        """
        ログインユーザーがワークスペースに所属しているが、仮登録中の場合はindexへリダイレクトされることを確認
        """
        # 検証対象のURL（特殊な前提条件が必要なものはコメントアウト）
        target_urls = [
            '/dashboard/',
            '/customer_list_user/',
            '/customer_list_user_map/',
            '/customer_list_group/',
            '/customer_list_group_map/',
            '/customer_list_all/',
            '/customer_list_all_map/',
            '/customer_area_search/',
            '/detail/1/',
            '/create/',
            '/update/1/',
            '/delete/1/',
            '/customer_info_import/',
            '/contact_create/',
            '/contact_from_customer_create/1/',
            '/visit_plan_from_customer_create/1/',
            '/visit_history_from_customer_create/1/',
            #'/contact_update/1/',
            #'/contact_from_customer_update/1/',
            #'/contact_by_customer_delete/1/',
            #'/contact_by_user_delete/1/',
            '/contact_detail/1/',
            #'/contactinfo_by_customer_list/1/',
            #'/contactinfo_by_user_list/1/',
            '/address_info_create/',
            '/address_info_update/1/',
            '/address_info_bulk_update/',
            '/address_info_list/',
            '/address_info_detail/1/',
            '/address_info_delete/1/',
            '/address_info_import/',
            '/visit_target_filter/',
            '/visit_target_map/',
            '/visit_plan_create/',
            #'/visit_plan_update/1/',
            '/visit_history_create/',
            #'/visit_history_update/1/',
            #'/visit_plan_or_history_delete/1/',
            '/call_history_create/1/',
            '/call_history_filter/',
            #'/call_history_update/1/',
            '/get_contactinfo_count/',
            '/goal_setting_create/',
            '/goal_setting_update/1/',
            '/workspace_environment_setting_create/',
            '/workspace_environment_setting_update/1/',
        ]
        
        for target_url in target_urls:
            #print("Testing: ", target_url)
            request = self.factory.get(target_url)
            request.user = self.nonactive_user
            reverse_match = resolve(target_url)
            response = reverse_match.func(request)
            
            self.assertEquals(response['Location'], '/')
            self.assertEquals(response.status_code, 302)

    def test_accept(self):
        """
        ログインユーザーがワークスペースに所属し、有効になっている場合はリダイレクトしないことを確認
        """
        # 検証対象のURL（特殊な前提条件が必要なものはコメントアウト）
        target_urls = [
            '/dashboard/',
            #'/customer_list_user/',
            #'/customer_list_user_map/',
            #'/customer_list_group/',
            #'/customer_list_group_map/',
            #'/customer_list_all/',
            #'/customer_list_all_map/',
            #'/customer_area_search/',
            #'/detail/1/',
            '/create/',
            #'/update/1/',
            #'/delete/1/',
            '/customer_info_import/',
            '/contact_create/',
            #'/contact_from_customer_create/1/',
            #'/visit_plan_from_customer_create/1/',
            #'/visit_history_from_customer_create/1/',
            #'/contact_update/1/',
            #'/contact_from_customer_update/1/',
            #'/contact_by_customer_delete/1/',
            #'/contact_by_user_delete/1/',
            #'/contact_detail/1/',
            #'/contactinfo_by_customer_list/1/',
            #'/contactinfo_by_user_list/1/',
            '/address_info_create/',
            #'/address_info_update/1/',
            #'/address_info_bulk_update/',
            '/address_info_list/',
            #'/address_info_detail/1/',
            #'/address_info_delete/1/',
            '/address_info_import/',
            #'/visit_target_filter/',
            #'/visit_target_map/',
            #'/visit_plan_create/',
            #'/visit_plan_update/1/',
            #'/visit_history_create/',
            #'/visit_history_update/1/',
            #'/visit_plan_or_history_delete/1/',
            #'/call_history_create/1/',
            #'/call_history_filter/',
            #'/call_history_update/1/',
            #'/get_contactinfo_count/',
            '/goal_setting_create/',
            #'/goal_setting_update/1/',
            '/workspace_environment_setting_create/',
            #'/workspace_environment_setting_update/1/',
        ]
        
        for target_url in target_urls:
            #print("Testing: ", target_url)
            request = self.factory.get(target_url)
            request.user = self.active_user
            reverse_match = resolve(target_url)
            response = reverse_match.func(request)
            
            self.assertEquals(response.status_code, 200)
