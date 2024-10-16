"""
URL configuration for ForumApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from boards import views
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.BoardListView.as_view(),name="home"),
    path('signup/',accounts_views.signup,name='signup'),
    path('login/',auth_views.LoginView.as_view(),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('password_change/',auth_views.PasswordChangeView.as_view(),name='password_change'),
    path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
    
    path('settings/accounts/',accounts_views.UserUpdateView.as_view(),name="my_account"),
    path('boards/<int:pk>',views.TopicListView.as_view(),name="board_topics"),
    path('boards/<int:pk>/new',views.new_topic,name="new_topic"),
    path('boards/<int:pk>/topics/<int:topic_pk>',views.PostListView.as_view(),name="topic_posts"),
    path('boards/<int:pk>/topics/<int:topic_pk>/reply',views.reply_topic,name="reply_topic"),
    path('boards/<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path("admin/", admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
