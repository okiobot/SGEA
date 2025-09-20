from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Usuario, Evento, Inscrito, Certificado
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import transaction

# Create your views here.
def home(request):
    return render(request, 'usuarios/home.html')

def cadastro_usuarios(request):
    #Adquire todas as informações inseridas pelo usuário
    if request.method == "POST":
        nome = request.POST.get("nome")
        senha = request.POST.get("senha")
        telefone = request.POST.get("telefone")
        
        #Verifica se o número inserido está conforme a regra definida (começar com +, possuir 13 caracteres e apenas números)
        validator = RegexValidator(regex = r'^\+?1?\d{13}$', message = "O número de telefone deve ser inserido no formato: '+9999999999999'.")
        
        try:
            validator(telefone)
            
            #Caso o telefone já tenha sido utilizado, o sistema impede de criar um novo usuário
            if Usuario.objects.filter(telefone = telefone).exists():
                return HttpResponse("Este telefone já foi cadastrado.")
            
            #Se todas as informações são válidas, um novo usuário é criado
            Usuario.objects.create(nome = nome, senha = senha, telefone = telefone)
            return redirect("listagem_usuarios")
       
        #Caso o número inserido não esteja no formato definido, esta mensagem irá aparecer ao usuário
        except ValidationError:
            return HttpResponse("Número inserido de forma inválida, deve seguir o seguinte formato: '+9999999999999'.")
    
    usuarios = {
        'usuarios' : Usuario.objects.all(),
    }
    
    return render(request, 'usuarios/usuarios.html', usuarios)

def ev(request):
    return render(request, "usuarios/eventos.html")

def todos_eventos(request):
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, "usuarios/visu_eventos.html", eventos)

def eventos(request):
    try:
        #Validação das informações adquiridas no campo das datas
        dia_inicio_str = request.POST.get("dataI")
        dia_fim_str = request.POST.get("dataF")

        #Verifica se os espaços dos dias não estão vazios
        if not dia_inicio_str or not dia_fim_str:  
            return HttpResponse("O campo data de início e final são obrigatórios")

        try:
            dia_inicio = int(dia_inicio_str)
            dia_fim = int(dia_fim_str)
        except ValueError:
            return HttpResponse("O campo data de início e final devem ser um número inteiro")

        #Verifica se a data é um dia válido (entre 1 ou 31)
        if dia_inicio < 1 or dia_inicio > 31 or dia_fim < 1 or dia_fim > 31:
            return HttpResponse("O dia de início e final devem estar entre 1 e 31")
        
        #Validação das informações adquiridas no campo dos horários
        horarioI_str = request.POST.get("horarioI")
        horarioF_str = request.POST.get("horarioF")
        
        #Verifica se os espaços não estão vazios
        if not horarioI_str or not horarioF_str:
            return HttpResponse("O campo do horário inicial e final são obrigatórios")
        
        try:
            horario_inicio = int(horarioI_str)
            horario_final = int(horarioF_str)
        except ValueError:
            return HttpResponse("O campo do horário inicial e final devem ser número inteiros")
            
        #Verifica se os horários estão entre horários existentes (entre 0 ou 24 horas)
        if horario_inicio < 0 or horario_inicio > 24 or horario_final < 0 or horario_final > 24:
            return HttpResponse("O horário inicial e final devem estar entre 0 e 24")
        
        #Validação das informações adquiridas no campo das vagas
        vagas_str = request.POST.get("vagas")
        quantParticipantes_str = request.POST.get("quantPart")
        
        #Verifica se a informação adquirida é um número inteiro
        try:
            vagasInt = int(vagas_str)
        except ValueError:
            return HttpResponse("O valor das vagas deve ser um número inteiro positivo")
        
        try:
            quantParticipantesInt = int(quantParticipantes_str)
        except ValueError:
            return HttpResponse("O valor da quantidade de participantes deve ser um valor inteiro positivo")
        
        #Verifica se há uma quantidade maior de vagas do que de participantes
        if vagasInt > quantParticipantesInt:
            return HttpResponse("Não pode haver um número maior de vagas do que de participantes")
        
        #Verifica se os valores são positivos
        if quantParticipantesInt < 0:
            return HttpResponse("Não pode haver uma quantidade negativa de participantes")
        
        if vagasInt < 0:
            return HttpResponse("Não pode haver uma quantidade negativa de vagas")
        
        #Caso todas as informações sejam verificadas, um novo evento é criado
        novo_evento = Evento(
        nome = request.POST.get("nome"),
        tipoevento = request.POST.get("tipoE"),
        dataI = dia_inicio,
        dataF = dia_fim,
        horarioI = horario_inicio,
        horarioF = horario_final,
        local = request.POST.get("local"),
        quantPart = quantParticipantesInt,
        organResp = request.POST.get("organResp"),
        vagas = vagasInt,
        )
        
        novo_evento.save()    
    
    except ValueError:
        messages.error(request, "Erro")
        return redirect("visu_eventos")
    
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, 'usuarios/visu_eventos.html', eventos)

def deletar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk = pk)
    if request.method == "GET":
        usuario.delete()
        return redirect("/usuarios/")
    
def deletar_evento(request, pk):
    evento = get_object_or_404(Evento, pk = pk)
    if request.method == "GET":
        evento.delete()
        return redirect("/todos_eventos/")
    
def loginU(request):
    if request.method == "POST":
        nomeU = request.POST.get("nome")
        senhaU = request.POST.get("senha")
        
        if not nomeU or not senhaU:
            return HttpResponse("Insira um nome e senha")
            
        try:     
            user = Usuario.objects.filter(nome = nomeU, senha = senhaU).first()
            if user:
                events = Evento.objects.all()
                return render(request, "usuarios/eventosU.html", {"usuario": user, "eventos": events})
            
            else:
                return HttpResponse("Usuário não encontrado (nome ou senha foram inseridos incorretamente)")
        
        except Exception as e:
            return HttpResponse(f"Erro {e}") 
    
    return render(request, "usuarios/login.html")

def home_inscricao(request, usuario_id):
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    eventos = Evento.objects.all()
    
    inscritos = Inscrito.objects.filter(usuario_id=usuario).values_list("evento_id", flat=True)

    return render(request, "usuarios/eventosU.html", {
        "usuario": usuario,
        "eventos": eventos,
        "inscritos": inscritos
    })

def inscricao_evento(request, usuario_id, evento_id):
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        evento = get_object_or_404(Evento, id_evento = evento_id)
    
        if Inscrito.objects.filter(usuario_id = usuario, evento_id = evento).exists():
            return HttpResponse("Você já está inscrito neste evento")
    
        total_inscritos = Inscrito.objects.filter(evento_id = evento).count()
        
        if evento.vagas <= 0:
            return HttpResponse("Não há mais vagas disponíveis")
    
        Inscrito.objects.create(usuario_id = usuario, evento_id = evento)

        evento.vagas -= 1
        evento.save()
        
        return HttpResponse(f"Você foi inscrito com sucesso no seguinte evento!: {evento.nome}")

    return render(request,"usuarios/meus_eventos.html", {"usuarios": Usuario.objects.all(), "eventos": Evento.objects.all()}) 

def usuario_eventos(request, usuario_id):
    user = get_object_or_404(Usuario, id_usuario = usuario_id)
    inscricoes = Inscrito.objects.filter(usuario_id = user)
    
    eventos = [inscricao.evento_id for inscricao in inscricoes]
    
    return render(request, "usuarios/meus_eventos.html", {"usuario" : user, "eventos" : eventos})

def ver_certificados(request):
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, "usuarios/certificados.html", eventos)

def emitir_certificados(request, evento_id):
    with transaction.atomic():
        try:
            evento = get_object_or_404(Evento, pk = evento_id)

            inscricoes = Inscrito.objects.filter(evento_id = evento.id_evento)

            if not inscricoes.exists():
                return HttpResponse("Não há inscritos para este evento.")
            
            for inscricao in inscricoes:
                Certificado.objects.create(usuario_id = inscricao.usuario_id, evento_id = inscricao.evento_id)
            
            inscricoes.delete()        
            #evento.delete()
            
        except Exception as e:
            return HttpResponse(f"Erro na emissão de certificados: {e}")
            
    return redirect("/certificados/")

def meus_certificados(request, usuario_id):
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        certs = Certificado.objects.filter(usuario_id = usuario)
    
    except Exception:
        return HttpResponse("Erro ao buscar certificados.")
    
    return render(request, "usuarios/meus_certificados.html", {"usuario" : usuario, "certificados" : certs})