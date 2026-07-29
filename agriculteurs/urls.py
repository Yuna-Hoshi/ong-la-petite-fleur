from django.urls import path
from . import views

urlpatterns = [
    path('', views.page_connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('dashboard/', views.tableau_de_bord_analyse, name='dashboard_analyse'),
    path('liste/', views.liste_agriculteurs, name='liste_agriculteurs'),
    path('ajouter/', views.ajouter_agriculteur, name='ajouter_agriculteur'),
    path('modifier/<int:pk>/', views.modifier_agriculteur, name='modifier_agriculteur'),
    path('supprimer/<int:pk>/', views.supprimer_agriculteur, name='supprimer_agriculteur'),
    path('detail/<int:pk>/', views.detail_agriculteur, name='detail_agriculteur'),
    path('rapport/imprimer/', views.rapport_analyse_imprimable, name='rapport_analyse_imprimable'),
    
    # Gestion des deux noms possibles pour éviter les erreurs de templates
    path('export/excel/', views.exporter_donnees_excel, name='exporter_donnees_excel'),
    path('export/excel/', views.exporter_donnees_excel, name='export_excel'), # Alias
    
    path('export/pdf/', views.exporter_donnees_pdf, name='exporter_donnees_pdf'),
    path('export/pdf/', views.exporter_donnees_pdf, name='export_pdf'),       # Alias
    
    path('utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('utilisateurs/supprimer/<int:pk>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('utilisateurs/modifier/<int:pk>/', views.modifier_utilisateur, name='modifier_utilisateur'),
]