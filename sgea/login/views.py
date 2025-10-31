from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import date, datetime

# Create your views here.
def home(request):
    return render(request, 'usuarios/home.html')

#Página de sobre------------------------------------------------------------------------------------------------------------

def sobre(request):
    # Adquire o ID e verifica se há algum, casa não haja, redireciona o usuário à tela de login
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")

    usuario = get_object_or_404(Usuario, id_usuario = usuario_id)    
    return render(request, "usuarios/sobre.html", {"usuario" : usuario})

#Funções envolvendo usuários------------------------------------------------------------------------------------------------------------

def deletar_usuario(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")
    
    # Caso o método de acesso da página seja um GET, apenas será enviado os dados do usuário e a renderização da página
    if request.method == "GET":
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        return render(request, "usuarios/deletar_usuario.html", {"usuario" : usuario})

    # Caso o método de acesso da página seja um POST, ele irá adquirir os dados do usuário e requerir uma senha, se a senha inserida for igual 
    # a senha anterior o perfil será deletado
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        
        senha = request.POST.get("senha")
        if usuario.senha != senha:
            return HttpResponse("Senha incorreta. Exclusão interrompida.")
        
        # Adquire as informações, as registra e então deleta o usuário
        Registro.objects.create(usuario_id = usuario_id, acao = "Exclusão de usuário" )
        usuario.delete()
        
        return redirect("cadastro")
        
def cadastro_usuarios(request):
    # Adquire todas as informações inseridas pelo usuário
    if request.method == "POST":
        nome = request.POST.get("nome")
        sobrenome = request.POST.get("sobrenome")
        senha = request.POST.get("senha")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        instituicao = request.POST.get("ensi")
        tipo_usuario = request.POST.get("tipo")
        senha_tipo = request.POST.get("senha_acesso")
        
        # Senhas de acesso para a criação de perfis de tipo 'professor' e 'organizador', respectivamente
        SENHAPROF = "123"
        SENHAORG = "321"
        
        # Verifica se o número inserido está conforme a regra definida (possuir 11 caracteres e apenas números)
        validatorE = RegexValidator(regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        tamanhoT = len(telefone)

        # Caso o número inserido não esteja no formato definido, esta mensagem irá aparecer ao usuário

        if not tamanhoT == 11:
            return HttpResponse("Número inserido de forma inválida, deve seguir o seguinte formato: '99999999999'.")
            
        try:
            validatorE(email)
        # Caso o email inserido não esteja no formato definido, esta mensagem irá aparecer ao usuário
        except Exception:
            return HttpResponse("Email inserido de forma inválida, deve seguir o seguinte modelo: 'exemplo@exemplo.com'")
        
        # Caso o telefone já tenha sido utilizado, o sistema impede de criar um novo usuário
        if Usuario.objects.filter(telefone = telefone).exists():
            return HttpResponse("Este telefone já foi cadastrado.")

        # Se todas as informações são válidas, um novo usuário é criado
        if tipo_usuario == "professor":
            if senha_tipo != SENHAPROF:
                return HttpResponse("Senha do professor inválida. Cadastro negado.")
        
        elif tipo_usuario == "organizador":
            if senha_tipo != SENHAORG:
                return HttpResponse("Senha do organizador inválida. Cadastro negado.")
        
        if Usuario.objects.filter(email = email).exists():
            return HttpResponse("Este email já foi cadastrado.")
            
        telefone_arrumado = (f"({telefone[0:2]}) {telefone[2:7]}-{telefone[7:11]}")
            
        # Caso todas as informações sejam inseridas corretamente, um novo usuário é criado 
        novo_usuario = Usuario.objects.create(nome = nome, sobrenome = sobrenome, senha = senha, telefone = telefone_arrumado, email = email, instituicao = instituicao, tipo = tipo_usuario)
        
        Registro.objects.create(usuario_id = novo_usuario.id_usuario, acao = "Cadastro de usuário" )

        return redirect("login")
       
    return render(request, "usuarios/home.html")

def ver_usuarios(request):
    # Adquire o ID e verifica se há algum, casa não haja, redireciona o usuário à tela de login
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")
    
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    # Como está é uma página restrita a organizadores, caso uma pessoa já logada como 'estudante' ou 'professor' tente realizar o acesso a está página,
    # o sistema irá verificar o tipo do perfil, caso seja diferente de 'organizador', irá redirecionar o usuário a sua tela principal
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    usuarios = {
    'usuarios' : Usuario.objects.all(),
    }  
    
    return render(request, 'usuarios/usuarios.html', usuarios)

def loginU(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        try:
            if not email or not senha:
                return HttpResponse("Insira um email e uma senha.")

            user = Usuario.objects.get(email=email, senha=senha)

            if user:
                request.session["usuario_id"] = user.id_usuario
                return redirect("inscricao")

            else:
                return HttpResponse("Usuário ou senha incorretos.")

        except Usuario.DoesNotExist:
            return HttpResponse("Usuário não encontrado")

    return render(request, "usuarios/login.html")

def editar_usuario(request):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        redirect("login")
    
    usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        senha = request.POST.get("senha")
        telefone = request.POST.get("telefone")
        
        if Usuario.objects.filter(telefone = telefone).exclude(id_usuario = usuario_id).exists():
            return HttpResponse("Este telefone já está cadastrado por outro usuário")
        
        validator = RegexValidator(regex = r'^\d{13}$', message = "O número de telefone deve ser inserido no formato: '9999999999999'.")
        
        try:
            validator(telefone)
        
        except ValidationError:
            return HttpResponse("O número deve ser inserido no seguinte formato: '9999999999999'.")
        
        Registro.objects.create(usuario_id = usuario_id, acao = "Edição de perfil")
        
        # Caso as informações sejam inseridas corretamente, as mudanças são salvas
        usuario.nome = nome
        usuario.senha = senha
        usuario.telefone = telefone
        usuario.save()
    
        return redirect("inscricao")

    return render(request, "usuarios/editar_usuario.html", {"usuario" : usuario})

#Funções envolvendo eventos------------------------------------------------------------------------------------------------------------

def todos_eventos(request):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    eventos = {
        "eventos" : Evento.objects.all()
    }
    
    return render(request, "usuarios/visu_eventos.html", eventos)

def eventos(request):
    try:
        # Validação das informações adquiridas no campo das datas
        dia_inicio_str = request.POST.get("dataI")
        dia_fim_str = request.POST.get("dataF")

        # Verifica se os espaços dos dias não estão vazios
        if not dia_inicio_str or not dia_fim_str:  
            return HttpResponse("O campo data de início e final são obrigatórios")

        ass = request.POST.get("assinatura")

        try:
            dia_inicio = datetime.strptime(dia_inicio_str, "%Y-%m-%d").date()
            dia_fim = datetime.strptime(dia_fim_str, "%Y-%m-%d").date()
            
        except ValueError:
            return HttpResponse("Formatação da data inválido, use: 'dia-mes-ano'.")
 
        data_hj = timezone.now().date()
 
        if dia_fim < dia_inicio:
            return HttpResponse("A data final não pode ser anterior a data inicial.")

        if dia_inicio < data_hj:
            return HttpResponse("A data de início não pode ser anterior à data atual.")

        # Validação das informações adquiridas no campo dos horários
        horarioI_str = request.POST.get("horarioI")
        horarioF_str = request.POST.get("horarioF")
        
        # Verifica se os espaços não estão vazios
        if not horarioI_str or not horarioF_str:
            return HttpResponse("O campo do horário inicial e final são obrigatórios")
        
        try:
            horario_inicio = int(horarioI_str)
            horario_final = int(horarioF_str)
        except ValueError:
            return HttpResponse("O campo do horário inicial e final devem ser número inteiros")
            
        # Verifica se os horários estão entre horários existentes (entre 0 ou 24 horas)
        if horario_inicio < 0 or horario_inicio > 24 or horario_final < 0 or horario_final > 24:
            return HttpResponse("O horário inicial e final devem estar entre 0 e 24")
        
        # Validação das informações adquiridas no campo das vagas
        vagas_str = request.POST.get("vagas")
        quantParticipantes_str = request.POST.get("quantPart")
        
        # Verifica se a informação adquirida é um número inteiro
        try:
            vagasInt = int(vagas_str)
        except ValueError:
            return HttpResponse("O valor das vagas deve ser um número inteiro positivo")
        
        try:
            quantParticipantesInt = int(quantParticipantes_str)
        except ValueError:
            return HttpResponse("O valor da quantidade de participantes deve ser um valor inteiro positivo")
        
        # Verifica se há uma quantidade maior de vagas do que de participantes
        if vagasInt > quantParticipantesInt:
            return HttpResponse("Não pode haver um número maior de vagas do que de participantes")
        
        # Verifica se os valores são positivos
        if quantParticipantesInt < 0:
            return HttpResponse("Não pode haver uma quantidade negativa de participantes")
        
        if vagasInt < 0:
            return HttpResponse("Não pode haver uma quantidade negativa de vagas")
        
        horasC = horario_final - horario_inicio
        
        horasinp = request.POST.get("horas")
        if horasinp and horasinp.isdigit():
            horas = int(horasinp)
        else:
            horas = horasC
        
        # Caso todas as informações sejam verificadas, um novo evento é criado
        novo_evento = Evento.objects.create(
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
        assinatura = ass,
        horas = horas
        )
        
        Registro.objects.create(evento_id = novo_evento.id_evento, acao = "Criação de evento")
        
        novo_evento.save()    
    
    except ValueError:
        messages.error(request, "Erro")
        return redirect("visu_eventos")
    
    eventos = {
        'eventos' : Evento.objects.all()
    }
    
    return render(request, 'usuarios/visu_eventos.html', eventos)

def ev(request):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    return render(request, "usuarios/eventos.html", {"usuarios" : usuario})

def deletar_evento(request, pk):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    evento = get_object_or_404(Evento, pk = pk)
    
    Registro.objects.create(evento_id = pk, acao = "Exclusão de evento")
    
    evento.delete()
    return redirect("even")

def editar_evento(request, pk):
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("login")
      
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
    
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário não foi encontrado.")
    
    if usuario.tipo != "organizador":
        return redirect("inscricao")
    
    evento = get_object_or_404(Evento, pk = pk)

    if request.method == "POST":
        nome = request.POST.get("nome")
        tipoevento = request.POST.get("tipo_evento")
        dataI_str = request.POST.get("dataI")
        dataF_str = request.POST.get("dataF")
        horarioI_str = request.POST.get("horarioI")
        horarioF_str = request.POST.get("horarioF")
        local = request.POST.get("local")
        quantPart_str = request.POST.get("quantPart")
        organResp = request.POST.get("organResp")
        vagas_str = request.POST.get("vagas")
        assinatura = request.POST.get("assinatura")
        horasinp = request.POST.get("horas")
        
        try:
            if nome and tipoevento and dataI_str and dataF_str and horarioI_str and horarioF_str and local and quantPart_str and organResp and vagas_str and assinatura and horasinp:
                dataI = int(dataI_str)
                dataF = int(dataF_str)
                vagas = int(vagas_str)
                quantPart = int(quantPart_str)
                horarioI = int(horarioI_str)
                horarioF = int(horarioF_str)
                
                if horasinp and horasinp.isdigit():
                    horas = int(horasinp)
                else:
                    horas = horarioF - horarioI 
                
                if dataI < 1 or dataI > 31 or dataF < 1 or dataF > 31:
                    return HttpResponse("A data inicial e final devem estar entre os dias 1 e 31.")
                
                if quantPart == 0:
                    return HttpResponse("Um evento não pode ter 0 participantes.")
                
                if quantPart < 0:
                    return HttpResponse("O evento não pode possuir um número negativo de participantes.")
            
                if dataI > dataF:
                    return HttpResponse("A data inicial não pode ser depois da data final.")
            
                if horarioI < 0 or horarioI > 24 or horarioF < 0 or horarioF > 31:
                    return HttpResponse("O horário deve ser entre 0 e 24.")
            
                if vagas > quantPart:
                    return HttpResponse("Não pode haver uma quantidade maior de vagas do que de participantes.")
            
                if horarioI > horarioF:
                    return HttpResponse("O horário inicial não pode ser menor que o horário final.")
            
                Registro.objects.create(evento_id = pk, acao = "Edição de evento")
            
                evento.nome = nome
                evento.tipoevento = tipoevento
                evento.dataI = dataI
                evento.dataF = dataF
                evento.horarioI = horarioI
                evento.horarioF = horarioF
                evento.local = local
                evento.quantPart = quantPart
                evento.organResp = organResp
                evento.vagas = vagas
                evento.horas = horas
                evento.assinatura = assinatura 
                evento.save()

                return redirect("even")

        except UnboundLocalError:
            return HttpResponse("Todas as caixas devem ser preenchidas.")

        else:
            return HttpResponse("Nenhum dos campos pode estar vazio.")

    return render(request, "usuarios/editar_evento.html", {"evento" : evento})

#Funções envolvendo inscrições------------------------------------------------------------------------------------------------------------

def home_inscricao(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")

    usuario = Usuario.objects.get(id_usuario=usuario_id)
    eventos = Evento.objects.all()
    
    inscritos = Inscrito.objects.filter(usuario_id=usuario).values_list("evento_id", flat=True)

    return render(request, "usuarios/eventosU.html", {
        "usuario": usuario,
        "eventos": eventos,
        "inscritos": inscritos
    })

def inscricao_evento(request, usuario_id, evento_id):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")
    
    if request.method == "POST":
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        evento = get_object_or_404(Evento, id_evento = evento_id)
    
        if Inscrito.objects.filter(usuario_id = usuario, evento_id = evento).exists():
            return HttpResponse("Você já está inscrito neste evento")
     
        if evento.vagas <= 0:
            return HttpResponse("Não há mais vagas disponíveis")
    
        nova_inscricao = Inscrito.objects.create(usuario_id = usuario, evento_id = evento)

        Registro.objects.create(usuario_id = nova_inscricao.usuario_id.id_usuario, evento_id = nova_inscricao.evento_id.id_evento, acao = "Inscrição em evento" )

        evento.vagas -= 1
        evento.save()
        
        messages.success(request, f"Você foi inscrito com sucesso no seguinte evento: {evento.nome}!")
        return redirect("inscricao")
        
    return render(request,"usuarios/meus_eventos.html", {"usuarios": Usuario.objects.all(), "eventos": Evento.objects.all()}) 

def usuario_eventos(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")
    
    user = get_object_or_404(Usuario, id_usuario = usuario_id)
    inscricoes = Inscrito.objects.filter(usuario_id = user)
    
    eventos = [inscricao.evento_id for inscricao in inscricoes]
    
    return render(request, "usuarios/meus_eventos.html", {"usuario" : user, "eventos" : eventos})

#Funções envolvendo certificados------------------------------------------------------------------------------------------------------------

def ver_certificados(request):
    eventos = {
        'eventos' : Evento.objects.filter(emitido = False)
    }
    
    return render(request, "usuarios/certificados.html", eventos)

def emitir_certificados(request, evento_id):
    with transaction.atomic():
        try:
            evento = get_object_or_404(Evento, pk = evento_id)

            inscricoes = Inscrito.objects.filter(evento_id = evento.pk)

            if not inscricoes.exists():
                return HttpResponse("Não há inscritos para este evento.")
            
            for inscricao in inscricoes:
                nova_emissao = Certificado.objects.create(usuario_id = inscricao.usuario_id, evento_id = inscricao.evento_id, assinatura = inscricao.evento_id.assinatura, horas = inscricao.evento_id.horas)
            
            Inscrito.objects.filter(evento_id = evento.pk).delete()        
            
            Registro.objects.create(usuario_id = nova_emissao.usuario_id.id_usuario, evento_id = nova_emissao.evento_id.id_evento, acao = "Emissão de certificado" )
            
            evento.emitido = True
            evento.save()
            
        except Exception as e:
            return HttpResponse(f"Erro na emissão de certificados: {e}")
            
    return redirect("/certificados/")

def meus_certificados(request):
    usuario_id = request.session.get("usuario_id")
    
    try:
        usuario = get_object_or_404(Usuario, id_usuario = usuario_id)
        certs = Certificado.objects.filter(usuario_id = usuario)
    
    except Exception:
        return HttpResponse("Erro ao buscar certificados.")
    
    return render(request, "usuarios/meus_certificados.html", {"usuario" : usuario, "certificados" : certs})

#Deslogar---------------------------------------------------------------------------------------------------------

def logout(request):
    # Verifica se há um id de usuário armazenado na sessão, se houver, o deletar e redireciona o usuário para a tela de login
    if "usuario_id" in request.session:
        del request.session["usuario_id"]
    
    request.session.flush()
    
    return redirect("login")

#Registros---------------------------------------------------------------------------------------------------------

def registros(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")
    
    registros = {
        'registros' : Registro.objects.all()
    }
    
    return render(request, "usuarios/registros.html", registros)