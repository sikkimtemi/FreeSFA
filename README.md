# FreeSFA
[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

# 概要

https://free-sfa.tk/

FreeSFAはPython3とDjangoで書かれたオープンソースの営業支援システム(SFA)です。

顧客情報を管理し、訪問や架電といったコンタクト履歴を記録することができます。

メールアドレスとパスワードを用いた認証とGoogleアカウントを用いたソーシャル認証に対応しています。


# 使い方
ローカル環境で動かす場合は`IISE/local_settings.py`と`my.cnf`を作成してください。

`my.cnf`を作成せずに、すべての設定を`IISE/local_settings.py`に書いてもいいです。

## `IISE/local_settings.py`の例

```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '6jn1ssy-4-0(he(8w((l*53f2gjuzgo$u134zoj73*ebgq+!j%'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': './my.cnf',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

DEBUG = True

ALLOWED_HOSTS = [
    '192.168.0.99',
]

# SOCIAL AUTH
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
#SOCIAL_AUTH_TWITTER_KEY = ''
#SOCIAL_AUTH_TWITTER_SECRET = ''
#SOCIAL_AUTH_GITHUB_KEY = ''
#SOCIAL_AUTH_GITHUB_SECRET = ''

# reCAPTCHA
GOOGLE_RECAPTCHA_SITE_KEY = ''
GOOGLE_RECAPTCHA_SECRET_KEY = ''

# Mail server
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'myuser'
EMAIL_HOST_PASSWORD = 'mypassword'
EMAIL_USE_SSL = True
```

## `my.cnf`の例

```
[client]
database = my_database_name
user = my_user
password = my_password
default-character-set = utf8mb4
```

## 起動方法

```
$ cd FreeSFA
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```

Cloud9で動かす場合は、最後のコマンドを以下のようにする必要があります。

```
$ python manage.py runserver $IP:$PORT
```

# Herokuへのデプロイ方法

Herokuへのデプロイ方法はこちらを御覧ください。

https://qiita.com/sikkim/items/5bb30abc44e5ac7676f6
