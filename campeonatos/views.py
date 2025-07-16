from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import json

from .models import Campeonato, Equipe, Participacao, Rodada, Partida, Classificacao
from .services import CampeonatoService, ClassificacaoService, PartidaService, RodadaService
from .forms import CampeonatoForm, EquipeForm, PartidaForm, RodadaForm, PartidaManualForm


def dashboard(request):
    """Página inicial do sistema"""
    context = {
        'campeonatos_andamento': Campeonato.objects.filter(status='em_andamento')[:5],
        'ultimos_resultados': PartidaService.obter_ultimos_resultados(5),
        'proximas_partidas': PartidaService.obter_proximas_partidas(5),
        'total_campeonatos': Campeonato.objects.count(),
        'total_equipes': Equipe.objects.count(),
        'total_partidas': Partida.objects.filter(status='finalizada').count(),
    }
    return render(request, 'campeonatos/dashboard.html', context)


def campeonatos_list(request):
    """Lista todos os campeonatos com filtros"""
    campeonatos = Campeonato.objects.all()

    # Filtros
    ano = request.GET.get('ano')
    status = request.GET.get('status')
    search = request.GET.get('search')

    if ano:
        campeonatos = campeonatos.filter(ano=ano)
    if status:
        campeonatos = campeonatos.filter(status=status)
    if search:
        campeonatos = campeonatos.filter(
            Q(nome__icontains=search)
        )

    # Calcular estatísticas ANTES da paginação
    campeonatos_em_andamento = campeonatos.filter(
        status='em_andamento').count()
    campeonatos_finalizados = campeonatos.filter(status='finalizado').count()
    campeonatos_planejados = campeonatos.filter(status='planejado').count()

    # Paginação
    paginator = Paginator(campeonatos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Anos disponíveis para filtro
    anos_disponiveis = Campeonato.objects.values_list(
        'ano', flat=True).distinct().order_by('-ano')

    context = {
        'page_obj': page_obj,
        'anos_disponiveis': anos_disponiveis,
        'campeonatos_em_andamento': campeonatos_em_andamento,
        'campeonatos_finalizados': campeonatos_finalizados,
        'campeonatos_planejados': campeonatos_planejados,
        'filtros': {
            'ano': ano,
            'status': status,
            'search': search,
        }
    }
    return render(request, 'campeonatos/campeonatos_list.html', context)


def campeonato_detail(request, pk):
    """Detalhes de um campeonato específico"""
    campeonato = get_object_or_404(Campeonato, pk=pk)

    # Abas do campeonato
    aba = request.GET.get('aba', 'info')

    context = {
        'campeonato': campeonato,
        'aba': aba,
    }

    if aba == 'equipes':
        context['participacoes'] = campeonato.participacao_set.all(
        ).select_related('equipe')
    elif aba == 'classificacao':
        if campeonato.tipo == 'grupos_mata_mata':
            # Classificação por grupos
            grupos = {}
            participacoes = campeonato.participacao_set.all().select_related('equipe')

            # Identificar todos os grupos existentes
            for participacao in participacoes:
                grupo = participacao.grupo or 'A'
                if grupo not in grupos:
                    grupos[grupo] = []

            # Obter classificação para cada grupo
            classificacao_grupos = {}
            for grupo in grupos.keys():
                classificacao_grupos[grupo] = ClassificacaoService.obter_classificacao_por_grupo(
                    campeonato, grupo)

            context['classificacao_grupos'] = classificacao_grupos
        else:
            # Classificação geral
            context['classificacao'] = ClassificacaoService.obter_classificacao_por_grupo(
                campeonato)
    elif aba == 'partidas':
        if campeonato.tipo == 'grupos_mata_mata':
            # Organizar rodadas por grupo para campeonatos de grupos
            rodadas_por_grupo = {}
            rodadas = campeonato.rodada_set.all().prefetch_related(
                'partida_set__equipe_mandante',
                'partida_set__equipe_visitante'
            )

            for rodada in rodadas:
                # Determinar o grupo da rodada baseado nas equipes
                grupos_rodada = set()
                for partida in rodada.partida_set.all():
                    # Buscar o grupo das equipes na participação
                    participacao_mandante = campeonato.participacao_set.filter(
                        equipe=partida.equipe_mandante
                    ).first()
                    if participacao_mandante and participacao_mandante.grupo:
                        grupos_rodada.add(participacao_mandante.grupo)

                # Se a rodada tem equipes de um grupo específico
                if len(grupos_rodada) == 1:
                    grupo = list(grupos_rodada)[0]
                    if grupo not in rodadas_por_grupo:
                        rodadas_por_grupo[grupo] = []
                    rodadas_por_grupo[grupo].append(rodada)
                else:
                    # Rodadas mistas ou mata-mata
                    if 'Mata-mata' not in rodadas_por_grupo:
                        rodadas_por_grupo['Mata-mata'] = []
                    rodadas_por_grupo['Mata-mata'].append(rodada)

            context['rodadas_por_grupo'] = rodadas_por_grupo
        else:
            # Classificação geral
            rodadas = campeonato.rodada_set.all().prefetch_related(
                'partida_set__equipe_mandante', 'partida_set__equipe_visitante')
            context['rodadas'] = rodadas

    return render(request, 'campeonatos/campeonato_detail.html', context)


@login_required
def campeonato_create(request):
    """Criar novo campeonato"""
    if request.method == 'POST':
        form = CampeonatoForm(request.POST)
        if form.is_valid():
            campeonato = form.save()
            messages.success(
                request, f'Campeonato "{campeonato.nome}" criado com sucesso!')
            return redirect('campeonato_detail', pk=campeonato.pk)
    else:
        form = CampeonatoForm()

    return render(request, 'campeonatos/campeonato_form.html', {'form': form, 'title': 'Criar Campeonato'})


@login_required
def campeonato_edit(request, pk):
    """Editar campeonato existente"""
    campeonato = get_object_or_404(Campeonato, pk=pk)

    if request.method == 'POST':
        form = CampeonatoForm(request.POST, instance=campeonato)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Campeonato "{campeonato.nome}" atualizado com sucesso!')
            return redirect('campeonato_detail', pk=campeonato.pk)
    else:
        form = CampeonatoForm(instance=campeonato)

    return render(request, 'campeonatos/campeonato_form.html', {
        'form': form,
        'title': 'Editar Campeonato',
        'campeonato': campeonato
    })


def equipes_list(request):
    """Lista todas as equipes"""
    equipes = Equipe.objects.all()

    search = request.GET.get('search')
    if search:
        equipes = equipes.filter(
            Q(nome__icontains=search) | Q(cidade__icontains=search)
        )

    # Calcular estatísticas ANTES da paginação
    equipes_com_escudo = equipes.filter(escudo__isnull=False).count()

    paginator = Paginator(equipes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'campeonatos/equipes_list.html', {
        'page_obj': page_obj,
        'search': search,
        'equipes_com_escudo': equipes_com_escudo,
    })


@login_required
def equipe_create(request):
    """Criar nova equipe"""
    if request.method == 'POST':
        form = EquipeForm(request.POST, request.FILES)
        if form.is_valid():
            equipe = form.save()
            messages.success(
                request, f'Equipe "{equipe.nome}" criada com sucesso!')
            return redirect('equipes_list')
    else:
        form = EquipeForm()

    return render(request, 'campeonatos/equipe_form.html', {'form': form, 'title': 'Criar Equipe'})


@login_required
def equipe_edit(request, pk):
    """Editar equipe existente"""
    equipe = get_object_or_404(Equipe, pk=pk)

    if request.method == 'POST':
        form = EquipeForm(request.POST, request.FILES, instance=equipe)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Equipe "{equipe.nome}" atualizada com sucesso!')
            return redirect('equipes_list')
    else:
        form = EquipeForm(instance=equipe)

    return render(request, 'campeonatos/equipe_form.html', {
        'form': form,
        'title': 'Editar Equipe',
        'equipe': equipe
    })


@login_required
@require_http_methods(["POST"])
def gerar_rodadas(request, campeonato_id):
    """Gera automaticamente as rodadas de um campeonato"""
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)

    try:
        if campeonato.tipo == 'pontos_corridos':
            CampeonatoService.gerar_rodadas_pontos_corridos(campeonato)
        else:
            CampeonatoService.gerar_rodadas_grupos(campeonato)

        messages.success(request, 'Rodadas geradas com sucesso!')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('campeonato_detail', pk=campeonato.pk)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def registrar_resultado(request):
    """Registra o resultado de uma partida via AJAX"""
    try:
        data = json.loads(request.body)
        partida_id = data.get('partida_id')
        gols_mandante = int(data.get('gols_mandante', 0))
        gols_visitante = int(data.get('gols_visitante', 0))

        partida = get_object_or_404(Partida, pk=partida_id)

        PartidaService.registrar_resultado(
            partida, gols_mandante, gols_visitante)

        return JsonResponse({
            'success': True,
            'message': 'Resultado registrado com sucesso!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao registrar resultado: {str(e)}'
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def adicionar_equipe_campeonato(request):
    """Adiciona uma equipe a um campeonato via AJAX"""
    try:
        data = json.loads(request.body)
        campeonato_id = data.get('campeonato_id')
        equipe_id = data.get('equipe_id')
        grupo = data.get('grupo', None)

        campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
        equipe = get_object_or_404(Equipe, pk=equipe_id)

        # Se não especificou grupo e é campeonato de grupos, atribuir automaticamente
        if not grupo and campeonato.tipo == 'grupos_mata_mata':
            grupo = CampeonatoService.obter_proximo_grupo_disponivel(
                campeonato)

        participacao, created = Participacao.objects.get_or_create(
            campeonato=campeonato,
            equipe=equipe,
            defaults={'grupo': grupo}
        )

        if created:
            # Atualizar classificação
            ClassificacaoService.atualizar_classificacao_campeonato(campeonato)

            grupo_texto = f" no {grupo}" if grupo else ""
            return JsonResponse({
                'success': True,
                'message': f'Equipe "{equipe.nome}" adicionada ao campeonato{grupo_texto}!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Equipe já está participando deste campeonato!'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao adicionar equipe: {str(e)}'
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def remover_equipe_campeonato(request):
    """Remove uma equipe de um campeonato"""
    try:
        data = json.loads(request.body)
        participacao_id = data.get('participacao_id')

        if not participacao_id:
            return JsonResponse({
                'success': False,
                'message': 'ID da participação é obrigatório'
            })

        participacao = get_object_or_404(Participacao, pk=participacao_id)
        campeonato = participacao.campeonato
        equipe_nome = participacao.equipe.nome

        # Verificar se o campeonato permite remoção de equipes
        if campeonato.status not in ['planejado', 'inscricoes_abertas']:
            return JsonResponse({
                'success': False,
                'message': 'Não é possível remover equipes de um campeonato em andamento'
            })

        # Remover a participação
        participacao.delete()

        return JsonResponse({
            'success': True,
            'message': f'Equipe {equipe_nome} removida do campeonato com sucesso'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao remover equipe: {str(e)}'
        })


def partidas_list(request):
    """Lista todas as partidas com filtros"""
    partidas = Partida.objects.all().select_related(
        'rodada__campeonato',
        'equipe_mandante',
        'equipe_visitante'
    ).order_by('-rodada__campeonato__ano', 'rodada__campeonato__nome', 'rodada__numero')

    # Filtros
    campeonato_id = request.GET.get('campeonato')
    status = request.GET.get('status')

    if campeonato_id:
        partidas = partidas.filter(rodada__campeonato_id=campeonato_id)
    if status:
        partidas = partidas.filter(status=status)

    # Calcular estatísticas ANTES da paginação
    partidas_finalizadas = partidas.filter(status='finalizada').count()
    partidas_pendentes = partidas.filter(status='pendente').count()

    # Organizar partidas por campeonato e rodada
    partidas_organizadas = {}

    # Se há filtro por campeonato específico, usar paginação normal
    if campeonato_id:
        paginator = Paginator(partidas, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        partidas_para_organizar = page_obj.object_list
    else:
        # Se não há filtro, mostrar todas organizadas (limitadas para performance)
        partidas_para_organizar = partidas[:100]  # Limitar para performance
        page_obj = None

    for partida in partidas_para_organizar:
        campeonato = partida.rodada.campeonato
        rodada = partida.rodada

        if campeonato.nome not in partidas_organizadas:
            partidas_organizadas[campeonato.nome] = {
                'campeonato': campeonato,
                'rodadas': {}
            }

        if rodada.nome not in partidas_organizadas[campeonato.nome]['rodadas']:
            partidas_organizadas[campeonato.nome]['rodadas'][rodada.nome] = {
                'rodada': rodada,
                'partidas': []
            }

        partidas_organizadas[campeonato.nome]['rodadas'][rodada.nome]['partidas'].append(
            partida)

    context = {
        'page_obj': page_obj,
        'partidas_organizadas': partidas_organizadas,
        'campeonatos': Campeonato.objects.all(),
        'total_partidas': partidas.count(),
        'partidas_finalizadas': partidas_finalizadas,
        'partidas_pendentes': partidas_pendentes,
        'filtros': {
            'campeonato': campeonato_id,
            'status': status,
        }
    }
    return render(request, 'campeonatos/partidas_list.html', context)


# NOTA: Estas funções foram comentadas pois usavam ConfiguracaoRodada que foi removido
# TODO: Refatorar para usar as configurações que agora estão no modelo Campeonato

# def configuracao_rodada(request, campeonato_id):
#     """Configuração de rodadas para um campeonato"""
#     campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
#     # Implementação será refatorada...

# def gerar_rodadas(request, campeonato_id):
#     """Gera rodadas baseadas na configuração do campeonato"""
#     campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
#     # Implementação será refatorada...


def gerenciar_rodadas(request, campeonato_id):
    """Lista e permite gerenciar rodadas de um campeonato"""
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)

    # Obter rodadas com partidas agrupadas
    rodadas_data = PartidaService.obter_partidas_por_rodada_agrupadas(
        campeonato)

    context = {
        'campeonato': campeonato,
        'rodadas_data': rodadas_data,
    }
    return render(request, 'campeonatos/gerenciar_rodadas.html', context)


def editar_rodada(request, campeonato_id, rodada_id):
    """Edita uma rodada específica"""
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
    rodada = get_object_or_404(Rodada, pk=rodada_id, campeonato=campeonato)

    if request.method == 'POST':
        form = RodadaForm(request.POST, instance=rodada)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Rodada {rodada.numero} atualizada com sucesso!')
            return redirect('gerenciar_rodadas', campeonato_id=campeonato.id)
    else:
        form = RodadaForm(instance=rodada)

    context = {
        'campeonato': campeonato,
        'rodada': rodada,
        'form': form
    }
    return render(request, 'campeonatos/editar_rodada.html', context)


def adicionar_partida_manual(request, campeonato_id, rodada_id):
    """Adiciona uma partida manualmente a uma rodada"""
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
    rodada = get_object_or_404(Rodada, pk=rodada_id, campeonato=campeonato)

    if request.method == 'POST':
        form = PartidaManualForm(campeonato, request.POST)
        if form.is_valid():
            try:
                partida = RodadaService.adicionar_partida_manual(
                    rodada=rodada,
                    equipe_mandante=form.cleaned_data['equipe_mandante'],
                    equipe_visitante=form.cleaned_data['equipe_visitante'],
                    local=form.cleaned_data.get('local'),
                    data_hora=form.cleaned_data.get('data_hora'),
                    duracao_prevista=form.cleaned_data.get('duracao_prevista', 90),
                    arbitro=form.cleaned_data.get('arbitro')
                )
                messages.success(
                    request, f'Partida {partida} adicionada com sucesso!')
                return redirect('gerenciar_rodadas', campeonato_id=campeonato.id)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = PartidaManualForm(campeonato)
        # Pré-preencher data com a data da rodada
        if rodada.data_inicio:
            from datetime import datetime, time
            form.fields['data_hora'].initial = datetime.combine(rodada.data_inicio, time(15, 0))

    # Obter partidas disponíveis para mostrar opções
    partidas_disponiveis = RodadaService.obter_partidas_disponiveis_para_rodada(
        campeonato, rodada)

    context = {
        'campeonato': campeonato,
        'rodada': rodada,
        'form': form,
        # Mostrar apenas 10 sugestões
        'partidas_disponiveis': partidas_disponiveis[:10]
    }
    return render(request, 'campeonatos/adicionar_partida_manual.html', context)


def reagrupar_partidas_por_data(request, campeonato_id):
    """Reagrupa partidas existentes por data em novas rodadas"""
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)

    if request.method == 'POST':
        try:
            RodadaService.reagrupar_partidas_por_data(campeonato)
            messages.success(
                request, 'Partidas reagrupadas por data com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao reagrupar partidas: {str(e)}')

        return redirect('gerenciar_rodadas', campeonato_id=campeonato.id)

    # Mostrar preview do reagrupamento
    partidas = Partida.objects.filter(
        rodada__campeonato=campeonato).order_by('data_hora')

    # Agrupar por data para mostrar preview
    partidas_por_data = {}
    for partida in partidas:
        data = partida.data_hora.date() if partida.data_hora else 'Sem data'
        if data not in partidas_por_data:
            partidas_por_data[data] = []
        partidas_por_data[data].append(partida)

    context = {
        'campeonato': campeonato,
        'partidas_por_data': partidas_por_data
    }
    return render(request, 'campeonatos/reagrupar_partidas.html', context)


@require_http_methods(["POST"])
def excluir_partida(request, campeonato_id, partida_id):
    """Exclui uma partida específica"""
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
    partida = get_object_or_404(
        Partida, pk=partida_id, rodada__campeonato=campeonato)

    if partida.status == 'finalizada':
        messages.error(
            request, 'Não é possível excluir uma partida já finalizada.')
    else:
        partida_str = str(partida)
        partida.delete()
        messages.success(
            request, f'Partida {partida_str} excluída com sucesso!')

    return redirect('gerenciar_rodadas', campeonato_id=campeonato.id)


# API Views para AJAX
@require_http_methods(["GET"])
def api_equipes(request):
    """API para buscar equipes (para formulários)"""
    search = request.GET.get('search', '')
    campeonato_id = request.GET.get('campeonato_id')

    equipes = Equipe.objects.all()

    # Filtrar por busca
    if search:
        equipes = equipes.filter(nome__icontains=search)

    # Excluir equipes já no campeonato
    if campeonato_id:
        try:
            campeonato = Campeonato.objects.get(pk=campeonato_id)
            equipes = equipes.exclude(
                participacao__campeonato=campeonato
            )
        except Campeonato.DoesNotExist:
            pass

    equipes = equipes[:20]  # Limitar resultados

    data = [{
        'id': equipe.id,
        'nome': equipe.nome,
        'cidade': equipe.cidade
    } for equipe in equipes]

    return JsonResponse({'equipes': data})


@require_http_methods(["GET"])
def api_classificacao(request, campeonato_id):
    """API para obter classificação atualizada via AJAX"""
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
    grupo = request.GET.get('grupo')

    classificacao = ClassificacaoService.obter_classificacao_por_grupo(
        campeonato, grupo)

    data = [{
        'equipe': item.equipe.nome,
        'pontos': item.pontos,
        'jogos': item.jogos,
        'vitorias': item.vitorias,
        'empates': item.empates,
        'derrotas': item.derrotas,
        'gols_pro': item.gols_pro,
        'gols_contra': item.gols_contra,
        'saldo_gols': item.saldo_gols,
    } for item in classificacao]

    return JsonResponse({'classificacao': data})


@login_required
@require_http_methods(["POST"])
def campeonato_delete(request, pk):
    """Exclui um campeonato e todos os dados relacionados (menos equipes)"""
    campeonato = get_object_or_404(Campeonato, pk=pk)
    nome = campeonato.nome

    # Excluir todas as participações, rodadas, partidas e classificações relacionadas
    Participacao.objects.filter(campeonato=campeonato).delete()
    Rodada.objects.filter(campeonato=campeonato).delete()
    Partida.objects.filter(rodada__campeonato=campeonato).delete()
    Classificacao.objects.filter(campeonato=campeonato).delete()

    # Excluir o campeonato
    campeonato.delete()

    messages.success(request, f'Campeonato "{nome}" excluído com sucesso!')
    return redirect('campeonatos_list')
