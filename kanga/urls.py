"""kanga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

from django.contrib import admin
from django.urls import path

from kanga import views


urlpatterns = [
    path('', views.home, name='home'),
    #
    path('assets/', views.assets, name='assets'),
    path('assets/<str:uuid>/', views.asset_detail, name='asset_detail'),
    #
    path('accounts/', views.accounts, name='accounts'),
    path('accounts/new', views.account_new, name='account_new'),
    path('accounts/<str:u>/edit', views.account_edit, name='account_edit'),
    path('accounts/<str:u>/delete', views.account_delete, name='account_delete'),
    path('accounts/<str:u>/view', views.account_view, name='account_view'),
    #
    path('messages/', views.messages, name='messages'),
    #
    path('groups/', views.groups, name='groups'),
    path('groups/new', views.group_new, name='group_new'),
    path('groups/<str:u>/edit', views.group_edit, name='group_edit'),
    path('groups/<str:u>/delete', views.group_delete, name='group_delete'),
    path('groups/<str:u>/view', views.group_view, name='group_view'),
    #
    path('targets/', views.targets, name='targets'),
    path('targets/new', views.target_new, name='target_new'),
    path('targets/import', views.targets_import, name='targets_import'),
    path('targets/<str:u>/view', views.target_view, name='target_view'),
    path('targets/<str:u>/edit', views.target_edit, name='target_edit'),
    path('targets/<str:u>/delete', views.target_delete, name='target_delete'),
    #
    path('templates/', views.templates, name='templates'),
    path('templates/new', views.template_new, name='template_new'),
    path('templates/<str:u>/edit', views.template_edit, name='template_edit'),
    path('templates/<str:u>/delete', views.template_delete, name='template_delete'),
    #
    path('plans/', views.plans, name='plans'),
    path('plans/new', views.plan_new, name='plan_new'),
    path('plans/<str:u>/edit', views.plan_edit, name='plan_edit'),
    path('plans/<str:u>/delete', views.plan_delete, name='plan_delete'),
    path('plans/<str:u>/view', views.plan_view, name='plan_view'),
    #
    path('results/', views.executions, name='executions'),
    path('results/<str:u>/view', views.execution_view, name='execution_view'),
    #
    path('admin/', admin.site.urls)
]
