from django.urls import path
from .views import (
    login_view,
    logout_view,
    register_view,
    AdminDashboardView,
    InspectorPanelView,
    create_client,
    manage_call_center,
    manage_inspectors,
    manage_user,
    change_password,
    reset_user_password,
    list_inspectors,
    list_clients,
)

urlpatterns = [
    # Authentication
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),  # Disabled for public
    
    # Dashboards
    path("admin_dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("inspector_panel/", InspectorPanelView.as_view(), name="inspector_panel"),
    
    # Admin: Manage Users
    path("admin/call-center/", manage_call_center, name="manage_call_center"),
    path("admin/inspectors/", manage_inspectors, name="manage_inspectors"),
    path("admin/users/<uuid:user_id>/", manage_user, name="manage_user"),
    path("admin/users/<uuid:user_id>/reset-password/", reset_user_password, name="reset_user_password"),

    # Password Management
    path("change-password/", change_password, name="change_password"),

    # Inspector: Create client
    path("create-client/", create_client, name="create_client"),

    # List inspectors (for Call Center and Admin)
    path("inspectors/", list_inspectors, name="list_inspectors"),

    # List clients (for Admin)
    path("admin/clients/", list_clients, name="list_clients"),
]