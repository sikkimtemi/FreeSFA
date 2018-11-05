from django_filters import filters, FilterSet
from .models import CustomerInfo, ContactInfo
from django import forms


class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = '%s （降順）'


class CustomerInfoFilter(FilterSet):

    corporate_number = filters.CharFilter(
        name='corporate_number', label='法人番号', lookup_expr='contains')
    optional_code1 = filters.CharFilter(
        name='optional_code1', label='任意コード1', lookup_expr='contains')
    optional_code2 = filters.CharFilter(
        name='optional_code2', label='任意コード2', lookup_expr='contains')
    optional_code3 = filters.CharFilter(
        name='optional_code3', label='任意コード3', lookup_expr='contains')
    customer_name = filters.CharFilter(
        name='customer_name', label='企業名', lookup_expr='contains')
    department_name = filters.CharFilter(
        name='department_name', label='部署名', lookup_expr='contains')
    tel_number1 = filters.CharFilter(
        name='tel_number1', label='電話番号1', lookup_expr='contains')
    tel_number2 = filters.CharFilter(
        name='tel_number2', label='電話番号2', lookup_expr='contains')
    tel_number3 = filters.CharFilter(
        name='tel_number3', label='電話番号3', lookup_expr='contains')
    fax_number = filters.CharFilter(
        name='fax_number', label='FAX番号', lookup_expr='contains')
    mail_address = filters.CharFilter(
        name='mail_address', label='メールアドレス', lookup_expr='contains')
    representative = filters.CharFilter(
        name='representative', label='代表者名', lookup_expr='contains')
    contact_name = filters.CharFilter(
        name='contact_name', label='担当者名', lookup_expr='contains')
    zip_code = filters.CharFilter(
        name='zip_code', label='郵便番号', lookup_expr='contains')
    address1 = filters.CharFilter(
        name='address1', label='都道府県', lookup_expr='contains')
    address2 = filters.CharFilter(
        name='address2', label='市区町村番地', lookup_expr='contains')
    address3 = filters.CharFilter(
        name='address3', label='建物名', lookup_expr='contains')
    latitude_gte = filters.CharFilter(
        name='latitude', label='緯度（以上）', lookup_expr='gte')
    latitude_lte = filters.CharFilter(
        name='latitude', label='緯度（以下）', lookup_expr='lte')
    longitude_gte = filters.CharFilter(
        name='longitude', label='経度（以上）', lookup_expr='gte')
    longitude_lte = filters.CharFilter(
        name='longitude', label='経度（以下）', lookup_expr='lte')
    url1 = filters.CharFilter(
        name='url1', label='企業URL1', lookup_expr='contains')
    url2 = filters.CharFilter(
        name='url2', label='企業URL2', lookup_expr='contains')
    url3 = filters.CharFilter(
        name='url3', label='企業URL3', lookup_expr='contains')
    industry_code = filters.CharFilter(
        name='industry_code', label='業種', lookup_expr='contains')
    contracted_flg = filters.BooleanFilter(name='contracted_flg', label='契約済み')
    data_source = filters.CharFilter(
        name='data_source', label='データソース', lookup_expr='contains')
    potential_gte = filters.CharFilter(
        name='potential', label='ポテンシャル（以上）', lookup_expr='gte')
    potential_lte = filters.CharFilter(
        name='potential', label='ポテンシャル（以下）', lookup_expr='lte')
    remarks = filters.CharFilter(
        name='remarks', label='備考', lookup_expr='contains')
    author = filters.CharFilter(
        name='author', label='作成者', lookup_expr='contains')
    created_timestamp_gte = filters.CharFilter(
        name='created_timestamp',
        label='作成日時（以降）',
        lookup_expr='gte',
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    created_timestamp_lte = filters.CharFilter(
        name='created_timestamp',
        label='作成日時（以前）',
        lookup_expr='lte',
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    modifier = filters.CharFilter(
        name='modifier', label='修正者', lookup_expr='contains')
    modified_timestamp = filters.CharFilter(
        name='modified_timestamp', label='修正日時', lookup_expr='contains')
    action_status_ex = filters.CharFilter(
        name='action_status',
        label='除外する進捗状況',
        lookup_expr='exact',
        exclude=True)

    order_by = MyOrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('customer_name', 'customer_name'),
            ('zip_code', 'zip_code'),
        ),
        field_labels={
            'customer_name': '企業名',
            'zip_code': '郵便番号',
        },
        label='並び順')

    class Meta:

        model = CustomerInfo
        fields = (
            'corporate_number',
            'optional_code1',
            'optional_code2',
            'optional_code3',
            'customer_name',
            'department_name',
            'tel_number1',
            'tel_number2',
            'tel_number3',
            'fax_number',
            'mail_address',
            'representative',
            'contact_name',
            'zip_code',
            'address1',
            'address2',
            'address3',
            'url1',
            'url2',
            'url3',
            'industry_code',
            'data_source',
            'contracted_flg',
            'potential_gte',
            'potential_lte',
            'tel_limit_flg',
            'fax_limit_flg',
            'mail_limit_flg',
            'attention_flg',
            'remarks',
            'sales_person',
            'action_status',
            'tel_called_flg',
            'mail_sent_flg',
            'fax_sent_flg',
            'dm_sent_flg',
            'visited_flg',
            'public_status',
            'author',
            'created_timestamp_gte',
            'created_timestamp_lte',
            'latitude_gte',
            'latitude_lte',
            'longitude_gte',
            'longitude_lte',
            'modifier',
            'modified_timestamp',
        )


class ContactInfoFilter(FilterSet):

    target_customer = filters.CharFilter(
        name='target_customer__customer_name',
        label='対象顧客',
        lookup_expr='contains')
    operator = filters.CharFilter(name='operator__email', label='担当者（メールアドレス）')
    contact_timestamp_gte = filters.CharFilter(
        name='contact_timestamp',
        label='対応日時（以降）',
        lookup_expr='gte',
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    contact_timestamp_lte = filters.CharFilter(
        name='contact_timestamp',
        label='対応日時（以前）',
        lookup_expr='lte',
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    visit_date_plan = filters.CharFilter(
        name='visit_date_plan', label='訪問日_予定', lookup_expr='exact')
    visit_date_act = filters.CharFilter(
        name='visit_date_act', label='訪問日_実績', lookup_expr='exact')

    order_by = MyOrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('contact_timestamp', 'contact_timestamp'),
            ('contact_type', 'contact_type'),
        ),
        field_labels={
            'contact_timestamp': '対応日時',
            'contact_type': '対応種別',
        },
        label='並び順')

    class Meta:

        model = ContactInfo
        fields = (
            'target_customer',
            'operator',
            'contact_type',
            'contact_timestamp_gte',
            'contact_timestamp_lte',
            'visit_date_plan',
            'visit_date_act',
        )
