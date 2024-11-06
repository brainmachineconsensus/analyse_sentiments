from django.urls import path
from .views import *

urlpatterns = [
    path('creation_compte', creation_compte, name='creation_compte'),
    path('suppression_compte/', delete_compte, name='suppresion_compte'),
    path('change_username/', change_username, name='change_username'),
    path('change_password/', change_password, name='change_password'),
    path('connexion/', connexion, name='connexion'),
    path('connectez_vous/', connectez_vous, name='connectez_vous'),
    path('', home, name='home'),
    path('activate/<uuid:activation_token>/', activate_compte, name='activate_compte'),
    path('compte_confirmation/', compte_confirmation, name='compte_confirmation'),
    path('demande_reset_mot_de_passe/', demande_reset_mot_de_passe, name='demande_reset_mot_de_passe'),
    path('reset_mot_de_passe/<str:reset_token>/', reset_mot_de_passe, name='reset_mot_de_passe'),
]