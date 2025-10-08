"""
URL configuration for sgea project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from login import views
 
urlpatterns = [
    path('admin/', admin.site.urls),
    
    #Página incial
    path('cadastro', views.cadastro_usuarios, name = "cadastro"),
    
    #Verificar usuários cadastrados
    path("usuarios/", views.ver_usuarios, name = "listagem_usuarios"),
    
    #Operações com os usuários
    path("inscrever/<int:usuario_id>/<int:evento_id>/", views.inscricao_evento, name = "inscricao_evento"),
    path("deletar_usuario/<int:pk>/", views.deletar_usuario, name = "deletar_usuario"),
    path("meus_eventos/<int:usuario_id>/", views.usuario_eventos, name = "meus_eventos"),
    path("meus_certificados/", views.meus_certificados, name = "meus_certificados"),
    path("editar_usuario/", views.editar_usuario, name="editar_usuario"),
    
    #Operações com os eventos
    path("cadastro_eventos/", views.ev, name = 'ev'),
    path("eventos/", views.eventos, name = 'visu_eventos'),
    path("todos_eventos/", views.todos_eventos, name = "even"),
    path("deletar_evento/<int:pk>/", views.deletar_evento, name = "deletar_evento"),
    path("editar_evento/<int:pk>", views.editar_evento, name = "editar_evento"),
    
    #Login do usuário
    path("login/", views.loginU, name = "login"),
    path("home_inscricao/", views.home_inscricao, name = "inscricao"),

    #Operações com certificados
    path("emitir_certificados/<int:evento_id>/", views.emitir_certificados, name = "emitir_certificados"),
    path("certificados/", views.ver_certificados, name = "ver_certs"),
    
    #Finalizar sessão (logout)
    path("logout/", views.logout, name = "logout"),
]