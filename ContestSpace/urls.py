from django.urls import path
from ContestSpace import views

urlpatterns = [
	path('', views.index, name='index'),
	path('<str:temp>', views.index, name = 'index'),
	path('contest/<str:temp>/', views.contests, name='contests'),
	path('team/new/', views.createteamform, name='createteamform'),
	path('manage_team/', views.manageteams, name='manageteams'),
	path('start/<str:temp>/', views.startcontest, name = 'startcontest'),
	path('problems/<str:temp>/<int:id>/', views.problems, name = 'problems'),
	path('result/<str:temp>/<int:id>/', views.showresult, name = 'showresult'),
]