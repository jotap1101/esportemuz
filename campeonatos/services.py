import random
from itertools import combinations
from django.db import transaction
from .models import Campeonato, Equipe, Participacao, Rodada, Partida, Classificacao


class CampeonatoService:
    """Serviço para gerenciamento de campeonatos"""
    
    @staticmethod
    def gerar_rodadas_pontos_corridos(campeonato):
        """Gera todas as rodadas para um campeonato de pontos corridos"""
        equipes = list(campeonato.participacao_set.all().values_list('equipe', flat=True))
        
        if len(equipes) < 2:
            raise ValueError("É necessário pelo menos 2 equipes para gerar as rodadas")
        
        # Limpar rodadas existentes
        Rodada.objects.filter(campeonato=campeonato).delete()
        
        # Gerar combinações de partidas (todos contra todos)
        partidas = list(combinations(equipes, 2))
        
        # Distribuir partidas em rodadas
        num_rodadas = len(equipes) - 1 if len(equipes) % 2 == 0 else len(equipes)
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
            ClassificacaoService.atualizar_classificacao_campeonato(partida.rodada.campeonato)
    
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
