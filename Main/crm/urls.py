from django.conf.urls import url,include
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from . import views
from django.views.generic import ListView,DetailView
from .models import Agent,RelationLogHistory,Customer


urlpatterns = [
    url(r'^login/', login, {'template_name': 'login.html'}),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^agent/$', views.update_profile, name='register'),
    url(r'^add/$', login_required(views.update_cust)),
    url(r'^addagent/$', login_required(views.AddAgent)),
    url(r'^home/',login_required(views.home)),
    url(r'^cus/',login_required(views.CusDet)),
    url(r'(?P<pk>[0-9]+)/updatem/$',login_required(views.updatema)),
    # url(r'(?P<pk>[0-9]+)/updatea/$',login_required(views.updatead)),
    url(r'(?P<pk>[0-9]+)/updateag/$',login_required(views.updateag)),
    url(r'agents.xml$',login_required(views.xml1)),
    url(r'^aginfo/', login_required(views.AgentInfo), name='list'),
    url(r'(?P<pk>\d+)/logs/$',login_required(views.AddL),name="logs"),
    url(r'^(?P<pk>\d+)/addlog/$',login_required(views.AddL)),
    url(r'^as/',login_required(views.Ass)),
    url(r'^export/csv/$', login_required(views.export_users_csv), name='export_users_csv'),
    url(r'^export/xls/$', login_required(views.export_users_xls), name='export_users_xls'),
    url(r'^import/$', login_required(views.import_cus_csv)),
    url(r'^importx/$', login_required(views.import_data)),
    url(r'^export/pdf/$', login_required(views.pdf)),
    url(r'^request/$',views.requests),
    url(r'^(?P<pk>\d+)/validate/$',views.validate),
    url(r'^(?P<pk>\d+)/update/$',views.UpdateAgent),
    url(r'^main/',views.main,name="home"),
    url(r'^com/',views.CompanyEdit),
    url(r'^changepass/',login_required(views.ChangePassword)),


]



