from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.db import transaction
from pure_pagination.mixins import PaginationMixin
from pytz import timezone
from register.models import User
from sfa.common_util import ExtractNumber, DecimalDefaultProc, CheckDuplicatePhoneNumber
from .filters import CustomerInfoFilter, ContactInfoFilter
from .forms import ContactInfoForm, CustomerInfoForm, CustomerInfoDeleteForm, AddressInfoForm, AddressInfoUploadForm, CustomerInfoUploadForm, VisitHistoryForm, VisitPlanForm, CallHistoryForm, GoalSettingForm, WorkspaceEnvironmentSettingForm, CustomerInfoDisplaySettingForm
from .models import ContactInfo, CustomerInfo, MyGroup, AddressInfo, GoalSetting, WorkspaceEnvironmentSetting, CustomerInfoDisplaySetting
import csv
import datetime
import io
import json
import requests

base_url = 'https://maps.googleapis.com/maps/api/geocode/json?language=ja&address={}&key='
headers = {'content-type': 'application/json'}


class CustomerInfoFilterView(LoginRequiredMixin, PaginationMixin, FilterView):
    """ 検索一覧画面（顧客情報） 自分が担当中の顧客で絞り込み（デフォルト表示） """
    model = CustomerInfo
    filterset_class = CustomerInfoFilter

    # pure_pagination用設定
    paginate_by = 30
    object = CustomerInfo

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        """
        以下の条件に合致する顧客情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         ・営業担当者がログインユーザー
         OR条件
         ・ワークスペースの公開ステータスが閲覧可能
         ・ワークスペースの公開ステータスが編集可能
         ・作成者が自分
         ・編集可能ユーザーが自分
         ・参照可能ユーザーが自分
         ・編集可能グループが自分が所属するグループと一致
         ・参照可能グループが自分が所属するグループと一致
        """
        return CustomerInfo.objects.filter(
            workspace=self.request.user.workspace,
            delete_flg='False',
            sales_person=self.request.user).filter(
                Q(public_status='1')
                | Q(public_status='2')
                | Q(author=self.request.user.email)
                | Q(shared_edit_user=self.request.user)
                | Q(shared_view_user=self.request.user)
                | Q(shared_edit_group__in=self.request.user.my_group.all())
                | Q(shared_view_group__in=self.request.user.my_group.all())
            ).distinct().order_by('-created_timestamp')

    def setExtractNumber(self, request, field, data_type):
        """
        リクエスト内の指定されたフィールドを変換して上書きする。
        param: 対象データfield。例：'(0120)123-456
        param: data_type。例：1=電話番号用、2=郵便番号用、3=法人番号用
        return: org_strから数字のみを抽出した文字列。例：'0120123456'
        """
        try:
            request.GET[field] = ExtractNumber(request.GET[field], data_type)
        except KeyError:
            pass

    def get(self, request, **kwargs):
        """
        検索条件の保存と復元およびあいまい検索の実装
        """
        if request.GET:
            request.GET = request.GET.copy()
            # 全角半角変換と記号の除去
            self.setExtractNumber(request, 'corporate_number', 3)
            self.setExtractNumber(request, 'tel_number1', 1)
            self.setExtractNumber(request, 'tel_number1', 1)
            self.setExtractNumber(request, 'tel_number2', 1)
            self.setExtractNumber(request, 'tel_number3', 1)
            self.setExtractNumber(request, 'fax_number', 1)
            self.setExtractNumber(request, 'zip_code', 2)
            # 対応終了を除外する
            if not 'action_status_ex' in request.GET:
                request.GET['action_status_ex'] = '3'
            # 検索条件をセッションに保存する
            request.session['query'] = request.GET
        else:
            # セッションから検索条件を復元
            request.GET = request.GET.copy()
            # 対応終了を除外する
            request.GET['action_status_ex'] = '3'
            if 'query' in request.session.keys():
                for key in request.session['query'].keys():
                    request.GET[key] = request.session['query'][key]

        # 一覧画面切り替え時に存在しないページを指定した場合のエラー回避処理
        curr_page = '1'
        if 'page' in request.GET:
            curr_page = request.GET['page']
        p = self.get_paginator(
            queryset=self.get_queryset(), per_page=self.paginate_by)
        if int(curr_page) > p.num_pages:  # 指定したページが全体よりも大きければ1ページ目を表示
            request.GET['page'] = '1'

        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡す値をセットする
        """
        ctx = super().get_context_data(**kwargs)
        if self.request.GET:
            if 'none' in self.request.GET:
                ctx['in_search'] = 'none'
            elif 'action_status' in self.request.GET:  # 検索中なら必ずaction_statusが含まれるため
                action_status = self.request.GET['action_status']
                ctx['in_search'] = 'active'
                if action_status == '0':
                    ctx['filtering_message'] = '未対応'
                elif action_status == '1':
                    ctx['filtering_message'] = '対応予定'
                elif action_status == '2':
                    ctx['filtering_message'] = '対応中'
                elif action_status == '3':
                    ctx['filtering_message'] = '対応終了'
                else:
                    ctx['filtering_message'] = '複数条件'
                ctx['filtering_message'] = ctx['filtering_message'] + 'で絞り込み中。'

            if 'map_view' in self.request.GET:
                ctx['map_view'] = '1'
        ctx['filtering_range'] = 'user'  # 絞り込みの範囲はユーザー
        # 任意コードを用いて外部システムを呼び出すURL1
        try:
            ctx['webhook_url1'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url1
        except:
            ctx['webhook_url1'] = ''
        # 任意コードを用いて外部システムを呼び出すURL2
        try:
            ctx['webhook_url2'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url2
        except:
            ctx['webhook_url2'] = ''
        # 任意コードを用いて外部システムを呼び出すURL3
        try:
            ctx['webhook_url3'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url3
        except:
            ctx['webhook_url3'] = ''

        # 顧客情報の表示制御を行う
        try:
            my_filter = ctx['filter']
            form = my_filter.form
            customer_info_display_setting = self.request.user.workspace.customerinfodisplaysetting
            optional_code1 = form.fields['optional_code1']
            optional_code2 = form.fields['optional_code2']
            optional_code3 = form.fields['optional_code3']
            if not customer_info_display_setting.optional_code1_active_flg:
                optional_code1.widget = forms.HiddenInput()
            if not customer_info_display_setting.optional_code2_active_flg:
                optional_code2.widget = forms.HiddenInput()
            if not customer_info_display_setting.optional_code3_active_flg:
                optional_code3.widget = forms.HiddenInput()
            if customer_info_display_setting.optional_code1_display_name:
                optional_code1.label = customer_info_display_setting.optional_code1_display_name
            if customer_info_display_setting.optional_code2_display_name:
                optional_code2.label = customer_info_display_setting.optional_code2_display_name
            if customer_info_display_setting.optional_code3_display_name:
                optional_code3.label = customer_info_display_setting.optional_code3_display_name
        except:
            pass

        return ctx


class CustomerInfoMapView(CustomerInfoFilterView):
    """自分が担当中の顧客情報一覧の地図画面を表示する"""
    template_name = 'sfa/visit_target_map.html'

    def get_context_data(self, **kwargs):
        """
        地図の表示に必要な情報を生成する
        """
        ctx = super().get_context_data(**kwargs)
        customerinfo_list = ctx['customerinfo_list']

        markers = []

        for customerinfo in customerinfo_list:
            if not (customerinfo.latitude or customerinfo.longitude):
                continue
            marker = {
                'name':
                customerinfo.customer_name,
                'address':
                customerinfo.address1 + customerinfo.address2 +
                customerinfo.address3,
                'lat':
                customerinfo.latitude,
                'lng':
                customerinfo.longitude,
                'visited':
                customerinfo.visited_flg
            }
            markers.append(marker)
        ctx['markers'] = json.dumps(
            markers, ensure_ascii=False, default=DecimalDefaultProc)
        # 地図を動的に生成するためのAPIキー
        try:
            ctx['api_key'] = self.request.user.workspace.workspaceenvironmentsetting.google_maps_javascript_api_key
        except:
            ctx['api_key'] = ''
        return ctx


class CustomerInfoAreaSearchView(LoginRequiredMixin, TemplateView):
    """与えられた緯度経度を中心とする2km四方のエリアに存在する顧客を一覧表示する"""

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get(self, request, **kwargs):
        """
        緯度と経度から検索条件を生成し、顧客情報一覧の検索を行う
        """
        target = None
        if request.GET:
            request.GET = request.GET.copy()
            # 対象顧客の条件を取得
            target = request.GET['target'] if 'target' in request.GET else None
            # 緯度と経度を取得
            latitude = Decimal(
                request.GET['latitude']) if 'latitude' in request.GET else None
            longitude = Decimal(request.GET[
                'longitude']) if 'longitude' in request.GET else None
            # 緯度と経度の差分
            sub_lat = Decimal('0.008987691')
            sub_lng = Decimal('0.010969825')
            if latitude and longitude:
                # 検索用の値を生成
                request.GET['latitude_gte'] = str(latitude - sub_lat)
                request.GET['latitude_lte'] = str(latitude + sub_lat)
                request.GET['longitude_gte'] = str(longitude - sub_lng)
                request.GET['longitude_lte'] = str(longitude + sub_lng)
                request.GET['action_status'] = ''
                request.GET['map_view'] = '1'
                # 検索条件をセッションに保存する
                request.session['query'] = request.GET

        if target == 'all':
            return redirect('customer_list_all')
        elif target == 'group':
            return redirect('customer_list_group')

        return redirect('customer_list_user')


class CustomerInfoGroupFilterView(CustomerInfoFilterView):
    """ 検索一覧画面（顧客情報） 同一グループで担当中の顧客で絞り込み """

    def get_queryset(self):
        """
        以下の条件に合致する顧客情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         ・営業担当者が自分と同一グループのユーザー
         OR条件
         ・ワークスペースの公開ステータスが閲覧可能
         ・ワークスペースの公開ステータスが編集可能
         ・作成者が自分
         ・編集可能ユーザーが自分
         ・参照可能ユーザーが自分
         ・編集可能グループが自分が所属するグループと一致
         ・参照可能グループが自分が所属するグループと一致
        """
        return CustomerInfo.objects.filter(
            workspace=self.request.user.workspace,
            delete_flg='False').filter(sales_person__in=User.objects.all(
            ).filter(my_group__in=self.request.user.my_group.all())).filter(
                Q(public_status='1')
                | Q(public_status='2')
                | Q(author=self.request.user.email)
                | Q(shared_edit_user=self.request.user)
                | Q(shared_view_user=self.request.user)
                | Q(shared_edit_group__in=self.request.user.my_group.all())
                | Q(shared_view_group__in=self.request.user.my_group.all())
            ).distinct().order_by('-created_timestamp')

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡す値をセットする
        """
        ctx = super().get_context_data(**kwargs)
        ctx['filtering_range'] = 'group'  # 絞り込みの範囲はグループ
        return ctx


class CustomerInfoGroupMapView(CustomerInfoGroupFilterView):
    """同一グループが担当中の顧客情報一覧の地図画面を表示する"""
    template_name = 'sfa/visit_target_map.html'

    def get_context_data(self, **kwargs):
        """
        地図の表示に必要な情報を生成する
        """
        ctx = super().get_context_data(**kwargs)
        customerinfo_list = ctx['customerinfo_list']

        markers = []

        for customerinfo in customerinfo_list:
            if not (customerinfo.latitude or customerinfo.longitude):
                continue
            marker = {
                'name':
                customerinfo.customer_name,
                'address':
                customerinfo.address1 + customerinfo.address2 +
                customerinfo.address3,
                'lat':
                customerinfo.latitude,
                'lng':
                customerinfo.longitude,
                'visited':
                customerinfo.visited_flg
            }
            markers.append(marker)
        ctx['markers'] = json.dumps(
            markers, ensure_ascii=False, default=DecimalDefaultProc)
        # 地図を動的に生成するためのAPIキー
        try:
            ctx['api_key'] = self.request.user.workspace.workspaceenvironmentsetting.google_maps_javascript_api_key
        except:
            ctx['api_key'] = ''
        return ctx


class CustomerInfoAllFilterView(CustomerInfoFilterView):
    """ 検索一覧画面（顧客情報） すべての顧客を表示 """

    def get_queryset(self):
        """
        以下の条件に合致する顧客情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         OR条件
         ・ワークスペースの公開ステータスが閲覧可能
         ・ワークスペースの公開ステータスが編集可能
         ・作成者が自分
         ・編集可能ユーザーが自分
         ・参照可能ユーザーが自分
         ・編集可能グループが自分が所属するグループと一致
         ・参照可能グループが自分が所属するグループと一致
        """
        return CustomerInfo.objects.filter(
            workspace=self.request.user.workspace, delete_flg='False').filter(
                Q(public_status='1')
                | Q(public_status='2')
                | Q(author=self.request.user.email)
                | Q(shared_edit_user=self.request.user)
                | Q(shared_view_user=self.request.user)
                | Q(shared_edit_group__in=self.request.user.my_group.all())
                | Q(shared_view_group__in=self.request.user.my_group.all())
            ).distinct().order_by('-created_timestamp')

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡す値をセットする
        """
        ctx = super().get_context_data(**kwargs)
        ctx['filtering_range'] = 'all'  # 絞り込みの範囲は全体
        return ctx


class CustomerInfoAllMapView(CustomerInfoAllFilterView):
    """同一ワークスペース内の顧客情報一覧の地図画面を表示する"""
    template_name = 'sfa/visit_target_map.html'

    def get_context_data(self, **kwargs):
        """
        地図の表示に必要な情報を生成する
        """
        ctx = super().get_context_data(**kwargs)
        customerinfo_list = ctx['customerinfo_list']

        markers = []

        for customerinfo in customerinfo_list:
            if not (customerinfo.latitude or customerinfo.longitude):
                continue
            marker = {
                'name':
                customerinfo.customer_name,
                'address':
                customerinfo.address1 + customerinfo.address2 +
                customerinfo.address3,
                'lat':
                customerinfo.latitude,
                'lng':
                customerinfo.longitude,
                'visited':
                customerinfo.visited_flg
            }
            markers.append(marker)
        ctx['markers'] = json.dumps(
            markers, ensure_ascii=False, default=DecimalDefaultProc)
        # 地図を動的に生成するためのAPIキー
        try:
            ctx['api_key'] = self.request.user.workspace.workspaceenvironmentsetting.google_maps_javascript_api_key
        except:
            ctx['api_key'] = ''

        return ctx


class CustomerInfoCheckDuplicateView(CustomerInfoFilterView):
    """ 電話番号が重複している顧客情報一覧を表示 """

    def get_queryset(self):
        """
        以下の条件に合致する顧客情報が処理の対象となる
         OR条件
         ・電話番号1が渡された電話番号と一致
         ・電話番号2が渡された電話番号と一致
         ・電話番号3が渡された電話番号と一致
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         OR条件
         ・作成者が自分
         ・編集可能ユーザーが自分
         ・参照可能ユーザーが自分
         ・編集可能グループが自分が所属するグループと一致
         ・参照可能グループが自分が所属するグループと一致
        """
        phone_number = self.request.GET[
            'phone_number'] if 'phone_number' in self.request.GET else ''
        if not phone_number:
            return redirect('customer_list_user')
        return CustomerInfo.objects.filter(
            Q(tel_number1=phone_number) | Q(tel_number2=phone_number)
            | Q(tel_number3=phone_number)).filter(
                workspace=self.request.user.workspace,
                delete_flg='False').filter(
                    Q(public_status='1')
                    | Q(public_status='2')
                    | Q(author=self.request.user.email)
                    | Q(shared_edit_user=self.request.user)
                    | Q(shared_view_user=self.request.user)
                    | Q(shared_edit_group__in=self.request.user.my_group.all())
                    | Q(shared_view_group__in=self.request.user.my_group.all())
                ).distinct().order_by('-created_timestamp')

    def get_context_data(self, **kwargs):
        """
        テンプレートに渡す値をセットする
        """
        ctx = super().get_context_data(**kwargs)
        ctx['filtering_range'] = 'all'  # 絞り込みの範囲は全体
        return ctx


class CustomerInfoDetailView(LoginRequiredMixin, DetailView):
    """ 詳細画面（顧客情報） """
    model = CustomerInfo

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        """
        以下の条件に合致する顧客情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         OR条件
         ・ワークスペースの公開ステータスが閲覧可能
         ・ワークスペースの公開ステータスが編集可能
         ・作成者が自分
         ・編集可能ユーザーが自分
         ・参照可能ユーザーが自分
         ・編集可能グループが自分が所属するグループと一致
         ・参照可能グループが自分が所属するグループと一致
        """
        return CustomerInfo.objects.filter(
            workspace=self.request.user.workspace, delete_flg='False').filter(
                Q(public_status='1')
                | Q(public_status='2')
                | Q(author=self.request.user.email)
                | Q(shared_edit_user=self.request.user)
                | Q(shared_view_user=self.request.user)
                | Q(shared_edit_group__in=self.request.user.my_group.all())
                | Q(shared_view_group__in=self.request.user.my_group.all())
            ).distinct().order_by('-created_timestamp')

    def get_context_data(self, **kwargs):
        """
        表示に必要な値をテンプレート側に渡す
        """
        ctx = super().get_context_data(**kwargs)
        # 地図を動的に生成するためのAPIキー
        try:
            ctx['api_key'] = self.request.user.workspace.workspaceenvironmentsetting.google_maps_javascript_api_key
        except:
            ctx['api_key'] = ''
        return ctx


class CustomerInfoCreateView(LoginRequiredMixin, CreateView):
    """ 登録画面（顧客情報） """
    model = CustomerInfo
    form_class = CustomerInfoForm
    success_url = reverse_lazy('customer_list_user')

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['sales_person'] = self.request.user  # 営業担当者をログインユーザーに設定
        initial['potential'] = 80000  # ポテンシャルを80000円に設定
        return initial

    def post(self, request, **kwargs):
        """
        作成者と修正者およびワークスペースの自動入力
        """
        request.POST = request.POST.copy()
        # ログインユーザー情報の取得
        user = request.user
        # 作成者と修正者にログインユーザーのメールアドレスを入力
        request.POST['author'] = user.email
        request.POST['modifier'] = user.email
        # ワークスペースにログインユーザーが所属するワークスペースを入力
        request.POST['workspace'] = user.workspace.pk

        return super().post(request, **kwargs)

    def get_context_data(self, **kwargs):
        """
        フォームの選択肢を絞り込む。表示項目の表示制御
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        login_user = self.request.user

        # 選択可能な共有ユーザーを同一ワークスペースで絞り込み、作成者は除外する
        shared_edit_user = form.fields['shared_edit_user']
        shared_view_user = form.fields['shared_view_user']
        shared_edit_user.queryset = User.objects.filter(
            workspace=login_user.workspace.pk).exclude(email=login_user.email)
        shared_view_user.queryset = User.objects.filter(
            workspace=login_user.workspace.pk).exclude(email=login_user.email)

        # 選択可能な共有グループを同一ワークスペースで絞り込む
        shared_edit_group = form.fields['shared_edit_group']
        shared_view_group = form.fields['shared_view_group']
        shared_edit_group.queryset = MyGroup.objects.filter(
            workspace=login_user.workspace.pk)
        shared_view_group.queryset = MyGroup.objects.filter(
            workspace=login_user.workspace.pk)

        # 選択可能な営業担当者を同一ワークスペースで絞り込む
        sales_person = form.fields['sales_person']
        sales_person.queryset = User.objects.filter(
            workspace=login_user.workspace.pk)

        # 顧客情報の表示制御を行う
        try:
            customer_info_display_setting = self.request.user.workspace.customerinfodisplaysetting
            optional_code1 = form.fields['optional_code1']
            optional_code2 = form.fields['optional_code2']
            optional_code3 = form.fields['optional_code3']
            if not customer_info_display_setting.optional_code1_active_flg:
                optional_code1.widget = forms.HiddenInput()
            if not customer_info_display_setting.optional_code2_active_flg:
                optional_code2.widget = forms.HiddenInput()
            if not customer_info_display_setting.optional_code3_active_flg:
                optional_code3.widget = forms.HiddenInput()
            if customer_info_display_setting.optional_code1_display_name:
                optional_code1.label = customer_info_display_setting.optional_code1_display_name
            if customer_info_display_setting.optional_code2_display_name:
                optional_code2.label = customer_info_display_setting.optional_code2_display_name
            if customer_info_display_setting.optional_code3_display_name:
                optional_code3.label = customer_info_display_setting.optional_code3_display_name
        except:
            pass

        return ctx

    def form_valid(self, form):
        """
        フォーム入力後の処理
        """
        # 電話番号の重複チェック
        tel_number1 = self.request.POST[
            'tel_number1'] if 'tel_number1' in self.request.POST else ''
        tel_number2 = self.request.POST[
            'tel_number2'] if 'tel_number1' in self.request.POST else ''
        tel_number3 = self.request.POST[
            'tel_number3'] if 'tel_number1' in self.request.POST else ''
        form.instance.tel_number1_duplicate_count = CheckDuplicatePhoneNumber(
            tel_number1, self.request.user)
        form.instance.tel_number2_duplicate_count = CheckDuplicatePhoneNumber(
            tel_number2, self.request.user)
        form.instance.tel_number3_duplicate_count = CheckDuplicatePhoneNumber(
            tel_number3, self.request.user)
        form.save()

        # 住所から緯度経度を取得
        # すでに緯度経度が入力済みの場合は何もしない
        latitude = self.request.POST[
            'latitude'] if 'latitude' in self.request.POST else ''
        longitude = self.request.POST[
            'longitude'] if 'longitude' in self.request.POST else ''
        if latitude and longitude:
            return super().form_valid(form)

        # 住所を取得
        address1 = self.request.POST[
            'address1'] if 'address1' in self.request.POST else ''
        address2 = self.request.POST[
            'address2'] if 'address2' in self.request.POST else ''
        address_str = address1 + address2
        # 住所から緯度経度を取得するためのAPIキー
        try:
            geocode_api_key = self.request.user.workspace.workspaceenvironmentsetting.google_maps_web_service_api_key
        except:
            geocode_api_key = ''

        if address_str and geocode_api_key:
            # Google Geocode APIで住所から緯度経度情報を取得
            geocode_url = base_url + geocode_api_key
            url = geocode_url.format(address_str)
            r = requests.get(url, headers=headers)
            data = r.json()
            if 'results' in data and len(data['results']) > 0:
                latitude = data['results'][0]['geometry']['location']['lat']
                longitude = data['results'][0]['geometry']['location']['lng']
                form.instance.latitude = latitude
                form.instance.longitude = longitude
                form.save()

        return super().form_valid(form)


class CustomerInfoUpdateView(LoginRequiredMixin, UpdateView):
    """ 更新画面（顧客情報） """
    model = CustomerInfo
    form_class = CustomerInfoForm

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('detail', kwargs={'pk': pk})

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        """
        以下の条件に合致する顧客情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         OR条件
         ・ワークスペースの公開ステータスが編集可能
         ・作成者が自分
         ・編集可能ユーザーが自分
         ・編集可能グループが自分が所属するグループと一致
        """
        return CustomerInfo.objects.filter(
            workspace=self.request.user.workspace, delete_flg='False').filter(
                Q(public_status='2')
                | Q(author=self.request.user.email)
                | Q(shared_edit_user=self.request.user)
                | Q(shared_edit_group__in=self.request.user.my_group.all())
            ).distinct().order_by('-created_timestamp')

    def get_context_data(self, **kwargs):
        """
        フォームの選択肢を絞り込む
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        author = CustomerInfo.objects.get(pk=self.kwargs['pk']).author
        login_user = self.request.user

        # 選択可能な共有ユーザーを同一ワークスペースで絞り込み、作成者は除外する
        shared_edit_user = form.fields['shared_edit_user']
        shared_view_user = form.fields['shared_view_user']
        shared_edit_user.queryset = User.objects.filter(
            workspace=login_user.workspace.pk).exclude(email=author)
        shared_view_user.queryset = User.objects.filter(
            workspace=login_user.workspace.pk).exclude(email=author)

        # 選択可能な共有グループを同一ワークスペースで絞り込む
        shared_edit_group = form.fields['shared_edit_group']
        shared_view_group = form.fields['shared_view_group']
        shared_edit_group.queryset = MyGroup.objects.filter(
            workspace=login_user.workspace.pk)
        shared_view_group.queryset = MyGroup.objects.filter(
            workspace=login_user.workspace.pk)

        # 選択可能な営業担当者を同一ワークスペースで絞り込む
        sales_person = form.fields['sales_person']
        sales_person.queryset = User.objects.filter(
            workspace=login_user.workspace.pk)

        # 顧客情報の表示制御を行う
        try:
            customer_info_display_setting = self.request.user.workspace.customerinfodisplaysetting
            optional_code1 = form.fields['optional_code1']
            optional_code2 = form.fields['optional_code2']
            optional_code3 = form.fields['optional_code3']
            if not customer_info_display_setting.optional_code1_active_flg:
                optional_code1.widget = forms.HiddenInput()
            if not customer_info_display_setting.optional_code2_active_flg:
                optional_code2.widget = forms.HiddenInput()
            if not customer_info_display_setting.optional_code3_active_flg:
                optional_code3.widget = forms.HiddenInput()
            if customer_info_display_setting.optional_code1_display_name:
                optional_code1.label = customer_info_display_setting.optional_code1_display_name
            if customer_info_display_setting.optional_code2_display_name:
                optional_code2.label = customer_info_display_setting.optional_code2_display_name
            if customer_info_display_setting.optional_code3_display_name:
                optional_code3.label = customer_info_display_setting.optional_code3_display_name
        except:
            pass

        return ctx

    def post(self, request, **kwargs):
        """
        修正者の自動入力
        """
        request.POST = request.POST.copy()
        # ログインユーザー情報の取得
        user = request.user
        # 修正者にログインユーザーのメールアドレスを入力
        request.POST['modifier'] = user.email

        return super().post(request, **kwargs)

    def form_valid(self, form):
        """
        住所から緯度経度を取得
        """
        # すでに緯度経度が入力済みの場合は何もしない
        latitude = self.request.POST[
            'latitude'] if 'latitude' in self.request.POST else ''
        longitude = self.request.POST[
            'longitude'] if 'longitude' in self.request.POST else ''
        if latitude and longitude:
            return super().form_valid(form)

        # 住所を取得
        address1 = self.request.POST[
            'address1'] if 'address1' in self.request.POST else ''
        address2 = self.request.POST[
            'address2'] if 'address2' in self.request.POST else ''
        address_str = address1 + address2
        # 住所から緯度経度を取得するためのAPIキー
        try:
            geocode_api_key = self.request.user.workspace.workspaceenvironmentsetting.google_maps_web_service_api_key
        except:
            geocode_api_key = ''

        if address_str and geocode_api_key:
            # Google Geocode APIで住所から緯度経度情報を取得
            geocode_url = base_url + geocode_api_key
            url = geocode_url.format(address_str)
            r = requests.get(url, headers=headers)
            data = r.json()
            if 'results' in data and len(data['results']) > 0:
                latitude = data['results'][0]['geometry']['location']['lat']
                longitude = data['results'][0]['geometry']['location']['lng']
                form.instance.latitude = latitude
                form.instance.longitude = longitude
                form.save()

        return super().form_valid(form)


class CustomerInfoBulkUpdateView(LoginRequiredMixin, TemplateView):
    """顧客情報の一括更新"""
    model = CustomerInfo
    success_url = reverse_lazy('customer_list_user')

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def post(self, request, **kwargs):
        """
        チェックされた顧客情報を一括更新する
        """
        check_ids = request.POST.getlist('check_ids')
        action_status = request.POST[
            'action_status'] if 'action_status' in request.POST else None
        for check_id in check_ids:
            if not action_status:
                continue
            target = CustomerInfo.objects.get(pk=check_id)
            if not target.is_editable(request.user.email):
                continue
            if action_status == '0' or action_status == '1' or action_status == '2' or action_status == '3':
                target.action_status = action_status  # 進捗状況
            elif action_status == '10':
                target.sales_person = request.user  # 営業担当者
            elif action_status == '99':
                target.delete_flg = True

            # 削除処理以外の場合は住所から緯度・経度を取得する
            if action_status != '99' and not (target.latitude
                                              and target.longitude):
                address_str = target.address1 + target.address2  # 住所を取得
                # 住所から緯度経度を取得するためのAPIキー
                try:
                    geocode_api_key = self.request.user.workspace.workspaceenvironmentsetting.google_maps_web_service_api_key
                except:
                    geocode_api_key = ''

                if address_str and geocode_api_key:
                    # Google Geocode APIで住所から緯度経度情報を取得
                    geocode_url = base_url + geocode_api_key
                    url = geocode_url.format(address_str)
                    r = requests.get(url, headers=headers)
                    data = r.json()
                    if 'results' in data and len(data['results']) > 0:
                        latitude = data['results'][0]['geometry']['location'][
                            'lat']
                        longitude = data['results'][0]['geometry']['location'][
                            'lng']
                        target.latitude = latitude
                        target.longitude = longitude

            target.save()
        return redirect('customer_list_user')


class CustomerInfoDeleteView(LoginRequiredMixin, TemplateView):
    """ 顧客情報を削除する """
    model = CustomerInfo

    def dispatch(self, request, *args, **kwargs):
        # 顧客情報の削除は、以下の条件を満たす場合のみ実施できる
        # ・ワークスペースに所属し、有効になっている
        # ・対象の顧客情報が編集可能
        target = CustomerInfo.objects.get(pk=self.kwargs['pk'])
        if request.user.workspace and request.user.is_workspace_active and target.is_editable(
                request.user.email):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get(self, request, **kwargs):
        target = CustomerInfo.objects.get(pk=self.kwargs['pk'])
        target.delete_flg = True
        target.save()
        return redirect('customer_list_user')


class CustomerInfoImportView(generic.FormView):
    """顧客情報を格納したCSVファイルをインポートする処理"""
    template_name = 'sfa/customerinfo_import.html'
    success_url = reverse_lazy('customer_list_user')
    form_class = CustomerInfoUploadForm
    number_of_columns = 31  # 列の数を定義しておく。各行の列がこれかどうかを判断する

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def save_csv(self, form):
        sales_person = self.request.POST[
            'sales_person'] if 'sales_person' in self.request.POST else None
        action_status = self.request.POST[
            'action_status'] if 'action_status' in self.request.POST else None
        potential = self.request.POST[
            'potential'] if 'potential' in self.request.POST else 1
        data_source = self.request.POST[
            'data_source'] if 'data_source' in self.request.POST else ''
        public_status = self.request.POST[
            'public_status'] if 'public_status' in self.request.POST else None
        shared_edit_group = self.request.POST.getlist(
            'shared_edit_group'
        ) if 'shared_edit_group' in self.request.POST else None
        shared_view_group = self.request.POST.getlist(
            'shared_view_group'
        ) if 'shared_view_group' in self.request.POST else None
        shared_edit_user = self.request.POST.getlist(
            'shared_edit_user'
        ) if 'shared_edit_user' in self.request.POST else None
        shared_view_user = self.request.POST.getlist(
            'shared_view_user'
        ) if 'shared_view_user' in self.request.POST else None
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csvfile = io.TextIOWrapper(form.cleaned_data['file'], encoding='MS932')
        reader = csv.reader(csvfile)
        index = 1  # 1行目でのUnicodeDecodeError対策。for文の初回のnextでエラーになるとiの値がない為
        try:
            # indexは、現在の行番号。エラーの際に補足情報として使う
            for index, row in enumerate(reader, 1):
                # 列数が違う場合
                if len(row) != self.number_of_columns:
                    raise InvalidColumnsExcepion(
                        '{0}行目が変です。本来の列数: {1}, {0}行目の列数: {2}'.format(
                            index, self.number_of_columns, len(row)))

                # 問題なければ、この行は保存する。(実際には、form_validのwithブロック終了後に正式に保存される)
                if index == 1:
                    continue
                my_potential = potential if row[25] == '' else row[25]
                customerinfo = CustomerInfo.objects.create(
                    potential=my_potential)
                customerinfo.corporate_number = ExtractNumber(
                    row[0], 3)  # 法人番号を数字のみに変換
                customerinfo.optional_code1 = row[1]
                customerinfo.optional_code2 = row[2]
                customerinfo.optional_code3 = row[3]
                customerinfo.customer_name = row[4]
                customerinfo.department_name = row[5]
                customerinfo.tel_number1 = ExtractNumber(row[6],
                                                         1)  # 電話番号を数字のみに変換
                customerinfo.tel_number2 = ExtractNumber(row[7],
                                                         1)  # 電話番号を数字のみに変換
                customerinfo.tel_number3 = ExtractNumber(row[8],
                                                         1)  # 電話番号を数字のみに変換
                customerinfo.fax_number = ExtractNumber(row[9],
                                                        1)  # FAX番号を数字のみに変換
                customerinfo.mail_address = row[10]
                customerinfo.representative = row[11]
                customerinfo.contact_name = row[12]
                customerinfo.zip_code = ExtractNumber(row[13],
                                                      2)  # 郵便番号を数字のみに変換
                customerinfo.address1 = row[14]
                customerinfo.address2 = row[15]
                customerinfo.address3 = row[16]
                customerinfo.latitude = None if row[17] == '' else Decimal(
                    row[17])
                customerinfo.longitude = None if row[18] == '' else Decimal(
                    row[18])
                customerinfo.url1 = row[19]
                customerinfo.url2 = row[20]
                customerinfo.url3 = row[21]
                customerinfo.industry_code = row[22]
                customerinfo.data_source = data_source if row[
                    23] == '' else row[23]
                customerinfo.contracted_flg = False if row[24] == '' else int(
                    row[24])
                customerinfo.tel_limit_flg = False if row[26] == '' else int(
                    row[26])
                customerinfo.fax_limit_flg = False if row[27] == '' else int(
                    row[27])
                customerinfo.mail_limit_flg = False if row[28] == '' else int(
                    row[28])
                customerinfo.attention_flg = False if row[29] == '' else int(
                    row[29])
                customerinfo.remarks = row[30]
                if public_status:
                    customerinfo.public_status = public_status
                if sales_person:
                    customerinfo.sales_person = User.objects.get(
                        pk=sales_person)
                if action_status:
                    customerinfo.action_status = action_status
                if shared_edit_group:
                    customerinfo.shared_edit_group.set(shared_edit_group)
                if shared_view_group:
                    customerinfo.shared_view_group.set(shared_view_group)
                if shared_edit_user:
                    customerinfo.shared_edit_user.set(shared_edit_user)
                if shared_view_user:
                    customerinfo.shared_view_user.set(shared_view_user)
                customerinfo.workspace = self.request.user.workspace
                customerinfo.author = self.request.user.email
                customerinfo.modifier = self.request.user.email
                # 電話番号の重複チェック
                customerinfo.tel_number1_duplicate_count = CheckDuplicatePhoneNumber(
                    customerinfo.tel_number1, self.request.user)
                customerinfo.tel_number2_duplicate_count = CheckDuplicatePhoneNumber(
                    customerinfo.tel_number2, self.request.user)
                customerinfo.tel_number3_duplicate_count = CheckDuplicatePhoneNumber(
                    customerinfo.tel_number3, self.request.user)
                customerinfo.save()

        except Exception as e:
            raise InvalidSourceExcepion(
                '{}行目でインポートに失敗しました。正しいCSVファイルか確認ください。{}'.format(index, e))

    def form_valid(self, form):
        try:
            # CSVの100行目でエラーがおきたら、前の99行分は保存されないようにする
            with transaction.atomic():
                self.save_csv(form)
        # 今のところは、この2つのエラーは同様に対処します。
        except InvalidSourceExcepion as e:
            form.add_error('file', e)
            return super().form_invalid(form)
        except InvalidColumnsExcepion as e:
            form.add_error('file', e)
            return super().form_invalid(form)
        else:
            return super().form_valid(form)  # うまくいったので、リダイレクトさせる

    def get_context_data(self, **kwargs):
        """
        フォームの選択肢を絞り込む
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        login_user = self.request.user

        # 選択可能な共有ユーザーを同一ワークスペースで絞り込み、作成者は除外する
        shared_edit_user = form.fields['shared_edit_user']
        shared_view_user = form.fields['shared_view_user']
        shared_edit_user.queryset = User.objects.filter(
            workspace=login_user.workspace.pk)
        shared_view_user.queryset = User.objects.filter(
            workspace=login_user.workspace.pk)

        # 選択可能な共有グループを同一ワークスペースで絞り込む
        shared_edit_group = form.fields['shared_edit_group']
        shared_view_group = form.fields['shared_view_group']
        shared_edit_group.queryset = MyGroup.objects.filter(
            workspace=login_user.workspace.pk)
        shared_view_group.queryset = MyGroup.objects.filter(
            workspace=login_user.workspace.pk)

        # 選択可能な営業担当者を同一ワークスペースで絞り込む
        sales_person = form.fields['sales_person']
        sales_person.queryset = User.objects.filter(
            workspace=login_user.workspace.pk)

        return ctx


class ContactInfoCreateView(LoginRequiredMixin, CreateView):
    """ ユーザーごとのコンタクト情報一覧画面からのコンタクト情報登録 """
    model = ContactInfo
    form_class = ContactInfoForm
    success_url = reverse_lazy('contactinfo_by_user_list')

    def post(self, request, **kwargs):
        # コンタクト情報の対応種別に応じて顧客情報の各種済フラグを立てる
        try:
            contact_type = request.POST['contact_type']
            target_customer_pk = request.POST['target_customer']
        except:
            return super().post(request, **kwargs)
        target_customer = CustomerInfo.objects.get(pk=target_customer_pk)
        # 対象顧客が同一ワークスペースでなければ何もしない
        if not target_customer.workspace == request.user.workspace:
            return super().post(request, **kwargs)
        if contact_type == '0':  # 対応種別が訪問かつ訪問済みの場合
            try:
                contact_visited_flg = request.POST['visited_flg']
            except:
                return super().post(request, **kwargs)
            if contact_visited_flg:
                target_customer.visited_flg = True
        elif contact_type == '2':  # 対応種別が架電（アウトバウンドの場合）（なおインバウンドの場合は架電済みとはみなさない）
            target_customer.tel_called_flg = True
        elif contact_type == '3':  # 対応種別がメールの場合
            target_customer.mail_sent_flg = True
        elif contact_type == '4':  # 対応種別がFAXの場合
            target_customer.fax_sent_flg = True
        elif contact_type == '5':  # 対応種別がDMの場合
            target_customer.dm_sent_flg = True
        else:
            return super().post(request, **kwargs)
        target_customer.save()
        return super().post(request, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_context_data(self, **kwargs):
        """
        フォームの選択肢を絞り込む
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        login_user = self.request.user
        target_customer = form.fields['target_customer']

        try:
            pk = self.kwargs['pk']
        except:
            # 選択可能な対象顧客を同一ワークスペースかつ自分が対応中の顧客で絞り込む
            target_customer.queryset = CustomerInfo.objects.filter(
                workspace=login_user.workspace.pk).filter(
                    sales_person=login_user, action_status='2')
        else:
            # 選択可能な対象顧客をPKで指定された顧客のみにする
            target_customer.queryset = CustomerInfo.objects.filter(
                workspace=login_user.workspace.pk, pk=pk)

        # 選択可能な対応者をログインユーザーのみにする
        operator = form.fields['operator']
        operator.queryset = User.objects.filter(pk=login_user.pk)

        return ctx

    def form_valid(self, form):
        """
        フォームのバリデーション成功後、遷移先を判断
        """
        # 対象顧客が同一ワークスペースでなければ何もしない
        target_customer_pk = self.request.POST['target_customer']
        target_customer = CustomerInfo.objects.get(pk=target_customer_pk)
        if not target_customer.workspace == self.request.user.workspace:
            return redirect('index')

        # フォームの内容を保存
        form.save()

        return super().form_valid(form)


class ContactInfoFromCustomerCreateView(ContactInfoCreateView):
    """ 顧客情報一覧画面からのコンタクト情報登録 """

    def form_valid(self, form):
        """
        フォームのバリデーション成功後、遷移先を判断
        """
        # 対象顧客が同一ワークスペースでなければ何もしない
        target_customer_pk = self.request.POST['target_customer']
        target_customer = CustomerInfo.objects.get(pk=target_customer_pk)
        if not target_customer.workspace == self.request.user.workspace:
            return redirect('index')

        # フォームの内容を保存
        form.save()

        pk = self.kwargs['pk']
        # 顧客毎のコンタクト一覧に遷移する
        return redirect('contactinfo_by_customer_list', pk)


class ContactInfoUpdateView(LoginRequiredMixin, UpdateView):
    """ 更新画面（コンタクト情報） """
    model = ContactInfo
    form_class = ContactInfoForm
    success_url = reverse_lazy('contactinfo_by_user_list')

    def post(self, request, **kwargs):
        # コンタクト情報の対応種別に応じて顧客情報の各種済フラグを立てる
        try:
            contact_type = request.POST['contact_type']
            target_customer_pk = request.POST['target_customer']
        except:
            return super().post(request, **kwargs)
        target_customer = CustomerInfo.objects.get(pk=target_customer_pk)
        if contact_type == '0':  # 対応種別が訪問かつ訪問済みの場合
            try:
                contact_visited_flg = request.POST['visited_flg']
            except:
                return super().post(request, **kwargs)
            if contact_visited_flg:
                target_customer.visited_flg = True
        elif contact_type == '2':  # 対応種別が架電（アウトバウンドの場合）（なおインバウンドの場合は架電済みとはみなさない）
            target_customer.tel_called_flg = True
        elif contact_type == '3':  # 対応種別がメールの場合
            target_customer.mail_sent_flg = True
        elif contact_type == '4':  # 対応種別がFAXの場合
            target_customer.fax_sent_flg = True
        elif contact_type == '5':  # 対応種別がDMの場合
            target_customer.dm_sent_flg = True
        else:
            return super().post(request, **kwargs)
        target_customer.save()
        return super().post(request, **kwargs)

    def get_queryset(self):
        return ContactInfo.objects.filter(delete_flg='False')

    def dispatch(self, request, *args, **kwargs):
        target = ContactInfo.objects.get(pk=self.kwargs['pk'])
        # コンタクト情報の更新は、以下の条件を満たす場合のみ実施できる
        # ・ワークスペースに所属し、有効になっている
        # ・コンタクト情報の対象顧客が同一ワークスペース
        if request.user.is_workspace_active and target.target_customer.workspace == request.user.workspace:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_context_data(self, **kwargs):
        """
        フォームの選択肢を絞り込む
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']

        # 対象顧客と対応者をHiddenに変える
        target_customer = form.fields['target_customer']
        target_customer.widget = forms.HiddenInput()
        operator = form.fields['operator']
        operator.widget = forms.HiddenInput()

        return ctx


class ContactInfoFromCustomerUpdateView(ContactInfoUpdateView):
    """ 更新画面（コンタクト情報） --顧客情報一覧から遷移した場合-- """

    def form_valid(self, form):
        """
        フォームのバリデーション成功後、遷移先を判断
        """
        # フォームの内容を保存
        form.save()

        # 顧客毎のコンタクト一覧に遷移する
        pk = ContactInfo.objects.get(pk=self.kwargs['pk']).target_customer.pk
        return redirect('contactinfo_by_customer_list', pk)


class ContactInfoByCustomerDeleteView(LoginRequiredMixin, TemplateView):
    """ 顧客情報毎一覧からの削除処理（コンタクト情報） """
    model = ContactInfo

    def get(self, request, **kwargs):
        target = ContactInfo.objects.get(pk=self.kwargs['pk'])
        target.delete_flg = True
        target.save()
        target_customer_pk = target.target_customer.pk

        return redirect('contactinfo_by_customer_list', pk=target_customer_pk)

    def dispatch(self, request, *args, **kwargs):
        target = ContactInfo.objects.get(pk=self.kwargs['pk'])
        # コンタクト情報の削除は、以下の条件を満たす場合のみ実施できる
        # ・ワークスペースに所属し、有効になっている
        # ・コンタクト情報の対象顧客が同一ワークスペース
        if request.user.is_workspace_active and target.target_customer.workspace == request.user.workspace:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class ContactInfoByUserDeleteView(LoginRequiredMixin, TemplateView):
    """ ユーザー毎一覧からの削除処理（コンタクト情報） """
    model = ContactInfo

    def get(self, request, **kwargs):
        target = ContactInfo.objects.get(pk=self.kwargs['pk'])
        target.delete_flg = True
        target.save()
        return redirect('contactinfo_by_user_list')

    def dispatch(self, request, *args, **kwargs):
        target = ContactInfo.objects.get(pk=self.kwargs['pk'])
        # コンタクト情報の削除は、以下の条件を満たす場合のみ実施できる
        # ・ワークスペースに所属し、有効になっている
        # ・コンタクト情報の対象顧客が同一ワークスペース
        if request.user.is_workspace_active and target.target_customer.workspace == request.user.workspace:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class ContactInfoDetailView(LoginRequiredMixin, DetailView):
    """ 詳細画面（コンタクト情報） """
    model = ContactInfo

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        """
        以下の条件に合致するコンタクト情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
        """
        return ContactInfo.objects.filter(
            delete_flg='False',
            target_customer__in=CustomerInfo.objects.filter(
                workspace=self.request.user.workspace))


class ContactInfoByCustomerListView(LoginRequiredMixin, PaginationMixin,
                                    FilterView):
    """ 一覧画面（顧客毎のコンタクト情報） """

    model = ContactInfo
    filterset_class = ContactInfoFilter
    template_name = 'sfa/contactinfo_by_customer_list.html'

    # pure_pagination用設定
    paginate_by = 30
    object = ContactInfo

    def get_queryset(self):
        """
        以下の条件に合致するコンタクト情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         ・対象顧客が指定された顧客と一致
        """
        return ContactInfo.objects.filter(
            delete_flg='False',
            target_customer__in=CustomerInfo.objects.filter(
                workspace=self.request.user.workspace)).filter(
                    target_customer=self.kwargs['pk']).order_by(
                        '-contact_timestamp')

    def dispatch(self, request, *args, **kwargs):
        target_customer = CustomerInfo.objects.get(pk=kwargs['pk'])
        # 顧客ごとのコンタクト情報一覧画面は、以下の条件を満たす場合のみ表示できる
        # ・ワークスペースに所属し、有効になっている
        # ・対象顧客が同一ワークスペース
        if request.user.is_workspace_active and target_customer.workspace == request.user.workspace:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_context_data(self, **kwargs):
        """
        ターゲットの顧客情報をテンプレート側に渡す
        """
        ctx = super().get_context_data(**kwargs)
        ctx['target_customer_pk'] = self.kwargs['pk']
        ctx['target_customer_name'] = CustomerInfo.objects.get(
            pk=self.kwargs['pk']).customer_name
        return ctx


class ContactInfoByUserListView(LoginRequiredMixin, PaginationMixin,
                                FilterView):
    """ 一覧画面（ユーザー毎のコンタクト情報） """

    model = ContactInfo
    filterset_class = ContactInfoFilter
    template_name = 'sfa/contactinfo_by_user_list.html'

    # pure_pagination用設定
    paginate_by = 30
    object = ContactInfo

    def get_queryset(self):
        """
        以下の条件に合致するコンタクト情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         ・対応者が自分
        """
        return ContactInfo.objects.filter(
            delete_flg='False',
            target_customer__in=CustomerInfo.objects.filter(
                workspace=self.request.user.workspace)).filter(
                    operator=self.request.user).order_by('-contact_timestamp')

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class AddressInfoCreateView(LoginRequiredMixin, CreateView):
    """ 登録画面（連絡先情報） """
    model = AddressInfo
    form_class = AddressInfoForm
    success_url = reverse_lazy('address_info_list')

    def post(self, request, **kwargs):
        """
        作成者と修正者およびワークスペースの自動入力
        """
        request.POST = request.POST.copy()
        # ログインユーザー情報の取得
        user = request.user
        # 作成者と修正者にログインユーザーを設定
        request.POST['author'] = user.pk
        request.POST['modifier'] = user.pk
        # ワークスペースにログインユーザーの所属ワークスペースを設定
        request.POST['workspace'] = user.workspace.pk

        return super().post(request, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class AddressInfoUpdateView(LoginRequiredMixin, UpdateView):
    """ 更新画面（連絡先情報） """
    model = AddressInfo
    form_class = AddressInfoForm
    success_url = reverse_lazy('address_info_list')

    def post(self, request, **kwargs):
        """
        修正者の自動入力
        """
        request.POST = request.POST.copy()
        # ログインユーザー情報の取得
        user = request.user
        # 修正者にログインユーザーを設定
        request.POST['modifier'] = user.pk
        return super().post(request, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class AddressInfoListView(PaginationMixin, ListView):
    """ 一覧画面（連絡先情報） """

    model = AddressInfo
    template_name = 'sfa/addressinfo_list.html'

    # pure_pagination用設定
    paginate_by = 30
    object = AddressInfo

    def get_queryset(self):
        """
        以下の条件に合致するコンタクト情報が処理の対象となる
         AND条件
         ・同一ワークスペース
         ・作成者がログインユーザーと一致
        """
        return AddressInfo.objects.filter(
            workspace=self.request.user.workspace).order_by(
                'related_flg',
                '-created_timestamp',
            )

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class AddressInfoDetailView(LoginRequiredMixin, DetailView):
    """ 詳細画面（連絡先情報） """
    model = AddressInfo

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        """
        以下の条件に合致する連絡先情報が処理の対象となる
         AND条件
         ・同一ワークスペース
        """
        return AddressInfo.objects.filter(
            workspace=self.request.user.workspace)


class AddressInfoDeleteView(LoginRequiredMixin, DeleteView):
    """ 連絡先情報の削除 """
    model = AddressInfo
    success_url = reverse_lazy('address_info_list')

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_queryset(self):
        """
        以下の条件に合致する連絡先情報が処理の対象となる
         AND条件
         ���同一ワークスペース
        """
        return AddressInfo.objects.filter(
            workspace=self.request.user.workspace)


class InvalidColumnsExcepion(Exception):
    """CSVの列が足りなかったり多かったりしたらこのエラー"""
    pass


class InvalidSourceExcepion(Exception):
    """CSVの読みとり中にUnicodeDecordErrorが出たらこのエラー"""
    pass


class AddressInfoImportView(generic.FormView):
    """SkyDeskからエクスポートしたCSVファイルをインポートする処理"""
    template_name = 'sfa/addressinfo_import.html'
    success_url = reverse_lazy('address_info_list')
    form_class = AddressInfoUploadForm
    number_of_columns = 34  # 列の数を定義しておく。各行の列がこれかどうかを判断する

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def save_csv(self, form):
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csvfile = io.TextIOWrapper(
            form.cleaned_data['file'], encoding='Shift_JISx0213')
        reader = csv.reader(csvfile)
        index = 1  # 1行目でのUnicodeDecodeError対策。for文の初回のnextでエラーになるとiの値がない為
        try:
            # indexは、現在の行番号。エラーの際に補足情報として使う
            for index, row in enumerate(reader, 1):
                # 列数が違う場合
                if len(row) != self.number_of_columns:
                    raise InvalidColumnsExcepion(
                        '{0}行目が変です。本来の列数: {1}, {0}行目の列数: {2}'.format(
                            index, self.number_of_columns, len(row)))

                # 問題なければ、この行は保存する。(実際には、form_validのwithブロック終了後に正式に保存される)
                if index == 1:
                    continue
                addressinfo = AddressInfo.objects.create()
                addressinfo.last_name = row[1]
                addressinfo.first_name = row[2]
                addressinfo.last_name_kana = row[3]
                addressinfo.first_name_kana = row[4]
                addressinfo.post = row[5]
                addressinfo.customer_name = row[6]
                addressinfo.customer_name_kana = row[7]
                addressinfo.mail_address = row[8]
                addressinfo.phone_number = row[9]
                addressinfo.fax_number = row[10]
                addressinfo.major_organization = row[11]
                addressinfo.middle_organization = row[12]
                addressinfo.country = row[13]
                addressinfo.zip_code = row[14]
                addressinfo.address1 = row[15]
                addressinfo.address2 = row[16]
                addressinfo.address3 = row[17]
                addressinfo.department_name = row[18]
                addressinfo.mobile_phone_number = row[19]
                addressinfo.url = row[20]
                addressinfo.zip_code_2 = row[21]
                addressinfo.prefectures_2 = row[22]
                addressinfo.city_2 = row[23]
                addressinfo.address_2 = row[24]
                addressinfo.building_name_2 = row[25]
                addressinfo.office_2 = row[26]
                addressinfo.phone_number_2 = row[27]
                addressinfo.fax_number_2 = row[28]
                addressinfo.workspace = self.request.user.workspace
                addressinfo.author = self.request.user
                addressinfo.modifier = self.request.user
                addressinfo.save()

        except Exception as e:
            print(e)
            raise InvalidSourceExcepion(
                '{}行目でインポートに失敗しました。正しいCSVファイルか確認ください。'.format(index))

    def form_valid(self, form):
        try:
            # CSVの100行目でエラーがおきたら、前の99行分は保存されないようにする
            with transaction.atomic():
                self.save_csv(form)
        # 今のところは、この2つのエラーは同様に対処します。
        except InvalidSourceExcepion as e:
            form.add_error('file', e)
            return super().form_invalid(form)
        except InvalidColumnsExcepion as e:
            form.add_error('file', e)
            return super().form_invalid(form)
        else:
            return super().form_valid(form)  # うまくいったので、リダイレクトさせる


class VisitTargetFilterView(ContactInfoByUserListView):
    """訪問先リスト画面"""
    template_name = 'sfa/visit_target_filter.html'

    def get_queryset(self):
        """
        以下の条件に合致するコンタクト情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         ・対応者が自分
        以下の条件でソート
         ・訪問開始時刻（予定）の昇順
        """
        return ContactInfo.objects.filter(
            delete_flg='False',
            target_customer__in=CustomerInfo.objects.filter(
                workspace=self.request.user.workspace)).filter(
                    operator=self.request.user).order_by('start_time_plan')

    def get(self, request, **kwargs):
        """
        検索条件の保存と復元およびあいまい検索の実装
        """
        if request.GET:
            request.GET = request.GET.copy()
            # 検索条件をセッションに保存する
            request.session['contact_info_query'] = request.GET

        else:
            # セッションから検索条件を復元
            request.GET = request.GET.copy()
            if 'contact_info_query' in request.session.keys():
                for key in request.session['contact_info_query'].keys():
                    request.GET[key] = request.session['contact_info_query'][
                        key]
        # 対応種別は「訪問」で固定
        request.GET['contact_type'] = '0'
        # 訪問日の設定
        visit_date = request.GET[
            'visit_date'] if 'visit_date' in request.GET else None
        if not visit_date:
            visit_date = datetime.datetime.now(
                timezone('Asia/Tokyo')).strftime("%Y-%m-%d")
        request.GET['visit_date'] = visit_date
        request.GET['visit_date_plan'] = visit_date
        # 以下の検索条件は予期せぬ動きを引き起こすため削除
        request.GET['visit_date_act'] = None
        request.GET['contact_timestamp_gte'] = None
        request.GET['contact_timestamp_lte'] = None

        # 一覧画面切り替え時に存在しないページを指定した場合のエラー回避処理
        curr_page = '1'
        if 'page' in request.GET:
            curr_page = request.GET['page']
        p = self.get_paginator(
            queryset=self.get_queryset(), per_page=self.paginate_by)
        if int(curr_page) > p.num_pages:  # 指定したページが全体よりも大きければ1ページ目を表示
            request.GET['page'] = '1'

        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        """
        検索条件をテンプレートの表示用に渡す
        """
        ctx = super().get_context_data(**kwargs)
        visit_date = self.request.GET['visit_date']
        ctx['visit_date'] = visit_date

        visit_act_count = ContactInfo.objects.filter(
            delete_flg=False,
            operator=self.request.user,
            contact_type='0',
            visit_date_act=visit_date,
            visited_flg=True).count()  # 訪問実績件数

        ctx['visit_act_count'] = visit_act_count

        visit_plan_count = ContactInfo.objects.filter(
            delete_flg=False,
            operator=self.request.user,
            contact_type='0',
            visit_date_plan=visit_date).count()  # 訪問予定件数

        ctx['visit_plan_count'] = visit_plan_count
        # 任意コードを用いて外部システムを呼び出すURL1
        try:
            ctx['webhook_url1'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url1
        except:
            ctx['webhook_url1'] = ''
        # 任意コードを用いて外部システムを呼び出すURL2
        try:
            ctx['webhook_url2'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url2
        except:
            ctx['webhook_url2'] = ''
        # 任意コードを用いて外部システムを呼び出すURL3
        try:
            ctx['webhook_url3'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url3
        except:
            ctx['webhook_url3'] = ''

        return ctx


class VisitTargetMapView(VisitTargetFilterView):
    """訪問先リスト地図画面"""
    template_name = 'sfa/visit_target_map.html'

    def get_context_data(self, **kwargs):
        """
        地図の表示に必要な情報を生成する
        """
        ctx = super().get_context_data(**kwargs)
        contactinfo_list = ctx['contactinfo_list']

        markers = []

        for contactinfo in contactinfo_list:
            target = contactinfo.target_customer
            if not (target.latitude or target.longitude):
                continue
            marker = {
                'name': target.customer_name,
                'address': target.address1 + target.address2 + target.address3,
                'lat': target.latitude,
                'lng': target.longitude,
                'visited': contactinfo.visited_flg
            }
            markers.append(marker)
        ctx['markers'] = json.dumps(
            markers, ensure_ascii=False, default=DecimalDefaultProc)
        return ctx


class VisitPlanCreateView(ContactInfoCreateView):
    """訪問予定の新規作成"""
    form_class = VisitPlanForm
    template_name = 'sfa/contactinfo_form.html'
    success_url = reverse_lazy('visit_target_filter')

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['contact_type'] = '0'  # コンタクト種別を「訪問」に設定
        initial['operator'] = self.request.user  # 対応者をログインユーザーに設定
        if 'contact_info_query' in self.request.session:
            query = self.request.session['contact_info_query']
            initial['visit_date_plan'] = query[
                'visit_date'] if 'visit_date' in query else None  # 訪問日_予定に表示中の訪問予定/実績の日付を設定
        return initial


class VisitPlanUpdateView(ContactInfoUpdateView):
    """訪問予定の更新"""
    form_class = VisitPlanForm
    template_name = 'sfa/contactinfo_form.html'
    success_url = reverse_lazy('visit_target_filter')

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['contact_type'] = '0'  # コンタクト種別を「訪問」に設定
        initial['operator'] = self.request.user  # 対応者をログインユーザーに設定
        return initial


class VisitHistoryCreateView(ContactInfoCreateView):
    """訪問実績の新規作成"""
    form_class = VisitHistoryForm
    template_name = 'sfa/contactinfo_form.html'
    success_url = reverse_lazy('visit_target_filter')

    def form_valid(self, form):
        """訪問予定日時と訪問済みフラグを自動更新する"""
        form.instance.visited_flg = True
        form.instance.visit_date_plan = form.instance.visit_date_act
        form.instance.start_time_plan = form.instance.start_time_act
        form.instance.end_time_plan = form.instance.end_time_act
        return super().form_valid(form)

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['contact_type'] = '0'  # コンタクト種別を「訪問」に設定
        initial['operator'] = self.request.user  # 対応者をログインユーザーに設定
        if 'contact_info_query' in self.request.session:
            query = self.request.session['contact_info_query']
            initial['visit_date_act'] = query[
                'visit_date'] if 'visit_date' in query else None  # 訪問日_実績に表示中の訪問予定/実績の日付を設定
        return initial


class VisitPlanFromCustomerCreateView(ContactInfoCreateView):
    """ 顧客情報一覧画面からの訪問予定登録 """
    form_class = VisitPlanForm
    success_url = reverse_lazy('visit_target_filter')


class VisitHistoryFromCustomerCreateView(VisitHistoryCreateView):
    """ 顧客情報一覧画面からの訪問実績登録 """
    form_class = VisitHistoryForm
    success_url = reverse_lazy('visit_target_filter')


class VisitHistoryUpdateView(ContactInfoUpdateView):
    """訪問実績の更新"""
    form_class = VisitHistoryForm
    template_name = 'sfa/contactinfo_form.html'
    success_url = reverse_lazy('visit_target_filter')

    def get_context_data(self, **kwargs):
        """
        フォームの属性を変更
        """
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        # 訪問日_実績をHiddenに変える
        visit_date_act = form.fields['visit_date_act']
        visit_date_act.widget = forms.HiddenInput()
        return ctx

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['contact_type'] = '0'  # コンタクト種別を「訪問」に設定
        initial['operator'] = self.request.user  # 対応者をログインユーザーに設定
        initial['visited_flg'] = True  # 訪問済みフラグを設定
        # 訪問予定日時を訪問実績日時のデフォルト値に設定
        contactinfo = ContactInfo.objects.get(pk=self.kwargs['pk'])
        initial['visit_date_act'] = contactinfo.visit_date_plan
        initial['start_time_act'] = contactinfo.start_time_plan
        initial['end_time_act'] = contactinfo.end_time_plan
        return initial


class VisitPlanOrHistoryDeleteView(ContactInfoByUserDeleteView):
    """ 訪問予定/実績の削除 """

    def get(self, request, **kwargs):
        target = ContactInfo.objects.get(pk=self.kwargs['pk'])
        target.delete_flg = True
        target.save()
        return redirect('visit_target_filter')


class CallHistoryCreateView(ContactInfoCreateView):
    """架電実績の新規作成"""
    form_class = CallHistoryForm
    template_name = 'sfa/call_history_form.html'
    success_url = reverse_lazy('call_history_filter')

    def get_initial(self):
        """デフォルト値の設定"""
        pk = self.kwargs['pk']
        target_customer = CustomerInfo.objects.get(pk=pk)
        initial = super().get_initial()
        initial['contact_type'] = '2'  # コンタクト種別を「架電（アウトバウンド）」に設定
        initial['operator'] = self.request.user  # 対応者をログインユーザーに設定
        initial[
            'target_person'] = target_customer.contact_name  # 顧客側担当者名を対象顧客の担当者名に設定
        initial[
            'tel_number'] = target_customer.tel_number1  # 顧客情報の電話番号１を連絡先電話番号に設定

        return initial

    def get_context_data(self, **kwargs):
        """
        架電実績入力画面へ各種情報を引き渡す
        """
        ctx = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        call_target_customer = CustomerInfo.objects.get(pk=pk)
        ctx['call_target_customer'] = call_target_customer  # 架電対象顧客の情報
        # IP電話の呼び出し用URL
        try:
            ctx['ip_phone_call_url'] = self.request.user.workspace.workspaceenvironmentsetting.ip_phone_call_url
        except:
            ctx['ip_phone_call_url'] = ''
        return ctx


class CallHistoryFilterView(ContactInfoByUserListView):
    """架電（アウトバウンド）履歴一覧を表示する"""
    template_name = 'sfa/call_history_filter.html'

    def get_queryset(self):
        """
        以下の条件に合致するコンタクト情報が処理の対象となる
         AND条件
         ・削除フラグが立っていない
         ・同一ワークスペース
         ・対応者が自分
        以下の条件でソート
         ・対応日時の降順
        """
        return ContactInfo.objects.filter(
            delete_flg='False',
            target_customer__in=CustomerInfo.objects.filter(
                workspace=self.request.user.workspace)).filter(
                    operator=self.request.user).order_by('-contact_timestamp')

    def get(self, request, **kwargs):
        """
        検索条件の保存と復元およびあいまい検索の実装
        """
        if request.GET:
            request.GET = request.GET.copy()
            # 検索条件をセッションに保存する
            request.session['contact_info_query'] = request.GET

        else:
            # セッションから検索条件を復元
            request.GET = request.GET.copy()
            if 'contact_info_query' in request.session.keys():
                for key in request.session['contact_info_query'].keys():
                    request.GET[key] = request.session['contact_info_query'][
                        key]
        # 対応種別は「架電（アウトバウンド）」で固定
        request.GET['contact_type'] = '2'
        # コンタクト実施日の設定
        contact_date = request.GET[
            'contact_date'] if 'contact_date' in request.GET else None
        if not contact_date:
            contact_date = datetime.datetime.now(
                timezone('Asia/Tokyo')).strftime("%Y-%m-%d")

        contact_date_gte = contact_date + " 0:0:0"
        contact_date_lte = contact_date + " 23:59:59"

        request.GET['contact_date'] = contact_date
        request.GET['contact_timestamp_gte'] = contact_date_gte
        request.GET['contact_timestamp_lte'] = contact_date_lte
        # 以下の検索条件は予期せぬ動きを引き起こすため削除
        request.GET['visit_date_plan'] = None
        request.GET['visit_date_act'] = None

        # 一覧画面切り替え時に存在しないページを指定した場合のエラー回避処理
        curr_page = '1'
        if 'page' in request.GET:
            curr_page = request.GET['page']
        p = self.get_paginator(
            queryset=self.get_queryset(), per_page=self.paginate_by)
        if int(curr_page) > p.num_pages:  # 指定したページが全体よりも大きければ1ページ目を表示
            request.GET['page'] = '1'

        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        """
        検索条件をテンプレートの表示用に渡す
        """
        ctx = super().get_context_data(**kwargs)
        contact_date = self.request.GET['contact_date']
        ctx['contact_date'] = contact_date
        contact_timestamp_gte = self.request.GET['contact_timestamp_gte']
        contact_timestamp_lte = self.request.GET['contact_timestamp_lte']
        outbound_count = ContactInfo.objects.filter(
            delete_flg=False,
            operator=self.request.user,
            contact_type='2',
            contact_timestamp__gte=contact_timestamp_gte,
            contact_timestamp__lte=contact_timestamp_lte,
            called_flg=True).count()  # 架電（アウトバウンド）の実績件数
        ctx['outbound_count'] = outbound_count
        # 任意コードを用いて外部システムを呼び出すURL1
        try:
            ctx['webhook_url1'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url1
        except:
            ctx['webhook_url1'] = ''
        # 任意コードを用いて外部システムを呼び出すURL2
        try:
            ctx['webhook_url2'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url2
        except:
            ctx['webhook_url2'] = ''
        # 任意コードを用いて外部システムを呼び出すURL3
        try:
            ctx['webhook_url3'] = self.request.user.workspace.workspaceenvironmentsetting.webhook_url3
        except:
            ctx['webhook_url3'] = ''

        return ctx


class CallHistoryUpdateView(ContactInfoUpdateView):
    """架電（アウトバウンド）実績の更新"""
    form_class = CallHistoryForm
    template_name = 'sfa/call_history_form.html'
    success_url = reverse_lazy('call_history_filter')


class GetContactInfoCountView(LoginRequiredMixin, TemplateView):
    """コンタクトの実績件数を取得する"""
    template_name = 'sfa/get_contactinfo_count.html'

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_context_data(self, **kwargs):
        """
        集計開始時刻、集計終了時刻から各種コンタクト実績の件数を返す
        """
        contact_timestamp_gte = self.request.GET['contact_timestamp_gte']
        visit_date_gte = datetime.datetime.strptime(
            contact_timestamp_gte, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        contact_timestamp_lte = self.request.GET['contact_timestamp_lte']
        visit_date_lte = datetime.datetime.strptime(
            contact_timestamp_lte, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        outbound_count = ContactInfo.objects.filter(
            delete_flg=False,
            operator=self.request.user,
            contact_type='2',
            contact_timestamp__gte=contact_timestamp_gte,
            contact_timestamp__lte=contact_timestamp_lte,
            called_flg=True).count()  # 架電（アウトバウンド）の実績件数
        visit_plan_count = ContactInfo.objects.filter(
            delete_flg=False,
            operator=self.request.user,
            contact_type='0',
            visit_date_plan__gte=visit_date_gte,
            visit_date_plan__lte=visit_date_lte).count()  # 訪問予定件数
        visit_count = ContactInfo.objects.filter(
            delete_flg=False,
            operator=self.request.user,
            contact_type='0',
            visit_date_act__gte=visit_date_gte,
            visit_date_act__lte=visit_date_lte,
            visited_flg=True).count()  # 訪問実績件数
        ctx = super().get_context_data(**kwargs)
        results = {
            'results': [
                {
                    'outbound_count': outbound_count,
                    'visit_plan_count': visit_plan_count,
                    'visit_count': visit_count,
                },
            ]
        }
        ctx['results'] = json.dumps(results, ensure_ascii=False)

        return ctx


class GoalSettingCreateView(LoginRequiredMixin, CreateView):
    """ 目標設定を行う（新規作成） """
    model = GoalSetting
    form_class = GoalSettingForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['user'] = self.request.user  # 目標設定の対象ユーザーはログインユーザー
        return initial

    def form_valid(self, form):
        """Hidden値を書き換えられた場合の対策"""
        form.instance.user = self.request.user
        return super().form_valid(form)


class GoalSettingUpdateView(LoginRequiredMixin, UpdateView):
    """ 目標設定を行う（更新） """
    model = GoalSetting
    form_class = GoalSettingForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # 以下の条件をすべて満たす場合のみ設定可能
        # ・ワークスペースに所属し、有効になっている
        # ・変更対象が自分自身の目標
        if request.user.workspace and request.user.is_workspace_active and request.user.goalsetting.pk == kwargs['pk']:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class DashboardView(LoginRequiredMixin, TemplateView):
    """ダッシュボードを表示する"""
    template_name = 'sfa/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # ワークスペースに所属し、有効になっている場合のみ表示できる
        if request.user.workspace and request.user.is_workspace_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class WelcomeView(LoginRequiredMixin, TemplateView):
    """ウェルカムページを表示する"""
    template_name = 'sfa/welcome.html'


class WorkspaceEnvironmentSettingCreateView(LoginRequiredMixin, CreateView):
    """ ワークスペース環境設定を行う（新規作成） """
    model = WorkspaceEnvironmentSetting
    form_class = WorkspaceEnvironmentSettingForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # 以下の条件をすべて満たす場合のみ表示可能
        # ・ワークスペースに所属し、有効になっている
        # ・権限がオーナー
        if request.user.workspace and request.user.is_workspace_active and request.user.workspace_role == '2':
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['workspace'] = self.request.user.workspace  # 環境設定対象のワークス―ペース
        return initial

    def form_valid(self, form):
        """Hidden値を書き換えられた場合の対策"""
        form.instance.workspace = self.request.user.workspace
        return super().form_valid(form)


class WorkspaceEnvironmentSettingUpdateView(LoginRequiredMixin, UpdateView):
    """ ワークスペース環境設定を行う（更新） """
    model = WorkspaceEnvironmentSetting
    form_class = WorkspaceEnvironmentSettingForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # 以下の条件をすべて満たす場合のみ更新可能
        # ・ワークスペースに所属し、有効になっている
        # ・権限がオーナー
        # ・更新対象が自分自身のワークスペースと一致
        if request.user.workspace and request.user.is_workspace_active and request.user.workspace_role == '2' and request.user.workspace.workspaceenvironmentsetting.pk == kwargs['pk']:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')


class CustomerInfoDisplaySettingCreateView(LoginRequiredMixin, CreateView):
    """ 顧客情報の表示制御をワークスペース毎に設定する（新規作成） """
    model = CustomerInfoDisplaySetting
    form_class = CustomerInfoDisplaySettingForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # 以下の条件をすべて満たす場合のみ表示可能
        # ・ワークスペースに所属し、有効になっている
        # ・権限がオーナー
        if request.user.workspace and request.user.is_workspace_active and request.user.workspace_role == '2':
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_initial(self):
        """デフォルト値の設定"""
        initial = super().get_initial()
        initial['workspace'] = self.request.user.workspace  # 環境設定対象のワークス―ペース
        return initial

    def form_valid(self, form):
        """Hidden値を書き換えられた場合の対策"""
        form.instance.workspace = self.request.user.workspace
        return super().form_valid(form)


class CustomerInfoDisplaySettingUpdateView(LoginRequiredMixin, UpdateView):
    """ 顧客情報の表示制御をワークスペース毎に設定する（更新） """
    model = CustomerInfoDisplaySetting
    form_class = CustomerInfoDisplaySettingForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # 以下の条件をすべて満たす場合のみ更新可能
        # ・ワークスペースに所属し、有効になっている
        # ・権限がオーナー
        # ・更新対象が自分自身のワークスペースと一致
        if request.user.workspace and request.user.is_workspace_active and request.user.workspace_role == '2' and request.user.workspace.workspaceenvironmentsetting.pk == kwargs['pk']:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('index')
