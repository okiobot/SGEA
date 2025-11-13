from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import date, datetime
from decimal import Decimal
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import random

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
        confirmar_senha = request.POST.get("confirmar_senha")
        
        # Senhas de acesso para a criação de perfis de tipo 'professor' e 'organizador', respectivamente
        SENHAPROF = "123"
        SENHAORG = "321"
        
        # Verifica se o número inserido está conforme a regra definida (possuir 11 caracteres e apenas números)
        validatorE = RegexValidator(regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        tamanhoT = len(telefone)
        telefone_arrumado = (f"({telefone[0:2]}) {telefone[2:7]}-{telefone[7:11]}")

        if not confirmar_senha == senha:
            messages.error(request, "As senhas são diferentes.")
            return redirect("cadastro")

        if len(senha) >= 8:
            carac_especial = "@#$%^&*()-+?_=,<>/\|."
            numeros = "0123456789"
            if any(c in carac_especial for c in senha):
                if any(c in numeros for c in senha):
                    pass
                else:
                    return HttpResponse("A senha deve possuir ao menos um número.")
            else:
                return HttpResponse("A senha deve possuir ao menos um caracter especial.")
        else:
            return HttpResponse("A senha deve possuir no mínimo 8 caracteres.")

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
        
        # Gerador de código que escolhe entre 10 números aleatórios e 26 letras aleatórias
        # O usuário pode escolher entrar com o código disponibilizado ou com a senha criada anteriormente
        codigo = ""
        for i in range(0,3):
            num = random.randint(0,9)
            let = random.choice("abcdefghijklmnopqrstuvwxyz")
            codigo += str(num)
            codigo += let
       
        # Caso todas as informações sejam inseridas corretamente, um novo usuário é criado 
        novo_usuario = Usuario.objects.create(nome = nome, sobrenome = sobrenome, senha = senha, telefone = telefone_arrumado, email = email, instituicao = instituicao, tipo = tipo_usuario, codigo = codigo)

        emailhtml = render_to_string('usuarios/confirmacao_cadastro.html', {"usuario" : novo_usuario, "codigo" : codigo})
        try:
            email = EmailMessage(subject=f"Confirmação de cadastro: {novo_usuario.nome} {novo_usuario.sobrenome}", 
                                body= emailhtml, from_email="casa.de.atenaa@gmail.com", to=[novo_usuario.email])
            email.content_subtype = 'html'
            email.send()
        
        except Exception as e:
            print("Erro ao enviar confirmação pelo email: "+e)
        
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
        inputS = request.POST.get("senha")

        if not email or not inputS:
            return HttpResponse("Insira um email e uma senha.")
        try:
            # O usuário pode escolher entrar com a senha criada anteriormente ou com o código disponibilizado pelo email
            user = Usuario.objects.get(Q(senha=inputS) | Q(codigo=inputS), email=email)
    
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
            # Define a forma que a data deve ser inserida para criar a string, .date() é utilizado para adquirir apenas a parte da data
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
            # Define a forma que o horário deve ser inserido para criar 
            horario_inicio = datetime.strptime(horarioI_str, "%H:%M").time()
            horario_final = datetime.strptime(horarioF_str, "%H:%M").time()
        
        except ValueError:
            return HttpResponse("Formato de data inserido inválido.")
            
        # Verifica se os horários estão entre horários existentes (entre 0 ou 24 horas)
        if horario_final <= horario_inicio:
            return HttpResponse("O horário final não pode ser anterior ao inicial.")
        
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
        
        # Cria um objeto datetime com uma data de placeholder e o horário definido pelo usuário
        datetime_inicio = datetime.combine(date.min, horario_inicio)
        datetime_final = datetime.combine(date.min, horario_final)
       
        # Duração do evento      
        duracao_timedelta = datetime_final - datetime_inicio
                
        # Duração do evento em segundos
        total_segundos = duracao_timedelta.total_seconds()
        
        # Horas do evento, sem conter resto, sendo um número inteiro
        horas_inteiras = total_segundos // 3600
        
        # Segundos do evento, adquirindo o total possível divido por 3600
        segundos_restantes = total_segundos % 3600
        
        # Resto dos minutos, arredondando para baixo
        minutos_restantes = round(segundos_restantes / 60)
        
        minutos_decimal = minutos_restantes / 100.0
        horasC = Decimal(horas_inteiras) + Decimal(f"{minutos_decimal:.2f}")
        
        horasinp = request.POST.get("horas")
        if horasinp:
            try:
                horas = Decimal(horasinp)
        
            except ValueError:
                horas = horasC
        
        else:
            horas = horasC
        
        imagem = request.FILES.get("imagem")
        descricao = request.POST.get("descricao")

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
        horas = horas,
        imagem = imagem,
        descricao = descricao
        )
        
        Registro.objects.create(evento_id = novo_evento.id_evento, acao = "Criação de evento")
        
        novo_evento.save()    
    
    except ValueError:
        messages.error(request, "Erro")
        return redirect("visu_eventos")
    
    eventos = {
        'eventos' : Evento.objects.all(),
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
        descricao = request.POST.get("descricao")
        
        try:
            if nome and tipoevento and dataI_str and dataF_str and horarioI_str and horarioF_str and local and quantPart_str and organResp and vagas_str and assinatura and descricao:
                dataI = datetime.strptime(dataI_str, "%Y-%m-%d").date()
                dataF = datetime.strptime(dataF_str, "%Y-%m-%d").date()
                vagas = int(vagas_str)
                quantPart = int(quantPart_str)
                horarioI = datetime.strptime(horarioI_str, "%H:%M").time()
                horarioF = datetime.strptime(horarioF_str, "%H:%M").time()
                
                datetime_inicio = datetime.combine(date.min, horarioI)
                datetime_final = datetime.combine(date.min, horarioF)
                duracao_timedelta = datetime_final - datetime_inicio
                        
                total_segundos = duracao_timedelta.total_seconds()
                horas_inteiras = total_segundos // 3600                  
                segundos_restantes = total_segundos % 3600                   
                minutos_restantes = round(segundos_restantes / 60)
                minutos_decimal = minutos_restantes / 100.0              
                horasC = Decimal(horas_inteiras) + Decimal(f"{minutos_decimal:.2f}")

                horasinp = request.POST.get("horas")
                if horasinp:
                    try:
                        horas = Decimal(horasinp)
                
                    except ValueError:
                        horas = horasC
                
                else:
                    horas = horasC
                   
                if quantPart == 0:
                    return HttpResponse("Um evento não pode ter 0 participantes.")
                
                if quantPart < 0:
                    return HttpResponse("O evento não pode possuir um número negativo de participantes.")
            
                if dataI > dataF:
                    return HttpResponse("A data inicial não pode ser depois da data final.")

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
                evento.descricao = descricao
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
                nova_emissao = Certificado.objects.create(usuario_id = inscricao.usuario_id, evento_id = inscricao.evento_id, assinatura = inscricao.evento_id.assinatura, horas = inscricao.evento_id.horas_e_minutos)
            
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
