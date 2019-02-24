"""whitelist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, re_path, include
from django.contrib.auth.views import LogoutView

from mojang.views import *
from twitch.views import *

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Social auth
    path('', include('social_django.urls', namespace='social')),
    path('logout', LogoutView.as_view(template_name='logout.html'), name='logout'),

    # Our views that aren't usernames
    path('', ExplainerView.as_view()),
    path('all', BrowseView.as_view(), name='whitelists'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('profile/whitelist', WhitelistView.as_view(), name='whitelist'),
    path('profile/whitelist/add', AddWhitelistView.as_view(), name='whitelist-add'),
    path('profile/whitelist/vip/add', AddVIPView.as_view(), name='add-vip'),
    path('profile/whitelist/vip/<int:id>/delete', RemoveVIPView.as_view(), name='remove-vip'),
    path('profile/whitelist/ban/add', AddBanView.as_view(), name='add-ban'),
    path('profile/whitelist/members/<int:id>/ban', BanUserView.as_view(), name='ban-user'),
    path('profile/whitelist/ban/<int:id>/delete', RemoveBanView.as_view(), name='remove-ban'),

    path('help/cname', CNameHelpView.as_view(), name='cname'),

    # The rest should be twitch usernames or related
    re_path(r'^(?P<username>[a-zA-Z0-9_]{4,25})/white-list.txt', WhitelistTXTView.as_view(), name='whitelist-txt'),
    re_path(r'^(?P<username>[a-zA-Z0-9_]{4,25})/whitelist.json', WhitelistJSONView.as_view(), name='whitelist-json'),
    re_path(r'^(?P<username>[a-zA-Z0-9_]{4,25})/join', TwitchJoinView.as_view(), name='broadcaster-join'),
    re_path(r'^(?P<username>[a-zA-Z0-9_]{4,25})$', TwitchConnectView.as_view(), name='broadcaster-connect'),
]
