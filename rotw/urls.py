"""rotw URL Configuration

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
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls import url


from main.views import CheckUser, UserView, PlanView, ActivityView, RemoveActivityView, RemoveAvailabilityView, \
    AvailabilityView, PlanDetailsView, RemovePlanView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rotw/', include('main.urls')),
    path('rotw/', include('django.contrib.auth.urls')),
    path('rotw/home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('check/', CheckUser.as_view()),
    re_path(r'^rotw/(?P<id>(\d)+)$', UserView.as_view()),
    re_path(r'^rotw/(?P<u_id>(\d)+)/(?P<p_id>(\d)+)$', PlanView.as_view()),
    re_path(r'^rotw/activity/(?P<id>(\d)+)$', ActivityView.as_view()),
    re_path(r'^rotw/availability/(?P<id>(\d)+)$', AvailabilityView.as_view()),
    url(r'^rotw/plan/remove/(?P<pk>(\d)+)$', RemovePlanView.as_view()),
    url(r'^rotw/activity/remove/(?P<pk>(\d)+)$', RemoveActivityView.as_view()),
    url(r'^rotw/availability/remove/(?P<pk>(\d)+)$', RemoveAvailabilityView.as_view()),
    url(r'^rotw/schedule_details/(?P<u_id>(\d)+)/(?P<p_id>(\d)+)$', PlanDetailsView.as_view()),
    # url(r'^rotw/schedule_recalculation/(?P<u_id>(\d)+)/(?P<p_id>(\d)+)$', ScheduleRecalculation.as_view()),
]
