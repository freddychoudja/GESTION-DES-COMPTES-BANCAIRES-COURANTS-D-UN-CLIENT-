from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_comptes, name='liste_comptes'),
    path('dashboard/<int:compte_id>/', views.dashboard, name='dashboard'),
    path('depot/<int:compte_id>/', views.depot, name='depot'),
    path('retrait/<int:compte_id>/', views.retrait, name='retrait'),
    path('virement/<int:compte_id>/', views.virement, name='virement'),
]
