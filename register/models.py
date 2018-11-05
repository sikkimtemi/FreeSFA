from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager

ROLE_CHOICES = (
    ('0', '一般ユーザー'),
    ('1', '管理者'),
    ('2', 'オーナー'),
)


class MyGroup(models.Model):
    """
    グループ管理
    """
    group_name = models.CharField(
        verbose_name='グループ名',
        max_length=40,
        blank=False,
    )

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name = _('グループ')
        verbose_name_plural = _('グループ')


class Workspace(models.Model):
    """
    ワークスペース管理
    """
    workspace_name = models.CharField(
        verbose_name='ワークスペース名',
        max_length=40,
        blank=False,
        unique=True,
    )

    my_group = models.ManyToManyField(
        MyGroup,
        verbose_name=_('グループ'),
        blank=True,
        help_text=_('Specific group for this workapce.'),
    )

    def __str__(self):
        return self.workspace_name

    class Meta:
        verbose_name = _('ワークスペース')
        verbose_name_plural = _('ワークスペース')


class UserManager(BaseUserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given username, email, and
        password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル
    usernameを使わず、emailアドレスをユーザー名として使うようにしています。
    """
    email = models.EmailField(verbose_name=_('email address'), unique=True)
    first_name = models.CharField(
        verbose_name=_('first name'), max_length=30, blank=True)
    last_name = models.CharField(
        verbose_name=_('last name'), max_length=150, blank=True)

    workspace = models.ForeignKey(
        Workspace,
        verbose_name=_('ワークスペース'),
        blank=True,
        null=True,
        help_text=_('このユーザーが所属するワークスペースです。'),
        related_name="user_set",
        related_query_name="user",
        on_delete=models.PROTECT)

    is_workspace_active = models.BooleanField(
        verbose_name=_('ワークスペース有効'),
        default=False,
        help_text=_('所属するワークスペースへの登録状況を管理します。'
                    '無効にすると仮登録、有効にすると本登録状態となります。'),
    )

    workspace_role = models.CharField(
        verbose_name=_('ワークスペース権限'),
        max_length=1,
        default='0',
        choices=ROLE_CHOICES,
    )

    my_group = models.ManyToManyField(
        MyGroup,
        verbose_name=_('グループ'),
        blank=True,
        help_text=_('Specific Group for this user.'),
        related_name="group_set",
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def email_workspace_admin(self,
                              subject,
                              message,
                              from_email=None,
                              recipients=None,
                              **kwargs):
        """Send an email to workspace administrators."""
        send_mail(subject, message, from_email, recipients, **kwargs)

    @property
    def username(self):
        return self.email
