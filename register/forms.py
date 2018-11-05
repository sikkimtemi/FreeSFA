from django import forms
from .models import Workspace, MyGroup, User
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       PasswordChangeForm, PasswordResetForm,
                                       SetPasswordForm)
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    """ログイン用フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs[
                'placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


class UserCreateForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('email', )
        else:
            fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    """ユーザー情報更新用フォーム"""

    class Meta:
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('email', 'last_name', 'first_name', 'my_group')
        else:
            fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更用フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordResetForm(PasswordResetForm):
    """パスワードリセット用フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MySetPasswordForm(SetPasswordForm):
    """パスワードリセット後の再設定用フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class WorkspaceCreateForm(forms.ModelForm):
    """ワークスペース登録用フォーム"""

    class Meta:
        model = Workspace
        fields = ('workspace_name', )


class WorkspaceJoinForm(forms.ModelForm):
    """ワークスペース参加申請用フォーム"""

    workspace_name = forms.CharField(label='ワークスペース名', max_length=40)

    class Meta:
        model = User
        fields = ()

    def clean_workspace_name(self):
        my_workspace_name = self.cleaned_data['workspace_name']
        if (not Workspace.objects.filter(workspace_name=my_workspace_name)):
            raise forms.ValidationError('入力されたワークスペースは存在しません。')
        return my_workspace_name


class WorkspaceUpdateForm(forms.ModelForm):
    """ワークスペース情報更新用フォーム"""

    class Meta:
        model = Workspace
        fields = ('workspace_name', )


class MyGroupCreateForm(forms.ModelForm):
    """グループ情報登録用フォーム"""

    class Meta:
        model = MyGroup
        fields = ('group_name', )

    workspace = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['workspace'] = [
                t.pk for t in kwargs['instance'].workspace_set.all()
            ]
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        forms.ModelForm.__init__(self, *args, **kwargs)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.workspace_set.clear()
            instance.workspace_set.add(self.cleaned_data['workspace'])

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class MyGroupUpdateForm(forms.ModelForm):
    """グループ情報更新用フォーム"""

    class Meta:
        model = MyGroup
        fields = ('group_name', )


class UserRoleUpdateForm(forms.ModelForm):
    """ユーザーのワークスペース権限更新用フォーム"""

    class Meta:
        model = User
        fields = ('workspace_role', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserInviteForm(forms.ModelForm):
    """ユーザー招待用フォーム"""

    class Meta:
        model = User
        fields = ('email', 'last_name', 'first_name')


class UserInviteConfirmForm(forms.Form):
    """ユーザー招待完了後の各種設定用フォーム"""

    last_name = forms.CharField(label='姓', max_length=40, required=False)
    first_name = forms.CharField(label='名', max_length=40, required=False)
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, label='パスワード', min_length=8)
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, label='確認パスワード', min_length=8)

    def clean_new_password1(self):
        new_password1 = self.data.get('new_password1')
        new_password2 = self.data.get('new_password2')
        if new_password1 != new_password2:
            raise forms.ValidationError('パスワードが一致しません')
        return new_password1
