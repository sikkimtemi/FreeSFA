from django.urls import path
from . import views

app_name = 'register'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path(
        'user_create/done/',
        views.UserCreateDone.as_view(),
        name='user_create_done'),
    path(
        'user_create/complete/<token>/',
        views.UserCreateComplete.as_view(),
        name='user_create_complete'),
    path(
        'user_detail/<int:pk>/',
        views.UserDetail.as_view(),
        name='user_detail'),
    path(
        'user_update/<int:pk>/',
        views.UserUpdate.as_view(),
        name='user_update'),
    path(
        'password_change/',
        views.PasswordChange.as_view(),
        name='password_change'),
    path(
        'password_change/done/',
        views.PasswordChangeDone.as_view(),
        name='password_change_done'),
    path(
        'password_reset/',
        views.PasswordReset.as_view(),
        name='password_reset'),
    path(
        'password_reset/done/',
        views.PasswordResetDone.as_view(),
        name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        views.PasswordResetConfirm.as_view(),
        name='password_reset_confirm'),
    path(
        'reset/done/',
        views.PasswordResetComplete.as_view(),
        name='password_reset_complete'),
    path(
        'workspace_create/',
        views.WorkspaceCreateView.as_view(),
        name='workspace_create'),
    path(
        'workspace_join/<int:pk>/',
        views.WorkspaceJoinView.as_view(),
        name='workspace_join'),
    path(
        'workspace_join/done/',
        views.WorkspaceJoinDoneView.as_view(),
        name='workspace_join_done'),
    path(
        'workspace_join_accept/<int:pk>/',
        views.WorkspaceJoinAcceptView.as_view(),
        name='workspace_join_accept'),
    path(
        'workspace_join_reject/<int:pk>/',
        views.WorkspaceJoinRejectView.as_view(),
        name='workspace_join_reject'),
    path(
        'workspace_update/<int:pk>/',
        views.WorkspaceUpdateView.as_view(),
        name='workspace_update'),
    path(
        'mygroup_create/',
        views.MyGroupCreateView.as_view(),
        name='mygroup_create'),
    path(
        'mygroup_update/<int:pk>/',
        views.MyGroupUpdateView.as_view(),
        name='mygroup_update'),
    path(
        'mygroup_list/', views.MyGroupListView.as_view(), name='mygroup_list'),
    path('user_list/', views.UserListView.as_view(), name='user_list'),
    path(
        'user_role_update/<int:pk>/',
        views.UserRoleUpdateView.as_view(),
        name='user_role_update'),
    path(
        'user_release_from_workspace/<int:pk>/',
        views.UserReleaseFromWorkspaceView.as_view(),
        name='user_release_from_workspace'),
    path('user_invite/', views.UserInviteView.as_view(), name='user_invite'),
    path(
        'user_invite_confirm/<token>/',
        views.UserInviteConfirmView.as_view(),
        name='user_invite_confirm'),
]
