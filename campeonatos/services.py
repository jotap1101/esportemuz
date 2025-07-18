import random
from itertools import combinations
from datetime import date, timedelta, datetime, time
from django.db import transaction
from .models import Campeonato, Equipe, Participacao, Rodada, Partida, Classificacao


class RodadaService:
    """Serviço para gerenciamento avançado de rodadas e partidas"""

    # TEMPORARIAMENTE COMENTADO - SERÁ REFATORADO PARA USAR CONFIGURAÇÕES DO CAMPEONATO
    # @staticmethod
    # def criar_configuracao_rodada(campeonato, tipo_configuracao='manual', partidas_por_rodada=1, dias_entre_rodadas=7, data_inicio=None):
    #     """Cria ou atualiza a configuração de rodada para um campeonato"""
    #     # Será refatorado para usar campos do modelo Campeonato

    # @staticmethod
    # def gerar_rodadas_configuravel(campeonato):
    #     """Gera rodadas baseadas na configuração do campeonato"""
    #     # Será refatorado para usar campos do modelo Campeonato

    # @staticmethod
    # def _gerar_rodadas_automaticas(campeonato, configuracao):
    #     """Gera rodadas automaticamente baseadas na configuração"""
    #     # Será refatorado para usar campos do modelo Campeonato

    # @staticmethod
    # def _preparar_estrutura_manual(campeonato, configuracao):
    #     """Prepara estrutura básica para configuração manual"""
    #     # Será refatorado para usar campos do modelo Campeonato

    @staticmethod
    def adicionar_partida_manual(rodada, equipe_mandante, equipe_visitante, local=None, data_hora=None, arbitro=None):
        """Adiciona uma partida manualmente a uma rodada"""
        # Verificar se já existe uma partida entre essas equipes na rodada
        if Partida.objects.filter(
            rodada=rodada,
            equipe_mandante=equipe_mandante,
            equipe_visitante=equipe_visitante
        ).exists():
            raise ValueError(
                "Já existe uma partida entre essas equipes nesta rodada")

        # Verificar se a rodada não excede o limite de partidas
        # TODO: Refatorar para usar campos do campeonato
        if rodada.total_partidas() >= rodada.campeonato.partidas_por_rodada:
            raise ValueError(
                f"Esta rodada já atingiu o limite de {rodada.campeonato.partidas_por_rodada} partidas")

        partida = Partida.objects.create(
            rodada=rodada,
            equipe_mandante=equipe_mandante,
            equipe_visitante=equipe_visitante,
            local=local or rodada.local_padrao,
            data_hora=data_hora or (datetime.combine(rodada.data_inicio, time(15, 0)) if rodada.data_inicio else None),
            arbitro=arbitro or ''
        )

        return partida

    @staticmethod
    def reagrupar_partidas_por_data(campeonato):
        """Reagrupa partidas existentes por data em novas rodadas"""
        partidas = Partida.objects.filter(
            rodada__campeonato=campeonato).order_by('data_hora')

        if not partidas.exists():
            return

        # Limpar rodadas existentes
        Rodada.objects.filter(campeonato=campeonato).delete()

        # Agrupar partidas por data
        partidas_por_data = {}
        for partida in partidas:
            data = partida.data_hora.date() if partida.data_hora else date.today()
            if data not in partidas_por_data:
                partidas_por_data[data] = []
            partidas_por_data[data].append(partida)

        # Criar novas rodadas baseadas nas datas
        rodada_num = 1
        for data, lista_partidas in sorted(partidas_por_data.items()):
            rodada = Rodada.objects.create(
                campeonato=campeonato,
                numero=rodada_num,
                nome=f"Rodada {rodada_num}",
                data_rodada=data
            )

            # Reatribuir partidas à nova rodada
            for partida in lista_partidas:
                partida.rodada = rodada
                partida.save()

            rodada_num += 1

    @staticmethod
    def obter_partidas_disponiveis_para_rodada(campeonato, rodada):
        """Obtém lista de partidas que podem ser adicionadas a uma rodada"""
        # Buscar todas as equipes do campeonato
        equipes = list(campeonato.participacao_set.all())

        # Gerar todas as possíveis combinações
        todas_combinacoes = list(combinations(equipes, 2))

        # Filtrar combinações que já existem em qualquer rodada
        partidas_existentes = set()
        for partida in Partida.objects.filter(rodada__campeonato=campeonato):
            partidas_existentes.add(
                (partida.equipe_mandante_id, partida.equipe_visitante_id))
            partidas_existentes.add(
                (partida.equipe_visitante_id, partida.equipe_mandante_id))

        # Retornar combinações disponíveis
        combinacoes_disponiveis = []
        for participacao1, participacao2 in todas_combinacoes:
            equipe1_id = participacao1.equipe_id
            equipe2_id = participacao2.equipe_id

            if (equipe1_id, equipe2_id) not in partidas_existentes:
                combinacoes_disponiveis.append(
                    (participacao1.equipe, participacao2.equipe))

        return combinacoes_disponiveis


class CampeonatoService:
    """Serviço para gerenciamento de campeonatos"""

    @staticmethod
    def gerar_rodadas_pontos_corridos(campeonato):
        """Gera todas as rodadas para um campeonato de pontos corridos"""
        equipes = list(campeonato.participacao_set.all(
        ).values_list('equipe', flat=True))

        if len(equipes) < 2:
            raise ValueError(
                "É necessário pelo menos 2 equipes para gerar as rodadas")

        # Limpar rodadas existentes
        Rodada.objects.filter(campeonato=campeonato).delete()

        # Gerar combinações de partidas (todos contra todos)
        partidas = list(combinations(equipes, 2))

        # Distribuir partidas em rodadas
        num_rodadas = len(equipes) - \
            1 if len(equipes) % 2 == 0 else len(equipes)
        partidas_por_rodada = len(equipes) // 2

        rodada_num = 1
        for i in range(0, len(partidas), partidas_por_rodada):
            rodada = Rodada.objects.create(
                campeonato=campeonato,
                numero=rodada_num,
                nome=f"Rodada {rodada_num}"
            )

            # Criar partidas da rodada
            partidas_rodada = partidas[i:i + partidas_por_rodada]
            for equipe_mandante_id, equipe_visitante_id in partidas_rodada:
                Partida.objects.create(
                    rodada=rodada,
                    equipe_mandante_id=equipe_mandante_id,
                    equipe_visitante_id=equipe_visitante_id
                )

            rodada_num += 1

    @staticmethod
    def gerar_grupos(campeonato):
        """Distribui as equipes em grupos aleatoriamente"""
        equipes = list(campeonato.participacao_set.all())
        random.shuffle(equipes)

        grupos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        for i, participacao in enumerate(equipes):
            grupo_index = i % campeonato.numero_grupos
            participacao.grupo = grupos[grupo_index]
            participacao.save()

    @staticmethod
    def gerar_rodadas_grupos(campeonato):
        """Gera rodadas para campeonato com grupos"""
        # Primeiro distribui as equipes em grupos
        CampeonatoService.gerar_grupos(campeonato)

        # Limpar rodadas existentes
        Rodada.objects.filter(campeonato=campeonato).delete()

        grupos = {}
        for participacao in campeonato.participacao_set.all():
            if participacao.grupo not in grupos:
                grupos[participacao.grupo] = []
            grupos[participacao.grupo].append(participacao.equipe.id)

        rodada_num = 1

        # Gerar rodadas para cada grupo
        for grupo, equipes in grupos.items():
            if len(equipes) < 2:
                continue

            partidas = list(combinations(equipes, 2))

            for equipe_mandante_id, equipe_visitante_id in partidas:
                # Verificar se já existe uma rodada para esse número
                rodada, created = Rodada.objects.get_or_create(
                    campeonato=campeonato,
                    numero=rodada_num,
                    defaults={'nome': f"Rodada {rodada_num} - Grupo {grupo}"}
                )

                Partida.objects.create(
                    rodada=rodada,
                    equipe_mandante_id=equipe_mandante_id,
                    equipe_visitante_id=equipe_visitante_id
                )

                rodada_num += 1

    @staticmethod
    def obter_proximo_grupo_disponivel(campeonato):
        """Obtém o próximo grupo disponível com menos equipes"""
        from collections import Counter

        # Contar equipes por grupo
        grupos_count = Counter()
        for participacao in campeonato.participacao_set.all():
            if participacao.grupo:
                grupos_count[participacao.grupo] += 1

        # Se não há grupos, começar com A
        if not grupos_count:
            return 'A'

        # Encontrar grupo com menor número de equipes
        grupos_disponiveis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for grupo in grupos_disponiveis:
            if grupos_count[grupo] < 4:  # Máximo 4 equipes por grupo
                return grupo

        # Se todos os grupos estão cheios, retornar A
        return 'A'


class ClassificacaoService:
    """Serviço para gerenciamento de classificações"""

    @staticmethod
    def atualizar_classificacao_campeonato(campeonato):
        """Atualiza a classificação completa de um campeonato"""
        with transaction.atomic():
            # Buscar ou criar classificações para todas as equipes do campeonato
            for participacao in campeonato.participacao_set.all():
                classificacao, created = Classificacao.objects.get_or_create(
                    campeonato=campeonato,
                    equipe=participacao.equipe,
                    defaults={'grupo': participacao.grupo}
                )

                # Atualizar grupo se necessário
                if classificacao.grupo != participacao.grupo:
                    classificacao.grupo = participacao.grupo

                # Recalcular estatísticas
                classificacao.calcular_estatisticas()

    @staticmethod
    def obter_classificacao_por_grupo(campeonato, grupo=None):
        """Obtém a classificação filtrada por grupo"""
        classificacoes = Classificacao.objects.filter(campeonato=campeonato)

        if grupo:
            classificacoes = classificacoes.filter(grupo=grupo)

        return classificacoes.order_by('-pontos', '-saldo_gols', '-gols_pro', 'equipe__nome')


class PartidaService:
    """Serviço para gerenciamento de partidas"""

    @staticmethod
    def registrar_resultado(partida, gols_mandante, gols_visitante):
        """Registra o resultado de uma partida"""
        with transaction.atomic():
            partida.gols_mandante = gols_mandante
            partida.gols_visitante = gols_visitante
            partida.status = 'finalizada'
            partida.save()

            # Atualizar classificação do campeonato
            ClassificacaoService.atualizar_classificacao_campeonato(
                partida.rodada.campeonato)

    @staticmethod
    def obter_ultimos_resultados(limite=10):
        """Obtém os últimos resultados finalizados"""
        return Partida.objects.filter(
            status='finalizada'
        ).order_by('-data_hora', '-id')[:limite]

    @staticmethod
    def obter_proximas_partidas(limite=10):
        """Obtém as próximas partidas pendentes"""
        return Partida.objects.filter(
            status='pendente'
        ).order_by('data_hora', 'id')[:limite]

    @staticmethod
    def agendar_partida(partida, data_hora, local=None):
        """Agenda uma partida com data/horário e local específicos"""
        partida.data_hora = data_hora
        if local:
            partida.local = local
        partida.save()
        return partida

    @staticmethod
    def obter_partidas_por_data(campeonato, data_inicio=None, data_fim=None):
        """Obtém partidas de um campeonato filtradas por período"""
        partidas = Partida.objects.filter(rodada__campeonato=campeonato)

        if data_inicio:
            partidas = partidas.filter(data_hora__date__gte=data_inicio)
        if data_fim:
            partidas = partidas.filter(data_hora__date__lte=data_fim)

        return partidas.order_by('data_hora')

    @staticmethod
    def obter_partidas_por_rodada_agrupadas(campeonato):
        """Obtém partidas agrupadas por rodada"""
        rodadas = Rodada.objects.filter(
            campeonato=campeonato).prefetch_related('partida_set')

        resultado = []
        for rodada in rodadas:
            partidas = rodada.partida_set.all().order_by('data_hora')
            resultado.append({
                'rodada': rodada,
                'partidas': partidas,
                'total_partidas': partidas.count(),
                'partidas_finalizadas': partidas.filter(status='finalizada').count()
            })

        return resultado
