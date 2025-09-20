from django.db import models
from django.utils import timezone

# Create your models here.
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key = True, unique = True)
    nome = models.TextField(max_length= 255, null = False)
    senha = models.TextField(max_length = 255, null = False)
    telefone = models.CharField(max_length = 13, unique = True, null = False)

class Evento(models.Model):
    id_evento = models.AutoField(primary_key = True)
    nome = models.TextField(max_length = 255, null = True)
    tipoevento = models.TextField(max_length = 255)
    dataI = models.IntegerField()
    dataF = models.IntegerField()
    horarioI = models.IntegerField()
    horarioF = models.IntegerField()
    local = models.TextField(max_length = 255)
    quantPart = models.IntegerField()
    organResp = models.TextField(max_length = 255)
    vagas = models.IntegerField()

class Inscrito(models.Model):
    id_inscricao = models.AutoField(primary_key = True)
    usuario_id = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    evento_id = models.ForeignKey(Evento, on_delete = models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add = True)
    
class Certificado(models.Model):
    id_cert = models.AutoField(primary_key = True)
    usuario_id = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    evento_id = models.ForeignKey(Evento, on_delete = models.CASCADE)
    data_emissao = models.DateTimeField(default = timezone.now)