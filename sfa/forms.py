from django import forms
from .models import CustomerInfo, ContactInfo, AddressInfo, GoalSetting, WorkspaceEnvironmentSetting
from register.models import User
from sfa.common_util import ExtractNumber
import bootstrap_datepicker_plus as datetimepicker


class CustomerInfoForm(forms.ModelForm):
    def clean_corporate_number(self):
        data = self.cleaned_data['corporate_number']
        return ExtractNumber(data, 3)

    def clean_tel_number1(self):
        data = self.cleaned_data['tel_number1']
        return ExtractNumber(data, 1)

    def clean_tel_number2(self):
        data = self.cleaned_data['tel_number2']
        return ExtractNumber(data, 1)

    def clean_tel_number3(self):
        data = self.cleaned_data['tel_number3']
        return ExtractNumber(data, 1)

    def clean_fax_number(self):
        data = self.cleaned_data['fax_number']
        return ExtractNumber(data, 1)

    def clean_zip_code(self):
        data = self.cleaned_data['zip_code']
        return ExtractNumber(data, 2)

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
            'latitude',
            'longitude',
            'url1',
            'url2',
            'url3',
            'industry_code',
            'data_source',
            'contracted_flg',
            'potential',
            'tel_limit_flg',
            'fax_limit_flg',
            'mail_limit_flg',
            'attention_flg',
            'related_document_url',
            'remarks',
            'workspace',
            'shared_edit_group',
            'shared_view_group',
            'shared_edit_user',
            'shared_view_user',
            'sales_person',
            'action_status',
            'tel_called_flg',
            'mail_sent_flg',
            'fax_sent_flg',
            'dm_sent_flg',
            'visited_flg',
            'public_status',
            'delete_flg',
            'author',
            'modifier',
        )
        widgets = {
            'customer_name':
            forms.TextInput(attrs={'placeholder': '記入例：インターマン株式会社'}),
            'zip_code':
            forms.TextInput(
                attrs={
                    'class': 'p-postal-code',
                    'placeholder': '記入例：1050012',
                }, ),
            'address1':
            forms.TextInput(
                attrs={
                    'class': 'p-region',
                    'placeholder': '記入例：東京都'
                }, ),
            'address2':
            forms.TextInput(
                attrs={
                    'class': 'p-locality p-street-address p-extended-address',
                    'placeholder': '記入例：港区芝大門1-10-18'
                }, ),
            'address3':
            forms.TextInput(
                attrs={
                    'class': '',
                    'placeholder': '記入例：PMO芝大門3階'
                }, ),
            'workspace':
            forms.HiddenInput(),
            'delete_flg':
            forms.HiddenInput(),
            'author':
            forms.HiddenInput(),
            'modifier':
            forms.HiddenInput(),
        }


class CustomerInfoDeleteForm(forms.ModelForm):
    def clean_delete_flg(self):
        return True

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
            'potential',
            'tel_limit_flg',
            'fax_limit_flg',
            'mail_limit_flg',
            'attention_flg',
            'remarks',
            'workspace',
            'shared_edit_group',
            'shared_view_group',
            'shared_edit_user',
            'shared_view_user',
            'sales_person',
            'delete_flg',
            'author',
            'modifier',
        )
        widgets = {
            'corporate_number': forms.TextInput(attrs={'readonly': True}),
            'optional_code1': forms.TextInput(attrs={'readonly': True}),
            'optional_code2': forms.TextInput(attrs={'readonly': True}),
            'optional_code3': forms.TextInput(attrs={'readonly': True}),
            'customer_name': forms.TextInput(attrs={'readonly': True}),
            'department_name': forms.TextInput(attrs={'readonly': True}),
            'tel_number1': forms.TextInput(attrs={'readonly': True}),
            'tel_number2': forms.TextInput(attrs={'readonly': True}),
            'tel_number3': forms.TextInput(attrs={'readonly': True}),
            'fax_number': forms.TextInput(attrs={'readonly': True}),
            'mail_address': forms.TextInput(attrs={'readonly': True}),
            'zip_code': forms.TextInput(attrs={'readonly': True}),
            'address1': forms.TextInput(attrs={'readonly': True}),
            'address2': forms.TextInput(attrs={'readonly': True}),
            'address3': forms.TextInput(attrs={'readonly': True}),
            'url1': forms.TextInput(attrs={'readonly': True}),
            'url2': forms.TextInput(attrs={'readonly': True}),
            'url3': forms.TextInput(attrs={'readonly': True}),
            'industry_code': forms.TextInput(attrs={'readonly': True}),
            'data_source': forms.TextInput(attrs={'readonly': True}),
            'contracted_flg': forms.CheckboxInput(attrs={'disabled': True}),
            'potential': forms.TextInput(attrs={'readonly': True}),
            'tel_limit_flg': forms.CheckboxInput(attrs={'disabled': True}),
            'fax_limit_flg': forms.CheckboxInput(attrs={'disabled': True}),
            'mail_limit_flg': forms.CheckboxInput(attrs={'disabled': True}),
            'attention_flg': forms.CheckboxInput(attrs={'disabled': True}),
            'remarks': forms.Textarea(attrs={'readonly': True}),
            'workspace': forms.Select(attrs={'disabled': True}),
            'shared_edit_group':
            forms.SelectMultiple(attrs={'disabled': True}),
            'shared_view_group':
            forms.SelectMultiple(attrs={'disabled': True}),
            'shared_edit_user': forms.SelectMultiple(attrs={'disabled': True}),
            'shared_view_user': forms.SelectMultiple(attrs={'disabled': True}),
            'sales_person': forms.Select(attrs={'disabled': True}),
            'delete_flg': forms.HiddenInput(),
            'author': forms.HiddenInput(),
            'modifier': forms.HiddenInput(),
        }


class ContactInfoForm(forms.ModelForm):
    target_customer = forms.ModelChoiceField(
        queryset=CustomerInfo.objects.all(),
        empty_label=None,
        label=ContactInfo._meta.get_field('target_customer').verbose_name)
    operator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label=None,
        label=ContactInfo._meta.get_field('operator').verbose_name)

    class Meta:
        model = ContactInfo
        fields = (
            'target_customer',
            'operator',
            'contact_type',
            'target_person',
            'tel_number',
            'mail_address',
            'called_flg',
            'visited_flg',
            'visit_date_plan',
            'visit_date_act',
            'start_time_plan',
            'end_time_plan',
            'start_time_act',
            'end_time_act',
            'remarks',
        )
        widgets = {
            'visit_date_plan':
            datetimepicker.DatePickerInput(
                format='%Y-%m-%d',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'dayViewHeaderFormat': 'YYYY年 MMMM',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'visit_date_act':
            datetimepicker.DatePickerInput(
                format='%Y-%m-%d',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'dayViewHeaderFormat': 'YYYY年 MMMM',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'start_time_plan':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'end_time_plan':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'start_time_act':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'end_time_act':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
        }


class AddressInfoForm(forms.ModelForm):
    class Meta:
        model = AddressInfo
        fields = (
            'last_name',
            'first_name',
            'last_name_kana',
            'first_name_kana',
            'post',
            'customer_name',
            'customer_name_kana',
            'mail_address',
            'phone_number',
            'fax_number',
            'major_organization',
            'middle_organization',
            'country',
            'zip_code',
            'address1',
            'address2',
            'address3',
            'department_name',
            'mobile_phone_number',
            'url',
            'zip_code_2',
            'prefectures_2',
            'city_2',
            'address_2',
            'building_name_2',
            'office_2',
            'phone_number_2',
            'fax_number_2',
            'remarks',
            'workspace',
            'author',
            'modifier',
        )
        widgets = {
            'workspace': forms.HiddenInput(),
            'author': forms.HiddenInput(),
            'modifier': forms.HiddenInput(),
        }


class AddressInfoUploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル', help_text='SkyDeskからエクスポートしたCSVファイルをアップロードしてください。')

    def clean_file(self):
        file = self.cleaned_data['file']
        print(file)
        if file.name.endswith('.csv'):
            return file
        else:
            raise forms.ValidationError('拡張子がcsvのファイルをアップロードしてください')


class CustomerInfoUploadForm(forms.ModelForm):
    file = forms.FileField(
        label='CSVファイル',
        help_text='テンプレートを参考にして顧客情報を入力したCSVファイルをアップロードしてください。')

    def clean_file(self):
        file = self.cleaned_data['file']
        print(file)
        if file.name.endswith('.csv'):
            return file
        else:
            raise forms.ValidationError('拡張子がcsvのファイルをアップロードしてください')

    class Meta:
        model = CustomerInfo
        fields = (
            'sales_person',
            'action_status',
            'potential',
            'data_source',
            'public_status',
            'shared_edit_group',
            'shared_view_group',
            'shared_edit_user',
            'shared_view_user',
        )


class VisitHistoryForm(ContactInfoForm):
    class Meta:
        model = ContactInfo
        fields = (
            'target_customer',
            'operator',
            'contact_type',
            'target_person',
            'visited_flg',
            'visit_date_plan',
            'start_time_plan',
            'end_time_plan',
            'visit_date_act',
            'start_time_act',
            'end_time_act',
            'remarks',
        )
        widgets = {
            'contact_type':
            forms.HiddenInput(),
            'visited_flg':
            forms.HiddenInput(),
            'visit_date_plan':
            forms.HiddenInput(),
            'start_time_plan':
            forms.HiddenInput(),
            'end_time_plan':
            forms.HiddenInput(),
            'visit_date_act':
            datetimepicker.DatePickerInput(
                format='%Y-%m-%d',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'dayViewHeaderFormat': 'YYYY年 MMMM',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'start_time_act':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'end_time_act':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
        }


class VisitPlanForm(ContactInfoForm):
    class Meta:
        model = ContactInfo
        fields = (
            'target_customer',
            'operator',
            'contact_type',
            'target_person',
            'visit_date_plan',
            'start_time_plan',
            'end_time_plan',
            'remarks',
        )
        widgets = {
            'contact_type':
            forms.HiddenInput(),
            'operator':
            forms.HiddenInput(),
            'visit_date_plan':
            datetimepicker.DatePickerInput(
                format='%Y-%m-%d',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'dayViewHeaderFormat': 'YYYY年 MMMM',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'start_time_plan':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
            'end_time_plan':
            datetimepicker.TimePickerInput(
                format='%H:%M',
                attrs={'readonly': 'true'},
                options={
                    'locale': 'ja',
                    'ignoreReadonly': True,
                    'allowInputToggle': True,
                }),
        }


class CallHistoryForm(ContactInfoForm):
    class Meta:
        model = ContactInfo
        fields = (
            'target_customer',
            'operator',
            'contact_type',
            'tel_number',
            'target_person',
            'called_flg',
            'remarks',
        )
        widgets = {
            'contact_type': forms.HiddenInput(),
        }


class GoalSettingForm(forms.ModelForm):
    class Meta:
        model = GoalSetting
        fields = (
            'user',
            'outbound_count',
            'visit_count',
        )
        widgets = {
            'user': forms.HiddenInput(),
        }


class WorkspaceEnvironmentSettingForm(forms.ModelForm):
    class Meta:
        model = WorkspaceEnvironmentSetting
        fields = (
            'workspace',
            'ip_phone_call_url',
            'google_maps_javascript_api_key',
            'google_maps_web_service_api_key',
            'webhook_url1',
            'webhook_url2',
            'webhook_url3',
        )
        widgets = {
            'workspace': forms.HiddenInput(),
        }
