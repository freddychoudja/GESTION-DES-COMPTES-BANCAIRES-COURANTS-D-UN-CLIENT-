from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_clients, name='index'),
    path('clients/', views.liste_clients, name='liste_clients'),
    path('client/<int:client_id>/', views.profile_client, name='profile_client'),
    path('client/<int:client_id>/edit/', views.edit_client, name='edit_client'),
    path('client/<int:client_id>/new_compte/', views.create_compte, name='create_compte'),
    path('comptes/', views.liste_comptes, name='liste_comptes'),
    path('dashboard/<int:compte_id>/', views.dashboard, name='dashboard'),
    path('depot/<int:compte_id>/', views.depot, name='depot'),
    path('retrait/<int:compte_id>/', views.retrait, name='retrait'),
    path('virement/<int:compte_id>/', views.virement, name='virement'),
    path('telecharger_rib/<int:compte_id>/', views.telecharger_rib, name='telecharger_rib'),
    path('telecharger_releve/<int:compte_id>/', views.telecharger_releve, name='telecharger_releve'),
    path('statistiques/<int:compte_id>/', views.statistiques_compte, name='statistiques'),
]
