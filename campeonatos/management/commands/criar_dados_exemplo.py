from django.core.management.base import BaseCommand
from campeonatos.models import Equipe, Campeonato, Participacao, Rodada, Partida, Classificacao
from campeonatos.services import CampeonatoService, ClassificacaoService
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Cria dados de exemplo para o sistema'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados de exemplo...')
        
        # Criar equipes
        equipes_data = [
            {'nome': 'Santos FC', 'cidade': 'Santos', 'representante': 'João Silva'},
            {'nome': 'Corinthians', 'cidade': 'São Paulo', 'representante': 'Maria Santos'},
            {'nome': 'Palmeiras', 'cidade': 'São Paulo', 'representante': 'Pedro Costa'},
            {'nome': 'São Paulo FC', 'cidade': 'São Paulo', 'representante': 'Ana Oliveira'},
            {'nome': 'Flamengo', 'cidade': 'Rio de Janeiro', 'representante': 'Carlos Mendes'},
            {'nome': 'Vasco da Gama', 'cidade': 'Rio de Janeiro', 'representante': 'Luiza Pereira'},
            {'nome': 'Botafogo', 'cidade': 'Rio de Janeiro', 'representante': 'Roberto Lima'},
            {'nome': 'Fluminense', 'cidade': 'Rio de Janeiro', 'representante': 'Fernanda Rosa'},
        ]
        
        equipes = []
        for data in equipes_data:
            equipe, created = Equipe.objects.get_or_create(
                nome=data['nome'],
                defaults=data
            )
            equipes.append(equipe)
            if created:
                self.stdout.write(f'Equipe criada: {equipe.nome}')
        
        # Criar campeonato de pontos corridos
        campeonato_pc, created = Campeonato.objects.get_or_create(
            nome='Campeonato Municipal 2024',
            ano=2024,
            defaults={
                'tipo': 'pontos_corridos',
                'status': 'em_andamento'
            }
        )
        
        if created:
            self.stdout.write(f'Campeonato criado: {campeonato_pc.nome}')
            
            # Adicionar equipes ao campeonato
            for equipe in equipes[:6]:  # Apenas 6 equipes para pontos corridos
                Participacao.objects.get_or_create(
                    campeonato=campeonato_pc,
                    equipe=equipe
                )
            
            # Gerar rodadas
            CampeonatoService.gerar_rodadas_pontos_corridos(campeonato_pc)
            self.stdout.write('Rodadas geradas para pontos corridos')
            
            # Simular alguns resultados
            partidas = Partida.objects.filter(rodada__campeonato=campeonato_pc)[:10]
            for partida in partidas:
                gols_mandante = random.randint(0, 4)
                gols_visitante = random.randint(0, 4)
                partida.gols_mandante = gols_mandante
                partida.gols_visitante = gols_visitante
                partida.status = 'finalizada'
                partida.save()
            
            # Atualizar classificação
            ClassificacaoService.atualizar_classificacao_campeonato(campeonato_pc)
            self.stdout.write('Resultados simulados e classificação atualizada')
        
        # Criar campeonato com grupos
        campeonato_grupos, created = Campeonato.objects.get_or_create(
            nome='Copa Regional 2024',
            ano=2024,
            defaults={
                'tipo': 'grupos_mata_mata',
                'numero_grupos': 2,
                'times_por_grupo': 4,
                'classificados_por_grupo': 2,
                'status': 'planejado'
            }
        )
        
        if created:
            self.stdout.write(f'Campeonato criado: {campeonato_grupos.nome}')
            
            # Adicionar todas as equipes
            for equipe in equipes:
                Participacao.objects.get_or_create(
                    campeonato=campeonato_grupos,
                    equipe=equipe
                )
            
            # Gerar grupos e rodadas
            CampeonatoService.gerar_rodadas_grupos(campeonato_grupos)
            self.stdout.write('Grupos e rodadas geradas')
            
            # Atualizar classificação
            ClassificacaoService.atualizar_classificacao_campeonato(campeonato_grupos)
        
        self.stdout.write(
            self.style.SUCCESS('Dados de exemplo criados com sucesso!')
        )
