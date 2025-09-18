from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Usuario, Evento, Inscrito
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.
def home(request):
    return render(request, 'usuarios/home.html')

def usuarios(request):
    if request.method == "POST":
        novo_usuario = Usuario()
        nome = request.POST.get("nome")
        senha = request.POST.get("senha")
        if nome and senha:
            Usuario.objects.create(nome = nome, senha = senha)
        
    usuarios = {
        'usuarios' : Usuario.objects.all()
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
            user = Usuario.objects.filter(nome = nomeU, senha = senhaU).exists()
            if user:
                events = Evento.objects.all()
                return render(request, "usuarios/eventosU.html", {"usuario": user, "eventos": events})
            
            else:
                return HttpResponse("Usuário não encontrado (nome ou senha foram inseridos incorretamente)")
        
        except Exception as e:
            return HttpResponse(f"Erro {e}") 
    
    return render(request, "usuarios/login.html")

def home_inscricao(request):
    eventos = {
        'eventos' : Evento.objects.all()
    }
    return render(request, "usuarios/eventosU.html", eventos)

def inscricao_evento(request):
    if request.method == "POST":
        user_id = request.POST.get("usuario_id")
        event_id = request.POST.get("evento_id")
    
        usuario = get_object_or_404(Usuario, id_usuario = user_id)
        evento = get_object_or_404(Evento, id_evento = event_id)
    
        if Inscrito.objects.filter(usuario = usuario, evento = evento).exists():
            return HttpResponse("Você já está inscrito neste evento")
    
        total_inscritos = Inscrito.objects.filter(evento = evento).count()
        if total_inscritos >= Evento.vagas:
            return HttpResponse("Não há mais vagas disponíveis")
    
        Inscrito.objects.create(usuario = usuario, evento = evento)
        return HttpResponse(f"Você foi inscrito com sucesso no seguinte evento: {Evento.nome}")

    return render(request,"usuario/inscrever_evento.html", {"usuarios": Usuario.objects.all(), "eventos": Evento.objects.all()}) 

def usuario_eventos(request, usuario_id):
    user = get_object_or_404(Usuario, id_usuario = usuario_id)
    inscricoes = Inscrito.objects.filter(user = user)
    
    return render(request, "usuario/meus_eventos.html", {"inscricoes" : inscricoes, "usuario" : user})