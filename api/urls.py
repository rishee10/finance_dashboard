from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
# from .views.auth_views    import RegisterView, LoginView, MeView
from .views.auth_views import RegisterView, LoginView, MeView
from .views.user_views    import UserListView, UserDetailView
from .views.record_views  import RecordListCreateView, RecordDetailView
from .views.dashboard_views import DashboardSummaryView, MonthlyTrendView, WeeklyTrendView

urlpatterns = [
    # Auth
    path('auth/register/',      RegisterView.as_view(),     name='register'),
    path('auth/login/',         LoginView.as_view(),         name='login'),
    path('auth/me/',            MeView.as_view(),            name='me'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),  name='token-refresh'),

    # User management (admin only)
    path('users/',              UserListView.as_view(),      name='user-list'),
    path('users/<int:pk>/',     UserDetailView.as_view(),    name='user-detail'),

    # Financial records
    path('records/',            RecordListCreateView.as_view(), name='record-list'),
    path('records/<int:pk>/',   RecordDetailView.as_view(),     name='record-detail'),

    # Dashboard / analytics (analyst + admin)
    path('dashboard/summary/',  DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/monthly/',  MonthlyTrendView.as_view(),     name='dashboard-monthly'),
    path('dashboard/weekly/',   WeeklyTrendView.as_view(),      name='dashboard-weekly'),
]