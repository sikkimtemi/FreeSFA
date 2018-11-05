from django.test import TestCase
from django.core.validators import ValidationError
from faker import Faker
from sfa.forms import CustomerInfoForm, ContactInfoForm
from datetime import datetime
from pytz import timezone

class CustomerInfoFormModelTests(TestCase):
    
    def test_customer_info_forms_normal_1(self):
        """
        顧客情報登録フォーム 正常系 1
        """
        # 全部入り。半角のみ。
        fake = Faker('ja_JP')
        params = dict(
            corporate_number=fake.ean13(),
            optional_code1=fake.ean13(),
            optional_code2=fake.ean13(),
            optional_code3=fake.ean13(),
            customer_name=fake.company(),
            department_name=fake.company(),
            tel_number1='099-123-4567',
            tel_number2='(03)1234-5678',
            tel_number3='0120-123-456',
            fax_number='(099)123-456',
            mail_address=fake.email(),
            representative=fake.name(),
            contact_name=fake.name(),
            zip_code='123-4567',
            address1=fake.prefecture(),
            address2=fake.address(),
            address3=fake.building_name() + fake.building_number(),
            url1=fake.url(),
            url2=fake.url(),
            url3=fake.url(),
            industry_code=fake.company(),
            data_source=fake.company(),
            contracted_flg='True',
            potential='100000',
            tel_limit_flg='False',
            fax_limit_flg='False',
            mail_limit_flg='False',
            attention_flg='False',
            remarks=fake.sentence(),
            public_status='0',
            delete_flg='False',
            author=fake.email(),
            modifier=fake.email(), 
        )
        form = CustomerInfoForm(params)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['corporate_number'], params['corporate_number'])
        self.assertEquals(form.cleaned_data['optional_code1'], params['optional_code1'])
        self.assertEquals(form.cleaned_data['optional_code2'], params['optional_code2'])
        self.assertEquals(form.cleaned_data['optional_code3'], params['optional_code3'])
        self.assertEquals(form.cleaned_data['customer_name'], params['customer_name'])
        self.assertEquals(form.cleaned_data['department_name'], params['department_name'])
        self.assertEquals(form.cleaned_data['tel_number1'], '0991234567')
        self.assertEquals(form.cleaned_data['tel_number2'], '0312345678')
        self.assertEquals(form.cleaned_data['tel_number3'], '0120123456')
        self.assertEquals(form.cleaned_data['fax_number'], '099123456')
        self.assertEquals(form.cleaned_data['mail_address'], params['mail_address'])
        self.assertEquals(form.cleaned_data['representative'], params['representative'])
        self.assertEquals(form.cleaned_data['contact_name'], params['contact_name'])
        self.assertEquals(form.cleaned_data['zip_code'], '1234567')
        self.assertEquals(form.cleaned_data['address1'], params['address1'])
        self.assertEquals(form.cleaned_data['address2'], params['address2'])
        self.assertEquals(form.cleaned_data['address3'], params['address3'])
        self.assertEquals(form.cleaned_data['url1'], params['url1'])
        self.assertEquals(form.cleaned_data['url2'], params['url2'])
        self.assertEquals(form.cleaned_data['url3'], params['url3'])
        self.assertEquals(form.cleaned_data['industry_code'], params['industry_code'])
        self.assertEquals(form.cleaned_data['data_source'], params['data_source'])
        self.assertTrue(form.cleaned_data['contracted_flg'])
        self.assertEquals(form.cleaned_data['potential'], 100000)
        self.assertFalse(form.cleaned_data['tel_limit_flg'])
        self.assertFalse(form.cleaned_data['fax_limit_flg'])
        self.assertFalse(form.cleaned_data['mail_limit_flg'])
        self.assertFalse(form.cleaned_data['attention_flg'])
        self.assertEquals(form.cleaned_data['remarks'], params['remarks'])
        self.assertEquals(form.cleaned_data['public_status'], '0')
        self.assertEquals(form.cleaned_data['author'], params['author'])
        self.assertEquals(form.cleaned_data['modifier'], params['modifier'])
 
    def test_customer_info_forms_normal_2(self):
        """
        顧客情報登録フォーム 正常系 2
        """
        # 全部入り。全角混在。
        fake = Faker('ja_JP')
        params = dict(
            corporate_number='１２３４５６７８９０１２３',
            optional_code1=fake.company(),
            optional_code2=fake.company(),
            optional_code3=fake.company(),
            customer_name=fake.company(),
            department_name=fake.company(),
            tel_number1='０９９−１２３−４５６７',
            tel_number2='（０３）1234-5678',
            tel_number3='0120-１２３-456',
            fax_number='099-123（４５６７）',
            mail_address=fake.email(),
            representative=fake.name(),
            contact_name=fake.name(),
            zip_code='１２３−４５６７',
            address1=fake.prefecture(),
            address2=fake.address(),
            address3=fake.building_name() + fake.building_number(),
            url1=fake.url(),
            url2=fake.url(),
            url3=fake.url(),
            industry_code=fake.company(),
            data_source=fake.company(),
            contracted_flg='True',
            potential='100000',
            tel_limit_flg='False',
            fax_limit_flg='False',
            mail_limit_flg='False',
            attention_flg='False',
            remarks=fake.sentence(),
            public_status='1',
            delete_flg='False',
            author=fake.email(),
            modifier=fake.email(), 
        )
        form = CustomerInfoForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['corporate_number'], '1234567890123')
        self.assertEquals(form.cleaned_data['optional_code1'], params['optional_code1'])
        self.assertEquals(form.cleaned_data['optional_code2'], params['optional_code2'])
        self.assertEquals(form.cleaned_data['optional_code3'], params['optional_code3'])
        self.assertEquals(form.cleaned_data['customer_name'], params['customer_name'])
        self.assertEquals(form.cleaned_data['department_name'], params['department_name'])
        self.assertEquals(form.cleaned_data['tel_number1'], '0991234567')
        self.assertEquals(form.cleaned_data['tel_number2'], '0312345678')
        self.assertEquals(form.cleaned_data['tel_number3'], '0120123456')
        self.assertEquals(form.cleaned_data['fax_number'], '0991234567')
        self.assertEquals(form.cleaned_data['mail_address'], params['mail_address'])
        self.assertEquals(form.cleaned_data['representative'], params['representative'])
        self.assertEquals(form.cleaned_data['contact_name'], params['contact_name'])
        self.assertEquals(form.cleaned_data['zip_code'], '1234567')
        self.assertEquals(form.cleaned_data['address1'], params['address1'])
        self.assertEquals(form.cleaned_data['address2'], params['address2'])
        self.assertEquals(form.cleaned_data['address3'], params['address3'])
        self.assertEquals(form.cleaned_data['url1'], params['url1'])
        self.assertEquals(form.cleaned_data['url2'], params['url2'])
        self.assertEquals(form.cleaned_data['url3'], params['url3'])
        self.assertEquals(form.cleaned_data['industry_code'], params['industry_code'])
        self.assertEquals(form.cleaned_data['data_source'], params['data_source'])
        self.assertTrue(form.cleaned_data['contracted_flg'])
        self.assertEquals(form.cleaned_data['potential'], 100000)
        self.assertFalse(form.cleaned_data['tel_limit_flg'])
        self.assertFalse(form.cleaned_data['fax_limit_flg'])
        self.assertFalse(form.cleaned_data['mail_limit_flg'])
        self.assertFalse(form.cleaned_data['attention_flg'])
        self.assertEquals(form.cleaned_data['remarks'], params['remarks'])
        self.assertEquals(form.cleaned_data['public_status'], '1')
        self.assertFalse(form.cleaned_data['delete_flg'])
        self.assertEquals(form.cleaned_data['author'], params['author'])
        self.assertEquals(form.cleaned_data['modifier'], params['modifier'])

    def test_customer_info_forms_normal_3(self):
        """
        顧客情報登録フォーム 正常系 3
        """
        # 必須項目のみ。
        fake = Faker('ja_JP')
        params = dict(
            corporate_number='',
            optional_code1='',
            optional_code2='',
            optional_code3='',
            customer_name=fake.company(),
            department_name='',
            tel_number1='',
            tel_number2='',
            tel_number3='',
            fax_number='',
            mail_address='',
            representative='',
            contact_name='',
            zip_code='',
            address1='',
            address2='',
            address3='',
            url1='',
            url2='',
            url3='',
            industry_code='',
            data_source='',
            contracted_flg='',
            potential='100000',
            tel_limit_flg='',
            fax_limit_flg='',
            mail_limit_flg='',
            attention_flg='',
            remarks='',
            workspace='', 
            public_status='2',
            delete_flg='',
            author='',
            modifier='', 
        )

        form = CustomerInfoForm(params)
        
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['corporate_number'], '')
        self.assertEquals(form.cleaned_data['optional_code1'], '')
        self.assertEquals(form.cleaned_data['optional_code2'], '')
        self.assertEquals(form.cleaned_data['optional_code3'], '')
        self.assertEquals(form.cleaned_data['customer_name'], params['customer_name'])
        self.assertEquals(form.cleaned_data['department_name'], '')
        self.assertEquals(form.cleaned_data['tel_number1'], '')
        self.assertEquals(form.cleaned_data['tel_number2'], '')
        self.assertEquals(form.cleaned_data['tel_number3'], '')
        self.assertEquals(form.cleaned_data['fax_number'], '')
        self.assertEquals(form.cleaned_data['mail_address'], '')
        self.assertEquals(form.cleaned_data['representative'], '')
        self.assertEquals(form.cleaned_data['contact_name'], '')
        self.assertEquals(form.cleaned_data['zip_code'], '')
        self.assertEquals(form.cleaned_data['address1'], '')
        self.assertEquals(form.cleaned_data['address2'], '')
        self.assertEquals(form.cleaned_data['address3'], '')
        self.assertEquals(form.cleaned_data['url1'], '')
        self.assertEquals(form.cleaned_data['url2'], '')
        self.assertEquals(form.cleaned_data['url3'], '')
        self.assertEquals(form.cleaned_data['industry_code'], '')
        self.assertEquals(form.cleaned_data['data_source'], '')
        self.assertFalse(form.cleaned_data['contracted_flg'])
        self.assertEquals(form.cleaned_data['potential'], 100000)
        self.assertFalse(form.cleaned_data['tel_limit_flg'])
        self.assertFalse(form.cleaned_data['fax_limit_flg'])
        self.assertFalse(form.cleaned_data['mail_limit_flg'])
        self.assertFalse(form.cleaned_data['attention_flg'])
        self.assertEquals(form.cleaned_data['remarks'], '')
        self.assertEquals(form.cleaned_data['public_status'], '2')
        self.assertFalse(form.cleaned_data['delete_flg'])
        self.assertEquals(form.cleaned_data['author'], '')
        self.assertEquals(form.cleaned_data['modifier'], '')

    def test_customer_info_forms_abnormal_1(self):
        """
        顧客情報登録フォーム 異常系 1
        """
        fake = Faker('ja_JP')
        params = dict(
            corporate_number='12345Abc90123',   # 法人番号にアルファベット混在
            optional_code1=fake.ean13(),
            optional_code2=fake.ean13(),
            optional_code3=fake.ean13(),
            customer_name='',               # 企業名が未入力
            department_name=fake.company(),
            tel_number1='A99-123-4567',     # 電話番号にアルファベット混在
            tel_number2='(03)1BC4-5678',    # 電話番号にアルファベット混在
            tel_number3='0120-123-4DE',     # 電話番号にアルファベット混在
            fax_number='(099)123Z4567',     # FAX番号にアルファベット混在
            mail_address='dummyexample.com',    # メールアドレスに@がない
            representative=fake.name(),
            contact_name=fake.name(),
            zip_code='123A4567',            # 郵便番号にアルファベット混在
            address1=fake.prefecture(),
            address2=fake.address(),
            address3=fake.building_name() + fake.building_number(),
            url1='://example.co.jp',       # URLが不正
            url2='https:/www.example.jp',       # URLが不正
            url3='http://example',      # URLが不正
            industry_code=fake.company(),
            data_source=fake.company(),
            contracted_flg='True',
            potential='',                   # ポテンシャルが未入力
            tel_limit_flg='False',
            fax_limit_flg='False',
            mail_limit_flg='False',
            attention_flg='False',
            remarks=fake.sentence(),
            workspace='1', 
            public_flg=True, 
            delete_flg='False',
            author=fake.email(),
            modifier=fake.email(),
        )
        form = CustomerInfoForm(params)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['corporate_number'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['customer_name'].__str__(), '[ValidationError([\'このフィールドは必須です。\'])]')
        self.assertEquals(form.errors.as_data()['tel_number1'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['tel_number2'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['tel_number3'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['fax_number'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['mail_address'].__str__(), '[ValidationError([\'有効なメールアドレスを入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['zip_code'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['url1'].__str__(), '[ValidationError([\'URLを正しく入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['url2'].__str__(), '[ValidationError([\'URLを正しく入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['url3'].__str__(), '[ValidationError([\'URLを正しく入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['potential'].__str__(), '[ValidationError([\'このフィールドは必須です。\'])]')
        self.assertEquals(form.errors.as_data()['workspace'].__str__(), '[ValidationError([\'正しく選択してください。選択したものは候補にありません。\'])]')

    def test_customer_info_forms_abnormal_2(self):
        """
        顧客情報登録フォーム 異常系 2
        """
        # 必須空欄、記号混在
        fake = Faker('ja_JP')
        params = dict(
            corporate_number='12345@@@90123',   # 法人番号に記号が混在
            optional_code1=fake.ean13(),
            optional_code2=fake.ean13(),
            optional_code3=fake.ean13(),
            customer_name='',                   # 企業名が未入力
            department_name=fake.company(),
            tel_number1='?99-123-4567',         # 電話番号に記号が混在
            tel_number2='(03)1??4-5678',        # 電話番号に記号が混在
            tel_number3='0120-123-4!!',         # 電話番号に記号が混在
            fax_number='(099)123[4567',         # FAX番号に記号が混在
            mail_address='example.@example.co.jp',  # メールアドレスが不正
            representative=fake.name(),
            contact_name=fake.name(),
            zip_code='123(4567',                # 郵便番号に記号が混在
            address1=fake.prefecture(),
            address2=fake.address(),
            address3=fake.building_name() + fake.building_number(),
            url1='htttp://example.co.jp',      # URLが不正
            url2='htps://www.example.jp',           # URLが不正
            url3='http://192.168.0.256',        # URLが不正
            industry_code=fake.company(),
            data_source=fake.company(),
            contracted_flg='True',
            potential='',                       # ポテンシャルが未入力
            tel_limit_flg='False',
            fax_limit_flg='False',
            mail_limit_flg='False',
            attention_flg='False',
            remarks=fake.sentence(),
            workspace='1', 
            public_status='',                   # 公開ステータスが未設定
            delete_flg='False',
            author=fake.email(),
            modifier=fake.email(),
        )
        form = CustomerInfoForm(params)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['corporate_number'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['customer_name'].__str__(), '[ValidationError([\'このフィールドは必須です。\'])]')
        self.assertEquals(form.errors.as_data()['tel_number1'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['tel_number2'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['tel_number3'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['fax_number'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['mail_address'].__str__(), '[ValidationError([\'有効なメールアドレスを入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['zip_code'].__str__(), '[ValidationError([\'数字のみ入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['url1'].__str__(), '[ValidationError([\'URLを正しく入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['url2'].__str__(), '[ValidationError([\'URLを正しく入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['url3'].__str__(), '[ValidationError([\'URLを正しく入力してください。\'])]')
        self.assertEquals(form.errors.as_data()['potential'].__str__(), '[ValidationError([\'このフィールドは必須です。\'])]')
        self.assertEquals(form.errors.as_data()['public_status'].__str__(), '[ValidationError([\'このフィールドは必須です。\'])]')

