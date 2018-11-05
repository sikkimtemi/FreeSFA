from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.loader import get_template
from django.urls import reverse
import urllib

USER_FIELDS = ['email']


# This is initially from https://github.com/python-social-auth/social-core/blob/master/social_core/pipeline/user.py
def get_username(strategy, details, backend, user=None, *args, **kwargs):
    registration_flg = strategy.session_get('registration_flg')

    # Get the logged in user (if any)
    logged_in_user = strategy.storage.user.get_username(user)

    # Custom: check for email being provided
    if not details.get('email'):
        error = "Sorry, but your social network (Facebook or Google) needs to provide us your email address."
        return HttpResponseRedirect(
            reverse('repairs-social-network-error') + "?error=" +
            urllib.parse.quote_plus(error))

    # Custom: if user is already logged in, double check his email matches the social network email
    if logged_in_user:
        if logged_in_user.lower() != details.get('email').lower():
            error = "Sorry, but you are already logged in with another account, and the email addresses do not match. Try logging out first, please."
            return HttpResponseRedirect(
                reverse('repairs-social-network-error') + "?error=" +
                urllib.parse.quote_plus(error))

    return {
        'username': details.get('email').lower(),
    }


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    registration_flg = strategy.session_get('registration_flg')
    # 登録処理でない場合は何もしない
    if registration_flg != '1':
        return

    # TODO: 登録済みの場合はエラーメッセージを表示
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    # ユーザーを作成して仮登録状態に設定
    user = strategy.create_user(**fields)
    user.is_active = False
    user.save()

    return {'is_new': True, 'user': user}


def welcome_new_user(strategy,
                     details,
                     backend,
                     user=None,
                     is_new=False,
                     *args,
                     **kwargs):
    """
    パイプライン処理　未登録ユーザであれば仮登録を実施し、アクティベーションURLを記載したメールを送信する
    param: create_userと同等
    return: 条件NG=エラー画面に遷移、条件OK=仮登録後、仮登録完了画面に遷移＋メール送信
    """
    registration_flg = strategy.session_get('registration_flg')
    if registration_flg == '1':
        # TODO: すでにユーザーが有効ならエラー画面へ遷移
        if user and user.is_active:
            return None
        # アクティベーションURLの送付
        current_site = get_current_site(strategy.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if strategy.request.is_secure() else 'http',
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
    else:
        return None
