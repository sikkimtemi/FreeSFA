from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from pure_pagination.mixins import PaginationMixin
from .forms import (
    LoginForm,
    UserCreateForm,
    UserUpdateForm,
    MyPasswordChangeForm,
    MyPasswordResetForm,
    MySetPasswordForm,
    WorkspaceCreateForm,
    WorkspaceJoinForm,
    WorkspaceUpdateForm,
    MyGroupCreateForm,
    MyGroupUpdateForm,
    UserRoleUpdateForm,
    UserInviteForm,
    UserInviteConfirmForm,
)
from .models import MyGroup, Workspace
import json
import requests

User = get_user_model()


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'register/login.html'


class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'register/login.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def dispatch(self, request, *args, **kwargs):
        # settings.pyのREGISTER_NEW_USER_FLGがTrueでなければ新規登録はできない
        if not settings.REGISTER_NEW_USER_FLG:
            return redirect('index')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        reCAPCHAのサイトキーをsetting.pyから取得してコンテキストにセットする
        """
        ctx = super().get_context_data(**kwargs)
        ctx['site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
        return ctx

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # reCAPCHAで不正利用を弾く
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify?secret=' + settings.GOOGLE_RECAPTCHA_SECRET_KEY + '&response=' + recaptcha_response
        response = requests.get(url)
        result = response.json()
        if not result['success']:
            form.add_error(None, '「私はロボットではありません」にチェックを入れてください')
            return self.form_invalid(form)

        # 仮登録と本登録の切り替えは、is_active属性を使う
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk, salt=getattr(settings, 'HASH_SALT')),
            'user': user,
        }

        subject_template = get_template(
            'register/mail_template/create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template(
            'register/mail_template/create/message.txt')
        message = message_template.render(context)

        from_email = settings.EMAIL_HOST_USER
        user.email_user(subject, message, from_email)
        return redirect('register:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録完了画面"""
    template_name = 'register/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS',
                              60 * 60 * 24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(
                token,
                max_age=self.timeout_seconds,
                salt=getattr(settings, 'HASH_SALT'))

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDelete(OnlyYouMixin, generic.TemplateView):
    """ユーザーの削除（実際には無効化）"""

    def get(self, request, **kwargs):
        """ユーザーの無効化"""
        user = User.objects.get(pk=kwargs['pk'])
        user.is_active = False
        user.save()
        return redirect('register:logout')


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザーの詳細ページ"""
    model = User
    template_name = 'register/user_detail.html'


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """ユーザー情報更新ページ"""
    model = User
    form_class = UserUpdateForm
    template_name = 'register/user_form.html'

    def get_success_url(self):
        return resolve_url('register:user_detail', pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        選択可能なグループを同一ワークスペースで絞り込む
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        my_group = form.fields['my_group']
        login_user = self.request.user

        if login_user.workspace:
            my_group.queryset = MyGroup.objects.filter(
                workspace=login_user.workspace.pk)
        else:
            # TODO:ワークスペース未設定時の暫定対応
            my_group.queryset = MyGroup.objects.filter(workspace='0')

        return ctx


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('register:password_change_done')
    template_name = 'register/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'register/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'register/mail_template/reset/subject.txt'
    email_template_name = 'register/mail_template/reset/message.txt'
    template_name = 'register/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('register:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'register/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('register:password_reset_complete')
    template_name = 'register/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'register/password_reset_complete.html'


class WorkspaceCreateView(LoginRequiredMixin, CreateView):
    """ワークスペース新規作成ページ"""
    model = Workspace
    form_class = WorkspaceCreateForm
    template_name = 'register/workspace_create.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # 作成者と更新者を入力
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.save()
        # 作成者をワークスペースのオーナーに設定
        self.request.user.workspace = form.instance
        self.request.user.workspace_role = '2'
        self.request.user.is_workspace_active = True
        self.request.user.save()
        return super(WorkspaceCreateView, self).form_valid(form)


class WorkspaceJoinView(OnlyYouMixin, generic.UpdateView):
    """ワークスペース参加申請ページ"""
    model = User
    form_class = WorkspaceJoinForm
    template_name = 'register/workspace_join.html'

    def form_valid(self, form):
        """仮登録と管理者への通知用メールの発行."""
        # formの入力値からワークスペース名を取り出す
        my_workspace_name = form.cleaned_data['workspace_name']
        # 仮登録かつ権限を一般ユーザーで初期化
        user = form.save(commit=False)
        user.workspace = Workspace.objects.filter(
            workspace_name=my_workspace_name)[0]
        user.is_workspace_active = False
        user.workspace_role = '0'
        user.save()

        # メール本文用のパラメータ
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'user': user,
        }

        subject_template = get_template(
            'register/mail_template/join_workspace/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template(
            'register/mail_template/join_workspace/message.txt')
        message = message_template.render(context)

        from_email = settings.EMAIL_HOST_USER
        # 送信先の設定
        recipients = []
        for member in User.objects.filter(workspace__pk=user.workspace.pk):
            if member.workspace_role >= '1':
                recipients.append(member.email)
        user.email_workspace_admin(subject, message, from_email, recipients)
        return redirect('register:workspace_join_done')


class WorkspaceJoinDoneView(generic.TemplateView):
    """ワークスペース仮登録完了画面"""

    template_name = 'register/workspace_join_done.html'


class WorkspaceJoinAcceptView(LoginRequiredMixin, generic.TemplateView):
    """ワークスペース参加承認"""

    def get(self, request, **kwargs):
        target_user = User.objects.get(pk=self.kwargs['pk'])
        login_user = request.user

        # ログインユーザーが本登録状態で、ワークスペース権限が管理者以上、
        # かつ、対象ユーザーとログインユーザーのワークスペースが同一の場合、
        # ワークスペースへの参加をみとめる
        if login_user.is_workspace_active and (
                login_user.workspace_role >=
                '1') and (target_user.workspace == login_user.workspace):
            target_user.is_workspace_active = True
            target_user.save()
            return redirect('register:user_list')
        else:
            return HttpResponseBadRequest()


class WorkspaceJoinRejectView(LoginRequiredMixin, generic.TemplateView):
    """ワークスペース参加否認"""

    def get(self, request, **kwargs):
        target_user = User.objects.get(pk=self.kwargs['pk'])
        login_user = request.user

        # ログインユーザーが本登録状態で、ワークスペース権限が管理者以上、
        # かつ、対象ユーザーとログインユーザーのワークスペースが同一の場合、
        # ワークスペースへの参加を拒否する
        if login_user.is_workspace_active and (
                login_user.workspace_role >=
                '1') and (target_user.workspace == login_user.workspace):
            target_user.workspace = None
            target_user.save()
            return redirect('register:user_list')
        else:
            return HttpResponseBadRequest()


class UserInviteView(LoginRequiredMixin, generic.CreateView):
    """ユーザー招待用ページ"""
    model = User
    form_class = UserInviteForm
    template_name = 'register/workspace_invite.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースへの招待は、管理者以上の場合のみ処理できる
        if request.user.workspace_role < '1':
            return redirect('index')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        reCAPCHAのサイトキーをsetting.pyから取得してコンテキストにセットする
        """
        ctx = super().get_context_data(**kwargs)
        ctx['site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
        return ctx

    def form_valid(self, form):
        """ワークスペースへの招待メール発行"""
        # reCAPCHAで不正利用を弾く
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify?secret=' + settings.GOOGLE_RECAPTCHA_SECRET_KEY + '&response=' + recaptcha_response
        response = requests.get(url)
        result = response.json()
        if not result['success']:
            form.add_error(None, '「私はロボットではありません」にチェックを入れてください')
            return self.form_invalid(form)

        # ユーザーを仮登録して招待メールを送信する
        user = form.save(commit=False)
        user.is_active = False
        user.workspace = self.request.user.workspace
        user.workspace_role = '0'
        user.is_workspace_active = True
        user.save()

        # メール本文用のパラメータ
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk, salt=getattr(settings, 'HASH_SALT')),
            'user': user,
            'host_user': self.request.user,
        }

        subject_template = get_template(
            'register/mail_template/invite/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template(
            'register/mail_template/invite/message.txt')
        message = message_template.render(context)

        from_email = settings.EMAIL_HOST_USER
        user.email_user(subject, message, from_email)
        return redirect('register:user_list')


class WorkspaceUpdateView(LoginRequiredMixin, UpdateView):
    """ 更新画面（ワークスペース情報） """

    model = Workspace
    form_class = WorkspaceUpdateForm
    success_url = reverse_lazy('index')
    template_name = 'register/workspace_update.html'

    def form_valid(self, form):
        # 更新者を入力
        form.instance.updated_by = self.request.user
        form.save()
        return super(WorkspaceUpdateView, self).form_valid(form)

    # ワークスペース名の更新は、オーナーのみ処理できる
    def get_queryset(self):
        login_user = self.request.user
        if login_user.workspace_role == '2':
            return super().get_queryset()
        else:
            return Workspace.objects.none()


class MyGroupCreateView(LoginRequiredMixin, CreateView):
    """ 登録画面（グループ情報） """

    model = MyGroup
    form_class = MyGroupCreateForm
    success_url = reverse_lazy('register:mygroup_list')
    template_name = 'register/mygroup_create.html'

    def dispatch(self, request, *args, **kwargs):
        # グループ情報登録画面は、ワークスペースに所属している場合のみ表示できる
        if request.user.workspace:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def form_valid(self, form):
        # 作成者と更新者を入力
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.save()
        return super(MyGroupCreateView, self).form_valid(form)

    def post(self, request, **kwargs):
        """
        ワークスペース情報の自動入力
        """
        request.POST = request.POST.copy()
        # ログインユーザー情報の取得
        user = request.user
        # 作成ユーザの所属するワークスペースを登録
        request.POST['workspace'] = user.workspace.pk
        return super().post(request, **kwargs)


class MyGroupUpdateView(LoginRequiredMixin, UpdateView):
    """ 更新画面（グループ情報） """

    model = MyGroup
    form_class = MyGroupUpdateForm
    success_url = reverse_lazy('register:mygroup_list')
    template_name = 'register/mygroup_update.html'

    def form_valid(self, form):
        # 更新者を入力
        form.instance.updated_by = self.request.user
        form.save()
        return super(MyGroupUpdateView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        # グループ情報更新画面は、ワークスペースに所属している場合のみ表示できる
        if request.user.workspace:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class MyGroupListView(PaginationMixin, ListView):
    """ 一覧画面（グループ情報） """

    model = MyGroup
    template_name = 'register/mygroup_list.html'

    # pure_pagination用設定
    paginate_by = 10
    object = MyGroup

    def dispatch(self, request, *args, **kwargs):
        # グループ情報一覧画面は、ワークスペースに所属している場合のみ表示できる
        if request.user.workspace:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        return MyGroup.objects.filter(
            workspace=self.request.user.workspace).order_by('group_name')


class UserListView(PaginationMixin, ListView):
    """ 一覧画面（ユーザー情報） """

    model = User
    template_name = 'register/user_list.html'

    # pure_pagination用設定
    paginate_by = 10
    object = User

    def dispatch(self, request, *args, **kwargs):
        # ユーザ情報一覧画面は、管理者以上の場合のみ表示できる
        if request.user.workspace_role < '1':
            return redirect('index')
        else:
            return super().dispatch(request, *args, **kwargs)

    # 自分のワークスペース権限が管理者以上の場合、同一ワークスペースのユーザーを表示
    def get_queryset(self):
        if self.request.user.workspace_role >= '1':
            return User.objects.filter(workspace=self.request.user.workspace
                                       ).order_by('is_workspace_active')
        else:
            return User.objects.none()


class UserRoleUpdateView(LoginRequiredMixin, UpdateView):
    """ 更新画面（ユーザーのワークスペース権限） """

    model = User
    form_class = UserRoleUpdateForm
    success_url = reverse_lazy('register:user_list')
    template_name = 'register/user_role_update.html'

    # 更新対象が同一ワークスペースで、ワークスペース権限が自分以下の場合のみ表示可能
    def get_queryset(self):
        target_user = User.objects.get(pk=self.kwargs['pk'])
        if (self.request.user.workspace == target_user.workspace) and (
                self.request.user.workspace_role >=
                target_user.workspace_role):
            return super().get_queryset()
        else:
            return User.objects.none()

    def get_context_data(self, **kwargs):
        """
        フォームの選択肢を絞り込む
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        login_user = self.request.user

        # 選択可能なワークスペース権限を自分のワークスペース権限以下で絞り込む
        if login_user.workspace_role == '1':
            form.fields['workspace_role'].choices = [('0', '一般ユーザー'), ('1',
                                                                       '管理者')]

        return ctx


class UserReleaseFromWorkspaceView(LoginRequiredMixin, generic.TemplateView):
    """ ユーザーをワークスペースから解除する """

    def get(self, request, **kwargs):
        target_user = User.objects.get(pk=self.kwargs['pk'])
        login_user = request.user

        # ログインユーザーが本登録状態で、ワークスペース権限が管理者以上、
        # かつ、対象ユーザーとログインユーザーのワークスペースが同一の場合、
        # ワークスペースから対象ユーザーを解除する
        if login_user.is_workspace_active and (
                login_user.workspace_role >=
                '1') and (target_user.workspace == login_user.workspace):
            target_user.workspace = None
            target_user.workspace_role = '0'
            target_user.is_workspace_active = False
            target_user.save()
            return redirect('register:user_list')
        else:
            return HttpResponseBadRequest()


class UserInviteConfirmView(generic.FormView):
    """パスワードを入力してワークスペースへの招待を完了する"""
    form_class = UserInviteConfirmForm
    success_url = reverse_lazy('register:password_reset_complete')
    template_name = 'register/user_form.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS',
                              60 * 60 * 24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(
                token,
                max_age=self.timeout_seconds,
                salt=getattr(settings, 'HASH_SALT'))

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                request.GET = request.GET.copy()
                # 既存の姓名を入力
                request.GET['last_name'] = user.last_name
                request.GET['first_name'] = user.first_name

                return super().get(request, **kwargs)

        return HttpResponseBadRequest()

    def get_initial(self):
        initial = super(UserInviteConfirmView, self).get_initial()
        if self.request.GET:
            initial['last_name'] = self.request.GET['last_name']
            initial['first_name'] = self.request.GET['first_name']
        return initial

    def form_valid(self, form):
        token = self.kwargs.get('token')
        user_pk = loads(
            token,
            max_age=self.timeout_seconds,
            salt=getattr(settings, 'HASH_SALT'))
        user = User.objects.get(pk=user_pk)
        user.last_name = form.cleaned_data['last_name']
        user.first_name = form.cleaned_data['first_name']
        user.set_password(form.cleaned_data['new_password2'])
        if not user.is_active:
            # まだ仮登録なら本登録とする
            user.is_active = True
        user.save()
        return super().form_valid(form)
