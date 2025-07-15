from django.core.management.base import BaseCommand
from campeonatos.models import Equipe, Campeonato
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Cria dados de teste para o sistema'

    def handle(self, *args, **options):
        # Criar equipes
        equipes_data = [
            {'nome': 'Atlético FC', 'cidade': 'São Paulo', 'representante': 'João Silva'},
            {'nome': 'Barcelona United', 'cidade': 'Rio de Janeiro', 'representante': 'Maria Santos'},
            {'nome': 'Corinthians Sport', 'cidade': 'Belo Horizonte', 'representante': 'Pedro Costa'},
            {'nome': 'Dinamite FC', 'cidade': 'Salvador', 'representante': 'Ana Lima'},
            {'nome': 'Estrela Azul', 'cidade': 'Recife', 'representante': 'Carlos Oliveira'},
            {'nome': 'Falcões do Norte', 'cidade': 'Fortaleza', 'representante': 'Luiza Fernandes'},
            {'nome': 'Guardiões SC', 'cidade': 'Porto Alegre', 'representante': 'Roberto Alves'},
            {'nome': 'Hurricanes FC', 'cidade': 'Curitiba', 'representante': 'Fernanda Rocha'},
        ]

        for equipe_data in equipes_data:
            equipe, created = Equipe.objects.get_or_create(
                nome=equipe_data['nome'],
                defaults={
                    'cidade': equipe_data['cidade'],
                    'representante': equipe_data['representante']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Equipe "{equipe.nome}" criada com sucesso')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Equipe "{equipe.nome}" já existe')
                )

        # Criar um campeonato de teste
        campeonato, created = Campeonato.objects.get_or_create(
            nome='Campeonato de Teste',
            defaults={
                'tipo': 'pontos_corridos',
                'data_inicio': date.today(),
                'data_fim': date.today() + timedelta(days=30),
                'status': 'inscricoes_abertas'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Campeonato "{campeonato.nome}" criado com sucesso')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Campeonato "{campeonato.nome}" já existe')
            )

        self.stdout.write(
            self.style.SUCCESS('Dados de teste criados com sucesso!')
        )
