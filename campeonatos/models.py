from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Sum, Count


class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    escudo = models.ImageField(upload_to='escudos/', blank=True, null=True)
    cidade = models.CharField(max_length=100)
    representante = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Equipe"
        verbose_name_plural = "Equipes"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Campeonato(models.Model):
    TIPO_CHOICES = [
        ('pontos_corridos', 'Pontos Corridos'),
        ('grupos_mata_mata', 'Grupos + Mata-mata'),
    ]

    STATUS_CHOICES = [
        ('planejado', 'Planejado'),
        ('inscricoes_abertas', 'Inscrições Abertas'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    CLASSIFICACAO_INICIAL_CHOICES = [
        ('alfabetica', 'Ordem Alfabética'),
        ('aleatoria', 'Ordem Aleatória'),
        ('manual', 'Definição Manual'),
        ('ranking', 'Por Ranking/Histórico'),
    ]

    FASE_MATA_MATA_CHOICES = [
        ('oitavas', 'Oitavas de Final'),
        ('quartas', 'Quartas de Final'),
        ('semifinal', 'Semifinal'),
        ('final', 'Final'),
    ]

    TIPO_RODADA_CHOICES = [
        ('manual', 'Manual - Organizador define'),
        ('automatica', 'Automática - Sistema distribui'),
        ('hibrida', 'Híbrida - Mista'),
    ]

    # Informações básicas
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, help_text="Descrição do campeonato")
    ano = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2030)])
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default='pontos_corridos')
    
    # Datas e localização
    data_inicio = models.DateField(blank=True, null=True, help_text="Data prevista de início")
    data_fim_prevista = models.DateField(blank=True, null=True, help_text="Data prevista de término")
    local_padrao = models.CharField(max_length=200, blank=True, help_text="Local padrão para as partidas")
    
    # Configurações de grupos (para grupos + mata-mata)
    numero_grupos = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])
    times_por_grupo = models.IntegerField(
        default=8, validators=[MinValueValidator(2), MaxValueValidator(20)])
    classificados_por_grupo = models.IntegerField(
        default=4, validators=[MinValueValidator(1), MaxValueValidator(10)])
    fase_inicial_mata_mata = models.CharField(
        max_length=20, choices=FASE_MATA_MATA_CHOICES, default='quartas',
        help_text="A partir de qual fase começará o mata-mata")
    
    # Configurações de equipes e classificação
    max_equipes = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(2)],
        help_text="Número máximo de equipes (deixe em branco para ilimitado)")
    classificacao_inicial = models.CharField(
        max_length=20, choices=CLASSIFICACAO_INICIAL_CHOICES, default='alfabetica')
    permite_empate = models.BooleanField(default=True, help_text="Se permite empates nas partidas")
    
    # Configurações de rodadas
    tipo_geracao_rodada = models.CharField(
        max_length=20, choices=TIPO_RODADA_CHOICES, default='manual')
    partidas_por_rodada = models.IntegerField(
        default=1, validators=[MinValueValidator(1)],
        help_text="Quantas partidas por rodada (para geração automática)")
    dias_entre_rodadas = models.IntegerField(
        default=7, validators=[MinValueValidator(1)],
        help_text="Intervalo em dias entre rodadas")
    
    # Status e metadados
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='planejado')
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Campeonato"
        verbose_name_plural = "Campeonatos"
        ordering = ['-ano', 'nome']

    def __str__(self):
        return f"{self.nome} - {self.ano}"

    def total_equipes(self):
        return self.participacao_set.count()
    
    def pode_adicionar_equipes(self):
        """Verifica se ainda é possível adicionar equipes"""
        if self.status not in ['planejado', 'inscricoes_abertas']:
            return False
        if self.max_equipes and self.total_equipes() >= self.max_equipes:
            return False
        return True
    
    def pode_remover_equipes(self):
        """Verifica se ainda é possível remover equipes"""
        return self.status in ['planejado', 'inscricoes_abertas']
    
    def grupos_necessarios(self):
        """Calcula quantos grupos são realmente necessários baseado no número de equipes"""
        total_equipes = self.total_equipes()
        if total_equipes == 0 or self.tipo == 'pontos_corridos':
            return 1
        
        # Para grupos + mata-mata, calcular baseado nas configurações
        grupos_minimos = max(1, (total_equipes + self.times_por_grupo - 1) // self.times_por_grupo)
        return min(grupos_minimos, self.numero_grupos)
    
    def distribuir_equipes_grupos(self):
        """Distribui equipes pelos grupos conforme configuração inicial"""
        participacoes = self.participacao_set.all()
        
        if self.tipo == 'pontos_corridos':
            # Para pontos corridos, todas ficam sem grupo
            participacoes.update(grupo=None)
            return
        
        # Para grupos + mata-mata
        grupos_disponiveis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'][:self.grupos_necessarios()]
        
        if self.classificacao_inicial == 'alfabetica':
            participacoes = participacoes.order_by('equipe__nome')
        elif self.classificacao_inicial == 'aleatoria':
            import random
            participacoes = list(participacoes)
            random.shuffle(participacoes)
        
        # Distribuir equipes pelos grupos de forma equilibrada
        for i, participacao in enumerate(participacoes):
            grupo_index = i % len(grupos_disponiveis)
            participacao.grupo = grupos_disponiveis[grupo_index]
            participacao.save()

    def atualizar_status(self):
        """Atualiza automaticamente o status do campeonato"""
        partidas = Partida.objects.filter(rodada__campeonato=self)
        total_partidas = partidas.count()

        if total_partidas == 0:
            # Se não há partidas, manter status atual se for planejado ou inscrições abertas
            if self.status not in ['planejado', 'inscricoes_abertas']:
                self.status = 'planejado'
        elif partidas.filter(status='finalizada').count() == total_partidas:
            self.status = 'finalizado'
        else:
            self.status = 'em_andamento'

        self.save()


class Participacao(models.Model):
    GRUPOS_CHOICES = [
        ('A', 'Grupo A'), ('B', 'Grupo B'), ('C', 'Grupo C'), ('D', 'Grupo D'),
        ('E', 'Grupo E'), ('F', 'Grupo F'), ('G', 'Grupo G'), ('H', 'Grupo H'),
    ]

    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    grupo = models.CharField(
        max_length=1, choices=GRUPOS_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = "Participação"
        verbose_name_plural = "Participações"
        unique_together = ('campeonato', 'equipe')

    def __str__(self):
        grupo_str = f" - Grupo {self.grupo}" if self.grupo else ""
        return f"{self.equipe.nome} em {self.campeonato.nome}{grupo_str}"


class Rodada(models.Model):
    TIPO_RODADA_CHOICES = [
        ('fase_grupos', 'Fase de Grupos'),
        ('oitavas', 'Oitavas de Final'),
        ('quartas', 'Quartas de Final'),
        ('semifinal', 'Semifinal'),
        ('final', 'Final'),
        ('terceiro_lugar', 'Disputa de 3º Lugar'),
        ('pontos_corridos', 'Pontos Corridos'),
    ]

    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    numero = models.IntegerField()
    nome = models.CharField(max_length=100, blank=True)
    tipo_rodada = models.CharField(
        max_length=20, choices=TIPO_RODADA_CHOICES, default='pontos_corridos')
    
    # Datas e local
    data_inicio = models.DateField(blank=True, null=True, help_text="Data de início da rodada")
    data_fim = models.DateField(blank=True, null=True, help_text="Data de fim da rodada")
    local_padrao = models.CharField(
        max_length=200, blank=True, help_text="Local padrão para todas as partidas desta rodada")
    
    # Grupo (para rodadas de grupos específicos)
    grupo = models.CharField(max_length=1, blank=True, null=True,
                           help_text="Grupo específico desta rodada (se aplicável)")
    
    # Configurações
    partidas_simultaneas = models.BooleanField(
        default=True, help_text="Se todas as partidas devem ocorrer no mesmo dia")
    observacoes = models.TextField(blank=True, help_text="Observações sobre a rodada")
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Rodada"
        verbose_name_plural = "Rodadas"
        unique_together = ('campeonato', 'numero')
        ordering = ['campeonato', 'numero']

    def __str__(self):
        return f"{self.campeonato.nome} - Rodada {self.numero}"

    def save(self, *args, **kwargs):
        if not self.nome:
            if self.tipo_rodada == 'pontos_corridos':
                self.nome = f"Rodada {self.numero}"
            elif self.grupo:
                self.nome = f"{self.get_tipo_rodada_display()} - Grupo {self.grupo}"
            else:
                self.nome = self.get_tipo_rodada_display()
        super().save(*args, **kwargs)

    def total_partidas(self):
        """Retorna o total de partidas da rodada"""
        return self.partida_set.count()

    def partidas_finalizadas(self):
        """Retorna o número de partidas finalizadas da rodada"""
        return self.partida_set.filter(status='finalizada').count()

    def is_finalizada(self):
        """Verifica se todas as partidas da rodada foram finalizadas"""
        return self.total_partidas() > 0 and self.partidas_finalizadas() == self.total_partidas()
    
    def pode_ser_editada(self):
        """Verifica se a rodada ainda pode ser editada"""
        return self.partidas_finalizadas() == 0
    
    def proxima_data_disponivel(self):
        """Calcula a próxima data disponível para esta rodada"""
        if self.data_inicio:
            return self.data_inicio
        
        # Buscar a última rodada finalizada
        ultima_rodada = Rodada.objects.filter(
            campeonato=self.campeonato,
            numero__lt=self.numero,
            data_fim__isnull=False
        ).order_by('-numero').first()
        
        if ultima_rodada:
            from datetime import timedelta
            return ultima_rodada.data_fim + timedelta(days=self.campeonato.dias_entre_rodadas)
        
        return self.campeonato.data_inicio


class Partida(models.Model):
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('finalizada', 'Finalizada'),
        ('adiada', 'Adiada'),
        ('cancelada', 'Cancelada'),
        ('w_o', 'W.O. (Walkover)'),
    ]

    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE)
    equipe_mandante = models.ForeignKey(
        Equipe, on_delete=models.CASCADE, related_name='partidas_mandante')
    equipe_visitante = models.ForeignKey(
        Equipe, on_delete=models.CASCADE, related_name='partidas_visitante')
    
    # Local e horário
    local = models.CharField(max_length=200, blank=True)
    data_hora = models.DateTimeField(blank=True, null=True, help_text="Data e horário da partida")
    duracao_prevista = models.IntegerField(
        default=90, validators=[MinValueValidator(30)], help_text="Duração em minutos")
    
    # Resultados
    gols_mandante = models.IntegerField(
        default=0, validators=[MinValueValidator(0)])
    gols_visitante = models.IntegerField(
        default=0, validators=[MinValueValidator(0)])
    penaltis_mandante = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    penaltis_visitante = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], blank=True, null=True)
    
    # Status e observações
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='agendada')
    observacoes = models.TextField(
        blank=True, help_text="Observações sobre a partida")
    arbitro = models.CharField(max_length=100, blank=True, help_text="Nome do árbitro")
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True, blank=True)
    resultado_registrado_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ['rodada__numero', 'data_hora']

    def __str__(self):
        if self.status == 'finalizada':
            if self.penaltis_mandante is not None and self.penaltis_visitante is not None:
                return f"{self.equipe_mandante.nome} {self.gols_mandante}({self.penaltis_mandante}) x {self.gols_visitante}({self.penaltis_visitante}) {self.equipe_visitante.nome}"
            return f"{self.equipe_mandante.nome} {self.gols_mandante} x {self.gols_visitante} {self.equipe_visitante.nome}"
        return f"{self.equipe_mandante.nome} x {self.equipe_visitante.nome}"

    def resultado(self):
        """Determina o resultado da partida"""
        if self.status not in ['finalizada', 'w_o']:
            return None
            
        if self.status == 'w_o':
            return 'w_o'
            
        # Resultado normal
        if self.gols_mandante > self.gols_visitante:
            return 'vitoria_mandante'
        elif self.gols_visitante > self.gols_mandante:
            return 'vitoria_visitante'
        else:
            # Empate - verificar se há pênaltis (mata-mata)
            if self.penaltis_mandante is not None and self.penaltis_visitante is not None:
                if self.penaltis_mandante > self.penaltis_visitante:
                    return 'vitoria_mandante_penaltis'
                else:
                    return 'vitoria_visitante_penaltis'
            return 'empate'

    def pode_ter_empate(self):
        """Verifica se a partida pode terminar empatada"""
        if not self.rodada.campeonato.permite_empate:
            return False
        # Mata-mata não permite empate
        return self.rodada.tipo_rodada in ['pontos_corridos', 'fase_grupos']
    
    def is_mata_mata(self):
        """Verifica se é uma partida de mata-mata"""
        return self.rodada.tipo_rodada in ['oitavas', 'quartas', 'semifinal', 'final', 'terceiro_lugar']
    
    def equipe_vencedora(self):
        """Retorna a equipe vencedora da partida"""
        resultado = self.resultado()
        if resultado in ['vitoria_mandante', 'vitoria_mandante_penaltis']:
            return self.equipe_mandante
        elif resultado in ['vitoria_visitante', 'vitoria_visitante_penaltis']:
            return self.equipe_visitante
        return None

    def save(self, *args, **kwargs):
        # Se não há local definido, usar o local padrão da rodada ou do campeonato
        if not self.local:
            if self.rodada.local_padrao:
                self.local = self.rodada.local_padrao
            elif self.rodada.campeonato.local_padrao:
                self.local = self.rodada.campeonato.local_padrao

        # Se não há data definida, usar a data da rodada
        if not self.data_hora and self.rodada.data_inicio:
            from datetime import datetime, time
            self.data_hora = datetime.combine(self.rodada.data_inicio, time(15, 0))  # 15:00 padrão
        
        # Registrar quando o resultado foi inserido
        if self.status == 'finalizada' and not self.resultado_registrado_em:
            self.resultado_registrado_em = timezone.now()

        super().save(*args, **kwargs)

        # Atualizar classificação após salvar partida
        if self.status == 'finalizada':
            self.atualizar_classificacao()
            self.rodada.campeonato.atualizar_status()

    def atualizar_classificacao(self):
        """Atualiza a classificação das equipes após uma partida finalizada"""
        from .services import ClassificacaoService
        ClassificacaoService.atualizar_classificacao_campeonato(
            self.rodada.campeonato)


class Classificacao(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    grupo = models.CharField(max_length=1, blank=True, null=True)
    jogos = models.IntegerField(default=0)
    vitorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    gols_pro = models.IntegerField(default=0)
    gols_contra = models.IntegerField(default=0)
    saldo_gols = models.IntegerField(default=0)
    pontos = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Classificação"
        verbose_name_plural = "Classificações"
        unique_together = ('campeonato', 'equipe')
        ordering = ['-pontos', '-saldo_gols', '-gols_pro', 'equipe__nome']

    def __str__(self):
        return f"{self.equipe.nome} - {self.pontos} pts"

    def calcular_estatisticas(self):
        """Calcula todas as estatísticas da equipe no campeonato"""
        partidas_mandante = Partida.objects.filter(
            rodada__campeonato=self.campeonato,
            equipe_mandante=self.equipe,
            status='finalizada'
        )

        partidas_visitante = Partida.objects.filter(
            rodada__campeonato=self.campeonato,
            equipe_visitante=self.equipe,
            status='finalizada'
        )

        # Reset stats
        self.jogos = 0
        self.vitorias = 0
        self.empates = 0
        self.derrotas = 0
        self.gols_pro = 0
        self.gols_contra = 0

        # Partidas como mandante
        for partida in partidas_mandante:
            self.jogos += 1
            self.gols_pro += partida.gols_mandante
            self.gols_contra += partida.gols_visitante

            if partida.gols_mandante > partida.gols_visitante:
                self.vitorias += 1
            elif partida.gols_mandante < partida.gols_visitante:
                self.derrotas += 1
            else:
                self.empates += 1

        # Partidas como visitante
        for partida in partidas_visitante:
            self.jogos += 1
            self.gols_pro += partida.gols_visitante
            self.gols_contra += partida.gols_mandante

            if partida.gols_visitante > partida.gols_mandante:
                self.vitorias += 1
            elif partida.gols_visitante < partida.gols_mandante:
                self.derrotas += 1
            else:
                self.empates += 1

        # Calcular saldo e pontos
        self.saldo_gols = self.gols_pro - self.gols_contra
        self.pontos = (self.vitorias * 3) + self.empates

        self.save()
