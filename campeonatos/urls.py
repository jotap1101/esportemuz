from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Campeonatos
    path('campeonatos/', views.campeonatos_list, name='campeonatos_list'),
    path('campeonatos/criar/', views.campeonato_create, name='campeonato_create'),
    path('campeonatos/<int:pk>/', views.campeonato_detail, name='campeonato_detail'),
    path('campeonatos/<int:pk>/editar/', views.campeonato_edit, name='campeonato_edit'),
    path('campeonatos/<int:pk>/excluir/', views.campeonato_delete, name='campeonato_delete'),
    path('campeonatos/<int:campeonato_id>/gerar-rodadas/', views.gerar_rodadas, name='gerar_rodadas'),
    
    # Equipes
    path('equipes/', views.equipes_list, name='equipes_list'),
    path('equipes/criar/', views.equipe_create, name='equipe_create'),
    path('equipes/<int:pk>/editar/', views.equipe_edit, name='equipe_edit'),
    
    # Partidas
    path('partidas/', views.partidas_list, name='partidas_list'),
    
    # API/AJAX
    path('api/equipes/', views.api_equipes, name='api_equipes'),
    path('api/classificacao/<int:campeonato_id>/', views.api_classificacao, name='api_classificacao'),
    path('api/registrar-resultado/', views.registrar_resultado, name='registrar_resultado'),
    path('api/adicionar-equipe-campeonato/', views.adicionar_equipe_campeonato, name='adicionar_equipe_campeonato'),
    path('api/remover-equipe-campeonato/', views.remover_equipe_campeonato, name='remover_equipe_campeonato'),
]
