from django.db import models
from django.utils import timezone

# Create your models here.
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key = True, unique = True)
    nome = models.TextField(max_length= 255, null = False)
    sobrenome = models.TextField(max_length = 255, null = False)
    senha = models.TextField(max_length = 255, null = False)
    confirmar_senha = models.TextField(max_length = 255, null = True)
    telefone = models.CharField(max_length = 13, unique = True, null = False)
    email = models.CharField(max_length = 255, unique = True, null = False)
    instituicao = models.CharField(max_length = 50, null = False)
    tipo = models.CharField(max_length = 50, choices = [("estudante","Estudante"), ("professor","Professor"), ("organizador","Organizador")], default = "estudante") 
    codigo = models.CharField(max_length = 6, null = True)

class Evento(models.Model):
    id_evento = models.AutoField(primary_key = True)
    nome = models.TextField(max_length = 255, null = True)
    tipoevento = models.TextField(max_length = 255)
    dataI = models.DateField()
    dataF = models.DateField()
    horarioI = models.TimeField()
    horarioF = models.TimeField()    
    local = models.TextField(max_length = 255)
    quantPart = models.IntegerField()
    organResp = models.TextField(max_length = 255)
    vagas = models.IntegerField()
    emitido = models.BooleanField(default = False)
    assinatura = models.TextField(max_length = 255, null = False)
    horas = models.DecimalField(decimal_places = 2, max_digits = 5, null = True, blank = True)
    descricao = models.TextField(max_length = 999, null = False)
    imagem = models.ImageField(upload_to = 'eventos/imagens/', blank = True, null = True)

    @property
    def horas_e_minutos(self):

        horas_str = str(self.horas)
        
        # Separa os números a partir do '.' em uma lista. ex: ['12', '45']
        horas_min = horas_str.split(".")
        
        # Primeiro valor da lista
        horasInteiras = horas_min[0]
        minutos = 0
        total = ""
        
        if len(horas_min) > 1:
            minutos = int(horas_min[1][:2])
    
        if horasInteiras == 1:
            total = f"{horasInteiras} Hora e "
        else:
            total = f"{horasInteiras} Horas e "
        
        if minutos > 0:
            if minutos == 1:
                total += f"{minutos} Minuto"
            else:    
                total += f"{minutos} Minutos"
        else:
            return "0 minutos"

        return total
    
class Inscrito(models.Model):
    id_inscricao = models.AutoField(primary_key = True)
    usuario_id = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    evento_id = models.ForeignKey(Evento, on_delete = models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add = True)
    
class Certificado(models.Model):
    id_cert = models.AutoField(primary_key = True)
    usuario_id = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    evento_id = models.ForeignKey(Evento, on_delete = models.CASCADE)
    assinatura = models.TextField(max_length = 255, null = True, blank = True)
    data_emissao = models.DateTimeField(default = timezone.now)
    horas = models.TextField(max_length = 255, null = True, blank = True)
    
class Registro(models.Model):
    id_registro = models.AutoField(primary_key = True, unique = True)
    hora = models.DateTimeField(default = timezone.now)
    usuario_id = models.TextField(max_length = 50, null = True)
    evento_id = models.TextField(max_length = 50, null = True)
    acao = models.TextField(max_length = 50, null = False)