from django.db import models

# Create your models here.
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key = True, unique = True)
    nome = models.TextField(max_length= 255, null = False)
    senha = models.TextField(max_length = 255, null = False)
    
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
