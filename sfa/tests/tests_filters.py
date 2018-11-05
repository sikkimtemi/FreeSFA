from django.test import TestCase
from sfa.filters import CustomerInfoFilter

class CustomerInfoFilterTests(TestCase):
    def test_fields_exist(self):
        """
        フィールドの存在確認
        """
        filter = CustomerInfoFilter()
        result = filter.Meta.fields

        expect = [
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
                    'modified_timestamp'
                ]

        for index in range(len(expect)):
            self.assertEqual(expect[index], result[index])
