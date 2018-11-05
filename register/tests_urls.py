from django.test import TestCase
from django.urls import resolve
from . import views

class UrlsTests(TestCase):
    
    def test_url_access(self):
        """
        urlsに登録されている画面が想定通り呼び出されることを確認
        """
        reverse_match = resolve('/register/workspace_create/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceCreateView.as_view().__name__)

        reverse_match = resolve('/register/workspace_update/1/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceUpdateView.as_view().__name__)


        reverse_match = resolve('/register/login/')
        self.assertEqual(reverse_match.func.__name__, views.Login.as_view().__name__)
        
        
        reverse_match = resolve('/register/logout/')
        self.assertEqual(reverse_match.func.__name__, views.Logout.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_create/')
        self.assertEqual(reverse_match.func.__name__, views.UserCreate.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_create/done/')
        self.assertEqual(reverse_match.func.__name__, views.UserCreateDone.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_create/complete/1/')
        self.assertEqual(reverse_match.func.__name__, views.UserCreateComplete.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_detail/1/')
        self.assertEqual(reverse_match.func.__name__, views.UserDetail.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_update/1/')
        self.assertEqual(reverse_match.func.__name__, views.UserUpdate.as_view().__name__)
        
        
        reverse_match = resolve('/register/password_change/')
        self.assertEqual(reverse_match.func.__name__, views.PasswordChange.as_view().__name__)
        
        
        reverse_match = resolve('/register/password_change/done/')
        self.assertEqual(reverse_match.func.__name__, views.PasswordChangeDone.as_view().__name__)
        
        
        reverse_match = resolve('/register/password_reset/')
        self.assertEqual(reverse_match.func.__name__, views.PasswordReset.as_view().__name__)
        
        
        reverse_match = resolve('/register/password_reset/done/')
        self.assertEqual(reverse_match.func.__name__, views.PasswordResetDone.as_view().__name__)
        
        
        reverse_match = resolve('/register/reset/1/1/')
        self.assertEqual(reverse_match.func.__name__, views.PasswordResetConfirm.as_view().__name__)
        
        
        reverse_match = resolve('/register/reset/done/')
        self.assertEqual(reverse_match.func.__name__, views.PasswordResetComplete.as_view().__name__)
        
        
        reverse_match = resolve('/register/workspace_create/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceCreateView.as_view().__name__)
        
        
        reverse_match = resolve('/register/workspace_join/1/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceJoinView.as_view().__name__)
        
        
        reverse_match = resolve('/register/workspace_join/done/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceJoinDoneView.as_view().__name__)
        
        
        reverse_match = resolve('/register/workspace_join_accept/1/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceJoinAcceptView.as_view().__name__)
        
        
        reverse_match = resolve('/register/workspace_join_reject/1/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceJoinRejectView.as_view().__name__)
        
        
        reverse_match = resolve('/register/workspace_update/1/')
        self.assertEqual(reverse_match.func.__name__, views.WorkspaceUpdateView.as_view().__name__)
        
        
        reverse_match = resolve('/register/mygroup_create/')
        self.assertEqual(reverse_match.func.__name__, views.MyGroupCreateView.as_view().__name__)
        
        
        reverse_match = resolve('/register/mygroup_update/1/')
        self.assertEqual(reverse_match.func.__name__, views.MyGroupUpdateView.as_view().__name__)
        
        
        reverse_match = resolve('/register/mygroup_list/')
        self.assertEqual(reverse_match.func.__name__, views.MyGroupListView.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_list/')
        self.assertEqual(reverse_match.func.__name__, views.UserListView.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_role_update/1/')
        self.assertEqual(reverse_match.func.__name__, views.UserRoleUpdateView.as_view().__name__)
        
        
        reverse_match = resolve('/register/user_release_from_workspace/1/')
        self.assertEqual(reverse_match.func.__name__, views.UserReleaseFromWorkspaceView.as_view().__name__)
        
        reverse_match = resolve('/register/user_invite/')
        self.assertEqual(reverse_match.func.__name__, views.UserInviteView.as_view().__name__)
        
        reverse_match = resolve('/register/user_invite_confirm/1/')
        self.assertEqual(reverse_match.func.__name__, views.UserInviteConfirmView.as_view().__name__)
        

        