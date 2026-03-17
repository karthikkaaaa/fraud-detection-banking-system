from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user-dashboard/', views.user_dashboard, name='user-dashboard'),
    
    path('history/', views.user_history, name='history'),
    path("profile/", views.user_profile, name="profile"),
    path('check-balance/', views.check_balance, name='check_balance'),
    path("pay-phone/", views.pay_phone, name="pay_phone"),
    path("help/", views.help_request, name="help_request"),

    path('make-transaction/', views.make_transaction, name='make_transaction'),
    path('confirm/<int:transaction_id>/', views.confirm_transaction, name='confirm_transaction'),
    path('report-fraud/<int:transaction_id>/', views.report_fraud, name='report_fraud'),

    path('bank-login/', views.bank_login, name='bank_login'),
    path('bank-dashboard/', views.bank_dashboard, name='bank_dashboard'),
    path('update-status/<int:transaction_id>/<str:new_status>/', views.update_status, name='update_status'),
    path('customer/<int:user_id>/', views.customer_detail, name='customer_detail'),
    path("bank-complaints/", views.bank_complaints, name="bank_complaints"),
    path("complaint/<int:complaint_id>/", views.complaint_detail, name="complaint_detail"),
    
    path('staff-list/', views.staff_list, name='staff_list'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('customers/', views.customer_dashboard, name='customer_dashboard'),
    path('bank-history/', views.bank_history, name='bank_history'),
]