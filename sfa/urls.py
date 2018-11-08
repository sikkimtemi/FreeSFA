from django.urls import path
from django.conf.urls import include
from django.contrib.auth import views
from .views import (
    WelcomeView,
    DashboardView,
    CustomerInfoFilterView,
    CustomerInfoMapView,
    CustomerInfoAreaSearchView,
    CustomerInfoGroupFilterView,
    CustomerInfoGroupMapView,
    CustomerInfoAllFilterView,
    CustomerInfoAllMapView,
    CustomerInfoDetailView,
    CustomerInfoCreateView,
    CustomerInfoUpdateView,
    CustomerInfoDeleteView,
    CustomerInfoImportView,
    ContactInfoCreateView,
    ContactInfoFromCustomerCreateView,
    VisitPlanFromCustomerCreateView,
    VisitHistoryFromCustomerCreateView,
    ContactInfoUpdateView,
    CustomerInfoBulkUpdateView,
    ContactInfoFromCustomerUpdateView,
    ContactInfoByCustomerDeleteView,
    ContactInfoByUserDeleteView,
    ContactInfoDetailView,
    ContactInfoByCustomerListView,
    ContactInfoByUserListView,
    AddressInfoCreateView,
    AddressInfoUpdateView,
    AddressInfoListView,
    AddressInfoDetailView,
    AddressInfoDeleteView,
    AddressInfoImportView,
    VisitTargetFilterView,
    VisitTargetMapView,
    VisitPlanCreateView,
    VisitPlanUpdateView,
    VisitHistoryCreateView,
    VisitHistoryUpdateView,
    VisitPlanOrHistoryDeleteView,
    CallHistoryCreateView,
    CallHistoryFilterView,
    CallHistoryUpdateView,
    GetContactInfoCountView,
    GoalSettingCreateView,
    GoalSettingUpdateView,
    WorkspaceEnvironmentSettingCreateView,
    WorkspaceEnvironmentSettingUpdateView,
    CustomerInfoDisplaySettingCreateView,
    CustomerInfoDisplaySettingUpdateView,
)
from django.contrib import admin

urlpatterns = [
    path('', WelcomeView.as_view(), name='index'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path(
        'customer_list_user/',
        CustomerInfoFilterView.as_view(),
        name='customer_list_user'),
    path(
        'customer_list_user_map/',
        CustomerInfoMapView.as_view(),
        name='customer_list_user_map'),
    path(
        'customer_list_group/',
        CustomerInfoGroupFilterView.as_view(),
        name='customer_list_group'),
    path(
        'customer_list_group_map/',
        CustomerInfoGroupMapView.as_view(),
        name='customer_list_group_map'),
    path(
        'customer_list_all/',
        CustomerInfoAllFilterView.as_view(),
        name='customer_list_all'),
    path(
        'customer_list_all_map/',
        CustomerInfoAllMapView.as_view(),
        name='customer_list_all_map'),
    path(
        'customer_area_search/',
        CustomerInfoAreaSearchView.as_view(),
        name='customer_area_search'),
    path('detail/<int:pk>/', CustomerInfoDetailView.as_view(), name='detail'),
    path('create/', CustomerInfoCreateView.as_view(), name='create'),
    path('update/<int:pk>/', CustomerInfoUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', CustomerInfoDeleteView.as_view(), name='delete'),
    path(
        'customer_info_import/',
        CustomerInfoImportView.as_view(),
        name='customer_info_import'),
    path(
        'contact_create/',
        ContactInfoCreateView.as_view(),
        name='contact_by_user_create'),
    path(
        'contact_from_customer_create/<int:pk>/',
        ContactInfoFromCustomerCreateView.as_view(),
        name='contact_from_customer_create'),
    path(
        'visit_plan_from_customer_create/<int:pk>/',
        VisitPlanFromCustomerCreateView.as_view(),
        name='visit_plan_from_customer_create'),
    path(
        'visit_history_from_customer_create/<int:pk>/',
        VisitHistoryFromCustomerCreateView.as_view(),
        name='visit_history_from_customer_create'),
    path(
        'contact_update/<int:pk>/',
        ContactInfoUpdateView.as_view(),
        name='contact_update'),
    path(
        'contact_from_customer_update/<int:pk>/',
        ContactInfoFromCustomerUpdateView.as_view(),
        name='contact_from_customer_update'),
    path(
        'contact_by_customer_delete/<int:pk>/',
        ContactInfoByCustomerDeleteView.as_view(),
        name='contact_by_customer_delete'),
    path(
        'contact_by_user_delete/<int:pk>/',
        ContactInfoByUserDeleteView.as_view(),
        name='contact_by_user_delete'),
    path(
        'contact_detail/<int:pk>/',
        ContactInfoDetailView.as_view(),
        name='contact_detail'),
    path(
        'contactinfo_by_customer_list/<int:pk>/',
        ContactInfoByCustomerListView.as_view(),
        name='contactinfo_by_customer_list'),
    path(
        'contactinfo_by_user_list/',
        ContactInfoByUserListView.as_view(),
        name='contactinfo_by_user_list'),
    path(
        'address_info_create/',
        AddressInfoCreateView.as_view(),
        name='address_info_create'),
    path(
        'address_info_update/<int:pk>/',
        AddressInfoUpdateView.as_view(),
        name='address_info_update'),
    path(
        'address_info_bulk_update/',
        CustomerInfoBulkUpdateView.as_view(),
        name='address_info_bulk_update'),
    path(
        'address_info_list/',
        AddressInfoListView.as_view(),
        name='address_info_list'),
    path(
        'address_info_detail/<int:pk>/',
        AddressInfoDetailView.as_view(),
        name='address_info_detail'),
    path(
        'address_info_delete/<int:pk>/',
        AddressInfoDeleteView.as_view(),
        name='address_info_delete'),
    path(
        'address_info_import/',
        AddressInfoImportView.as_view(),
        name='address_info_import'),
    path(
        'visit_target_filter/',
        VisitTargetFilterView.as_view(),
        name='visit_target_filter'),
    path(
        'visit_target_map/',
        VisitTargetMapView.as_view(),
        name='visit_target_map'),
    path(
        'visit_plan_create/',
        VisitPlanCreateView.as_view(),
        name='visit_plan_create'),
    path(
        'visit_plan_update/<int:pk>/',
        VisitPlanUpdateView.as_view(),
        name='visit_plan_update'),
    path(
        'visit_history_create/',
        VisitHistoryCreateView.as_view(),
        name='visit_history_create'),
    path(
        'visit_history_update/<int:pk>/',
        VisitHistoryUpdateView.as_view(),
        name='visit_history_update'),
    path(
        'visit_plan_or_history_delete/<int:pk>/',
        VisitPlanOrHistoryDeleteView.as_view(),
        name='visit_plan_or_history_delete'),
    path(
        'call_history_create/<int:pk>/',
        CallHistoryCreateView.as_view(),
        name='call_history_create'),
    path(
        'call_history_filter/',
        CallHistoryFilterView.as_view(),
        name='call_history_filter'),
    path(
        'call_history_update/<int:pk>/',
        CallHistoryUpdateView.as_view(),
        name='call_history_update'),
    path(
        'get_contactinfo_count/',
        GetContactInfoCountView.as_view(),
        name='get_contactinfo_count'),
    path(
        'goal_setting_create/',
        GoalSettingCreateView.as_view(),
        name='goal_setting_create'),
    path(
        'goal_setting_update/<int:pk>/',
        GoalSettingUpdateView.as_view(),
        name='goal_setting_update'),
    path(
        'workspace_environment_setting_create/',
        WorkspaceEnvironmentSettingCreateView.as_view(),
        name='workspace_environment_setting_create'),
    path(
        'workspace_environment_setting_update/<int:pk>/',
        WorkspaceEnvironmentSettingUpdateView.as_view(),
        name='workspace_environment_setting_update'),
    path(
        'customer_info_display_setting_create/',
        CustomerInfoDisplaySettingCreateView.as_view(),
        name='customer_info_display_setting_create'),
    path(
        'customer_info_display_setting_update/<int:pk>/',
        CustomerInfoDisplaySettingUpdateView.as_view(),
        name='customer_info_display_setting_update'),
]
