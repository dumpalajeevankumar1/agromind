from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ----------------------------
    # 🔐 Authentication Routes
    # ----------------------------
        path("", views.custom_login_view, name="custom_login"),  # Make custom login the root
    path("custom-login/", views.custom_login_view, name="custom_login"),
    path("login/", views.login_view, name="login"),
    path("home/", views.home, name="home"),
    # ...existing code...
    path("custom-login/", views.custom_login_view, name="custom_login"),
# ...existing code...
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # ----------------------------
    # 🔑 Password Reset (Django built-in)
    # ----------------------------
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="forgot_password.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete",
    ),

    # ----------------------------
    # 🧭 Dashboard Pages
    # ----------------------------
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/update-preferences/", views.update_preferences, name="update_preferences"),
    path("settings/change-password/", views.password_change_request, name="change_password_request"),
    path("settings/change-password/confirm/<uidb64>/<token>/", views.password_change_confirm, name="change_password_confirm"),

    # ----------------------------
    # 🚜 Equipment & Reports
    # ----------------------------
    path("equipment/", views.equipment_status, name="equipment"),
    path('reports/', views.reports, name='reports'),


    # ----------------------------
    # 🤖 Chatbot (Gemini API)
    # ----------------------------
    path("chatbot/", views.chatbot_view, name="chatbot"),
    path("api/chatbot/", views.farming_chatbot, name="farming_chatbot"),
    path('sensordata/', views.sensor_data, name='sensor_data'),
    path('api/sensordata/', views.sensor_data, name='sensor_data'),
]
