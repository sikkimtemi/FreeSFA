from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from register.models import MyGroup, Workspace, User
import datetime

ACTION_CHOICES = (
    ('0', '未対応'),
    ('1', '対応予定'),
    ('2', '対応中'),
    ('3', '対応終了'),
)

PUBLIC_CHOICES = (
    ('0', '非公開'),
    ('1', '閲覧可能'),
    ('2', '編集可能'),
)

CONTACT_CHOICES = (
    ('0', '訪問'),
    ('1', '架電（インバウンド）'),
    ('2', '架電（アウトバウンド）'),
    ('3', 'メール'),
    ('4', 'FAX'),
    ('5', 'DM'),
)


class CustomerInfo(models.Model):

    number_regex = RegexValidator(regex='^[0-9]+$', message='数字のみ入力してください。')

    corporate_number = models.CharField(
        verbose_name='法人番号',
        max_length=13,
        blank=True,
        validators=[number_regex],
    )

    optional_code1 = models.CharField(
        verbose_name='任意コード1',
        max_length=16,
        blank=True,
    )

    optional_code2 = models.CharField(
        verbose_name='任意コード2',
        max_length=16,
        blank=True,
    )

    optional_code3 = models.CharField(
        verbose_name='任意コード3',
        max_length=16,
        blank=True,
    )

    customer_name = models.CharField(
        verbose_name='企業名',
        max_length=40,
    )

    department_name = models.CharField(
        verbose_name='部署名',
        max_length=256,
        blank=True,
    )

    tel_number1 = models.CharField(
        verbose_name='電話番号1',
        max_length=15,
        blank=True,
        validators=[number_regex],
    )

    tel_number2 = models.CharField(
        verbose_name='電話番号2',
        max_length=15,
        blank=True,
        validators=[number_regex],
    )

    tel_number3 = models.CharField(
        verbose_name='電話番号3',
        max_length=15,
        blank=True,
        validators=[number_regex],
    )

    fax_number = models.CharField(
        verbose_name='FAX番号',
        max_length=15,
        blank=True,
        validators=[number_regex],
    )

    mail_address = models.EmailField(
        verbose_name='メールアドレス',
        max_length=256,
        blank=True,
    )

    representative = models.CharField(
        verbose_name='代表者名',
        blank=True,
        max_length=30,
    )

    contact_name = models.CharField(
        verbose_name='担当者名',
        blank=True,
        max_length=30,
    )

    zip_code = models.CharField(
        verbose_name='郵便番号',
        max_length=8,
        blank=True,
        validators=[number_regex],
    )

    address1 = models.CharField(
        verbose_name='都道府県',
        max_length=40,
        blank=True,
    )

    address2 = models.CharField(
        verbose_name='市区町村番地',
        max_length=40,
        blank=True,
    )

    address3 = models.CharField(
        verbose_name='建物名',
        max_length=40,
        blank=True,
    )

    latitude = models.DecimalField(
        verbose_name='緯度',
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
    )

    longitude = models.DecimalField(
        verbose_name='経度',
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
    )

    url1 = models.URLField(
        verbose_name='企業URL1',
        max_length=512,
        blank=True,
    )

    url2 = models.URLField(
        verbose_name='企業URL2',
        max_length=512,
        blank=True,
    )

    url3 = models.URLField(
        verbose_name='企業URL3',
        max_length=512,
        blank=True,
    )

    industry_code = models.CharField(
        verbose_name='業種',
        max_length=40,
        blank=True,
    )

    data_source = models.CharField(
        verbose_name='データソース',
        max_length=40,
        blank=True,
    )

    contracted_flg = models.BooleanField(
        verbose_name='契約済みフラグ',
        blank=True,
        default=False,
    )

    potential = models.IntegerField(verbose_name='ポテンシャル', )

    tel_limit_flg = models.BooleanField(
        verbose_name='電話禁止フラグ',
        blank=True,
        default=False,
    )

    fax_limit_flg = models.BooleanField(
        verbose_name='FAX禁止フラグ',
        blank=True,
        default=False,
    )

    mail_limit_flg = models.BooleanField(
        verbose_name='メール禁止フラグ',
        blank=True,
        default=False,
    )

    attention_flg = models.BooleanField(
        verbose_name='要注意フラグ',
        blank=True,
        default=False,
    )

    related_document_url = models.URLField(
        verbose_name='関連資料URL',
        max_length=512,
        blank=True,
    )

    remarks = models.TextField(
        verbose_name='備考',
        max_length=4096,
        blank=True,
    )

    workspace = models.ForeignKey(
        Workspace,
        verbose_name='ワークスペース',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    shared_edit_group = models.ManyToManyField(
        MyGroup,
        related_name='shared_edit_group',
        verbose_name='編集可能グループ',
        blank=True,
        help_text='この顧客情報を編集できるグループを指定します。',
    )

    shared_view_group = models.ManyToManyField(
        MyGroup,
        related_name='shared_view_group',
        verbose_name='閲覧可能グループ',
        blank=True,
        help_text='この顧客情報を閲覧できるグループを指定します。',
    )

    shared_edit_user = models.ManyToManyField(
        User,
        related_name='shared_edit_user',
        verbose_name='編集可能ユーザー',
        blank=True,
        help_text='この顧客情報を編集できるユーザーを指定します。',
    )

    shared_view_user = models.ManyToManyField(
        User,
        related_name='shared_view_user',
        verbose_name='閲覧可能ユーザー',
        blank=True,
        help_text='この顧客情報を閲覧できるユーザーを指定します。',
    )

    sales_person = models.ForeignKey(
        User,
        verbose_name='営業担当者',
        blank=True,
        null=True,
        on_delete=models.PROTECT)

    action_status = models.CharField(
        verbose_name='対応状況',
        max_length=20,
        blank=True,
        choices=ACTION_CHOICES,
        default='0',
    )

    tel_called_flg = models.BooleanField(
        verbose_name='電話済みフラグ',
        blank=True,
        default=False,
    )

    mail_sent_flg = models.BooleanField(
        verbose_name='メール済みフラグ',
        blank=True,
        default=False,
    )

    fax_sent_flg = models.BooleanField(
        verbose_name='FAX済みフラグ',
        blank=True,
        default=False,
    )

    dm_sent_flg = models.BooleanField(
        verbose_name='DM送付済みフラグ',
        blank=True,
        default=False,
    )

    visited_flg = models.BooleanField(
        verbose_name='訪問済みフラグ',
        blank=True,
        default=False,
    )

    public_status = models.CharField(
        verbose_name='公開ステータス',
        max_length=1,
        choices=PUBLIC_CHOICES,
        default='0',
    )

    delete_flg = models.BooleanField(
        verbose_name='削除フラグ',
        blank=True,
        default=False,
    )

    author = models.CharField(
        verbose_name='作成者',
        max_length=256,
        blank=True,
    )

    created_timestamp = models.DateTimeField(
        verbose_name='作成日時', auto_now_add=True)

    modifier = models.CharField(
        verbose_name='修正者',
        max_length=256,
        blank=True,
    )

    modified_timestamp = models.DateTimeField(
        verbose_name='修正日時', auto_now=True)

    def __unicode__(self):
        return u"{}".format(self.your_field)

    # 管理サイト上の表示設定
    def __str__(self):
        return self.customer_name

    def is_editable(self, email):
        """
        顧客情報が指定されたユーザーで編集可能かどうか確認する
        """
        if email == self.author:
            return True
        if self.public_status == '2':
            return True
        # ユーザーが編集可能かどうか確認
        for editable_user in self.shared_edit_user.all():
            if email == editable_user.email:
                return True
        # emailからユーザー情報を取得
        my_user = User.objects.filter(email__contains=email).all()
        # 所属するグループが編集可能かどうか確認
        for editable_group in self.shared_edit_group.all():
            for my_group in my_user[0].my_group.all():
                if my_group == editable_group:
                    return True
        return False

    class Meta:
        verbose_name = '顧客情報'
        verbose_name_plural = '顧客情報'


class ContactInfo(models.Model):

    number_regex = RegexValidator(regex='^[0-9]+$', message='数字のみ入力してください。')

    target_customer = models.ForeignKey(
        CustomerInfo,
        verbose_name='対象顧客',
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )

    operator = models.ForeignKey(
        User,
        verbose_name='対応者',
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )

    contact_type = models.CharField(
        verbose_name='対応種別',
        max_length=20,
        blank=False,
        choices=CONTACT_CHOICES,
        default='0',
    )

    target_person = models.CharField(
        verbose_name='顧客側担当者名',
        max_length=40,
        blank=True,
        help_text='実際に話をした相手の名前を入力してください。',
    )

    contact_timestamp = models.DateTimeField(
        verbose_name='対応日時', auto_now_add=True)

    tel_number = models.CharField(
        verbose_name='連絡先電話番号',
        max_length=15,
        blank=True,
        validators=[number_regex],
        help_text='実際に電話する番号を入力してください。',
    )

    mail_address = models.EmailField(
        verbose_name='連絡先メールアドレス',
        max_length=256,
        blank=True,
    )

    called_flg = models.BooleanField(
        verbose_name='架電済みフラグ',
        blank=True,
        default=False,
        help_text='顧客と話せた場合のみ場合のみチェックしてください。',
    )

    visited_flg = models.BooleanField(
        verbose_name='訪問済みフラグ',
        blank=True,
        default=False,
    )

    visit_date_plan = models.DateField(
        verbose_name='訪問日_予定',
        blank=True,
        null=True,
    )

    visit_date_act = models.DateField(
        verbose_name='訪問日_実績',
        blank=True,
        null=True,
    )

    start_time_plan = models.TimeField(
        verbose_name='訪問開始時刻_予定',
        blank=True,
        null=True,
    )

    end_time_plan = models.TimeField(
        verbose_name='訪問終了時刻_予定',
        blank=True,
        null=True,
    )

    start_time_act = models.TimeField(
        verbose_name='訪問開始時刻_実績',
        blank=True,
        null=True,
    )

    end_time_act = models.TimeField(
        verbose_name='訪問終了時刻_実績',
        blank=True,
        null=True,
    )

    remarks = models.TextField(
        verbose_name='備考',
        max_length=4096,
        blank=True,
    )

    delete_flg = models.BooleanField(
        verbose_name='削除フラグ',
        blank=True,
        default=False,
    )

    # 管理サイト上の表示設定
    def __str__(self):
        return self.target_customer.customer_name

    class Meta:
        verbose_name = 'コンタクト情報'
        verbose_name_plural = 'コンタクト情報'


class AddressInfo(models.Model):

    last_name = models.CharField(
        verbose_name='姓',
        blank=True,
        max_length=20,
    )

    first_name = models.CharField(
        verbose_name='名',
        blank=True,
        max_length=20,
    )

    last_name_kana = models.CharField(
        verbose_name='姓かな',
        blank=True,
        max_length=20,
    )

    first_name_kana = models.CharField(
        verbose_name='名かな',
        blank=True,
        max_length=20,
    )

    post = models.CharField(
        verbose_name='役職',
        blank=True,
        max_length=256,
    )

    customer_name = models.CharField(
        verbose_name='会社名',
        blank=True,
        max_length=40,
    )

    customer_name_kana = models.CharField(
        verbose_name='会社名かな',
        blank=True,
        max_length=40,
    )

    mail_address = models.EmailField(
        verbose_name='メールアドレス',
        blank=True,
        max_length=256,
    )

    phone_number = models.CharField(
        verbose_name='電話番号',
        blank=True,
        max_length=15,
    )

    fax_number = models.CharField(
        verbose_name='FAX',
        blank=True,
        max_length=15,
    )

    major_organization = models.CharField(
        verbose_name='大組織',
        blank=True,
        max_length=20,
    )

    middle_organization = models.CharField(
        verbose_name='中組織',
        blank=True,
        max_length=20,
    )

    country = models.CharField(
        verbose_name='国名',
        blank=True,
        max_length=20,
    )

    zip_code = models.CharField(
        verbose_name='郵便番号',
        blank=True,
        max_length=8,
    )

    address1 = models.CharField(
        verbose_name='都道府県',
        blank=True,
        max_length=40,
    )

    address2 = models.CharField(
        verbose_name='市区町村番地',
        blank=True,
        max_length=80,
    )

    address3 = models.CharField(
        verbose_name='ビル名',
        blank=True,
        max_length=40,
    )

    department_name = models.CharField(
        verbose_name='所属',
        blank=True,
        max_length=256,
    )

    mobile_phone_number = models.CharField(
        verbose_name='携帯電話',
        blank=True,
        max_length=15,
    )

    url = models.URLField(
        verbose_name='URL',
        blank=True,
        max_length=512,
    )

    zip_code_2 = models.CharField(
        verbose_name='郵便番号2',
        blank=True,
        max_length=8,
    )

    prefectures_2 = models.CharField(
        verbose_name='都道府県2',
        blank=True,
        max_length=10,
    )

    city_2 = models.CharField(
        verbose_name='市区町村2',
        blank=True,
        max_length=20,
    )

    address_2 = models.CharField(
        verbose_name='番地2',
        blank=True,
        max_length=80,
    )

    building_name_2 = models.CharField(
        verbose_name='ビル名2',
        blank=True,
        max_length=40,
    )

    office_2 = models.CharField(
        verbose_name='事業所2',
        blank=True,
        max_length=40,
    )

    phone_number_2 = models.CharField(
        verbose_name='電話番号2',
        blank=True,
        max_length=15,
    )

    fax_number_2 = models.CharField(
        verbose_name='FAX2',
        blank=True,
        max_length=15,
    )

    remarks = models.CharField(
        verbose_name='備考',
        blank=True,
        max_length=4096,
    )

    workspace = models.ForeignKey(
        Workspace,
        verbose_name='ワークスペース',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    related_flg = models.BooleanField(
        verbose_name='関連付けフラグ',
        blank=True,
        default=False,
    )

    author = models.ForeignKey(
        User,
        verbose_name='作成者',
        related_name='author',
        blank=True,
        null=True,
        on_delete=models.PROTECT)

    created_timestamp = models.DateTimeField(
        verbose_name='作成日時', auto_now_add=True)

    modifier = models.ForeignKey(
        User,
        verbose_name='修正者',
        related_name='modifier',
        blank=True,
        null=True,
        on_delete=models.PROTECT)

    modified_timestamp = models.DateTimeField(
        verbose_name='修正日時', auto_now=True)

    # 管理サイト上の表示設定
    def __str__(self):
        return self.last_name + ' ' + self.first_name

    class Meta:
        verbose_name = '連絡先情報'
        verbose_name_plural = '連絡先情報'


class GoalSetting(models.Model):
    """
    目標設定
    """
    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.PROTECT,
    )
    outbound_count = models.IntegerField(
        verbose_name='架電（アウトバウンド）件数',
        null=True,
    )
    visit_count = models.IntegerField(
        verbose_name='訪問件数',
        null=True,
    )


class WorkspaceEnvironmentSetting(models.Model):
    """
    ワークスペース環境設定
    """
    workspace = models.OneToOneField(
        Workspace,
        null=True,
        on_delete=models.PROTECT,
    )

    ip_phone_call_url = models.CharField(
        verbose_name='IP電話呼び出し用URL',
        max_length=512,
        blank=True,
    )

    google_maps_javascript_api_key = models.CharField(
        verbose_name='Google Maps JavaScript API用のキー',
        blank=True,
        max_length=128,
        help_text=
        '地図を動的に生成するためのAPIキーです。外部から見える場所に設置するため、必ずアプリケーションの制限（HTTPリファラー）を設定してください。',
    )

    google_maps_web_service_api_key = models.CharField(
        verbose_name='Google Maps Geocoding API用のキー',
        blank=True,
        max_length=128,
        help_text='住所から緯度経度を取得するためのAPIキーです。HTTPリファラーを設定していると動作しません。',
    )

    webhook_url1 = models.CharField(
        verbose_name='外部連携用URL1',
        max_length=512,
        blank=True,
        help_text='顧客情報の任意コード1を用いて外部システムを呼び出すときに設定します。',
    )

    webhook_url2 = models.CharField(
        verbose_name='外部連携用URL2',
        max_length=512,
        blank=True,
        help_text='顧客情報の任意コード2を用いて外部システムを呼び出すときに設定します。',
    )

    webhook_url3 = models.CharField(
        verbose_name='外部連携用URL3',
        max_length=512,
        blank=True,
        help_text='顧客情報の任意コード3を用いて外部システムを呼び出すときに設定します。',
    )

class CustomerInfoDisplaySetting(models.Model):
    """
    顧客情報の表示制御をワークスペース毎に設定する
    """
    workspace = models.OneToOneField(
        Workspace,
        null=True,
        on_delete=models.PROTECT,
    )

    optional_code1_display_name = models.CharField(
        verbose_name='任意コード1表示名',
        max_length=512,
        blank=True,
    )

    optional_code1_active_flg = models.BooleanField(
        verbose_name='任意コード1表示フラグ',
        blank=True,
        default=True,
    )

    optional_code2_display_name = models.CharField(
        verbose_name='任意コード2表示名',
        max_length=512,
        blank=True,
    )

    optional_code2_active_flg = models.BooleanField(
        verbose_name='任意コード2表示フラグ',
        blank=True,
        default=True,
    )

    optional_code3_display_name = models.CharField(
        verbose_name='任意コード3表示名',
        max_length=512,
        blank=True,
    )

    optional_code3_active_flg = models.BooleanField(
        verbose_name='任意コード3表示フラグ',
        blank=True,
        default=True,
    )
