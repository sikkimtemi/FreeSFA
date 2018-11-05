from django.test import TestCase
from django.core.validators import ValidationError
from .forms import WorkspaceCreateForm, WorkspaceUpdateForm

class WorkspaceCreateFormTests(TestCase):
    
    def test_workspace_create_forms_normal_1(self):
        """
        顧客情報登録フォーム 正常系 1
        """
        # 半角のみ。
        params = dict(
            workspace_name='harfangletest_corp',
        )
        form = WorkspaceCreateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], 'harfangletest_corp')

    def test_workspace_create_forms_normal_2(self):
        """
        顧客情報登録フォーム 正常系 ２
        """
        # 全角のみ。
        params = dict(
            workspace_name='全角テスト株式会社',
        )
        form = WorkspaceCreateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], '全角テスト株式会社')

    def test_workspace_create_forms_normal_3(self):
        """
        顧客情報登録フォーム 正常系 ３
        """
        # 全角半角
        params = dict(
            workspace_name='angletest株式会社',
        )
        form = WorkspaceCreateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], 'angletest株式会社')

    def test_workspace_create_forms_normal_4(self):
        """
        顧客情報登録フォーム 正常系 ４
        """
        # 全角半角、数字、記号
        params = dict(
            workspace_name='テスト（test0123@dummy.jp）',
        )
        form = WorkspaceCreateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], 'テスト（test0123@dummy.jp）')

    def test_workspace_create_forms_abnormal_1(self):
        """
        顧客情報登録フォーム 異常系 １
        """
        # 入力無し　許可しない
        params = dict(
            workspace_name='',
        )
        form = WorkspaceCreateForm(params)
        
        self.assertFalse(form.is_valid())


class WorkspaceUpdateFormTests(TestCase):
    
    def test_workspace_update_forms_normal_1(self):
        """
        顧客情報更新フォーム 正常系 1
        """
        # 半角のみ。
        params = dict(
            workspace_name='harfangletest_corp',
        )
        form = WorkspaceUpdateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], 'harfangletest_corp')

    def test_workspace_update_forms_normal_2(self):
        """
        顧客情報更新フォーム 正常系 ２
        """
        # 全角のみ。
        params = dict(
            workspace_name='全角テスト株式会社',
        )
        form = WorkspaceUpdateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], '全角テスト株式会社')

    def test_workspace_update_forms_normal_3(self):
        """
        顧客情報更新フォーム 正常系 ３
        """
        # 全角半角
        params = dict(
            workspace_name='angletest株式会社',
        )
        form = WorkspaceUpdateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], 'angletest株式会社')

    def test_workspace_update_forms_normal_4(self):
        """
        顧客情報更新フォーム 正常系 ４
        """
        # 全角半角、数字、記号
        params = dict(
            workspace_name='テスト（test0123@dummy.jp）',
        )
        form = WorkspaceUpdateForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['workspace_name'], 'テスト（test0123@dummy.jp）')

    def test_workspace_update_forms_abnormal_1(self):
        """
        顧客情報更新フォーム 異常系 １
        """
        # 入力無し　許可しない
        params = dict(
            workspace_name='',
        )
        form = WorkspaceUpdateForm(params)
        
        self.assertFalse(form.is_valid())


