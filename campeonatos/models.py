from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Sum, Count


class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    escudo = models.ImageField(upload_to='escudos/', blank=True, null=True)
    cidade = models.CharField(max_length=100)
    representante = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

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
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
    ]

    nome = models.CharField(max_length=200)
    ano = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2030)])
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default='pontos_corridos')
    numero_grupos = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])
    times_por_grupo = models.IntegerField(
        default=8, validators=[MinValueValidator(2), MaxValueValidator(20)])
    classificados_por_grupo = models.IntegerField(
        default=4, validators=[MinValueValidator(1), MaxValueValidator(10)])
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='planejado')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Campeonato"
        verbose_name_plural = "Campeonatos"
        ordering = ['-ano', 'nome']

    def __str__(self):
        return f"{self.nome} - {self.ano}"

    def total_equipes(self):
        return self.participacao_set.count()

    def atualizar_status(self):
        """Atualiza automaticamente o status do campeonato"""
        partidas = Partida.objects.filter(rodada__campeonato=self)
        total_partidas = partidas.count()

        if total_partidas == 0:
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


class ConfiguracaoRodada(models.Model):
    TIPO_CONFIGURACAO_CHOICES = [
        ('manual', 'Manual - Organizador escolhe as partidas'),
        ('automatica', 'Automática - Sistema distribui aleatoriamente'),
    ]

    campeonato = models.OneToOneField(
        Campeonato, on_delete=models.CASCADE, related_name='configuracao_rodada')
    tipo_configuracao = models.CharField(
        max_length=20, choices=TIPO_CONFIGURACAO_CHOICES, default='manual')
    partidas_por_rodada = models.IntegerField(
        default=1, validators=[MinValueValidator(1)])
    dias_entre_rodadas = models.IntegerField(
        default=7, validators=[MinValueValidator(1)])
    data_inicio_campeonato = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Configuração de Rodada"
        verbose_name_plural = "Configurações de Rodada"

    def __str__(self):
        return f"Configuração - {self.campeonato.nome}"


class Rodada(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    numero = models.IntegerField()
    nome = models.CharField(max_length=100, blank=True)
    data_rodada = models.DateField(blank=True, null=True)
    local_padrao = models.CharField(
        max_length=200, blank=True, help_text="Local padrão para todas as partidas desta rodada")

    class Meta:
        verbose_name = "Rodada"
        verbose_name_plural = "Rodadas"
        unique_together = ('campeonato', 'numero')
        ordering = ['campeonato', 'numero']

    def __str__(self):
        return f"{self.campeonato.nome} - Rodada {self.numero}"

    def save(self, *args, **kwargs):
        if not self.nome:
            self.nome = f"Rodada {self.numero}"
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


class Partida(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('finalizada', 'Finalizada'),
        ('adiada', 'Adiada'),
        ('cancelada', 'Cancelada'),
    ]

    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE)
    equipe_mandante = models.ForeignKey(
        Equipe, on_delete=models.CASCADE, related_name='partidas_mandante')
    equipe_visitante = models.ForeignKey(
        Equipe, on_delete=models.CASCADE, related_name='partidas_visitante')
    local = models.CharField(max_length=200, blank=True)
    data_partida = models.DateField(blank=True, null=True)
    horario = models.TimeField(blank=True, null=True)
    gols_mandante = models.IntegerField(
        default=0, validators=[MinValueValidator(0)])
    gols_visitante = models.IntegerField(
        default=0, validators=[MinValueValidator(0)])
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField(
        blank=True, help_text="Observações sobre a partida")

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ['rodada__numero', 'data_partida', 'horario']

    def __str__(self):
        if self.status == 'finalizada':
            return f"{self.equipe_mandante.nome} {self.gols_mandante} x {self.gols_visitante} {self.equipe_visitante.nome}"
        return f"{self.equipe_mandante.nome} x {self.equipe_visitante.nome}"

    def resultado(self):
        if self.status == 'finalizada':
            if self.gols_mandante > self.gols_visitante:
                return 'vitoria_mandante'
            elif self.gols_visitante > self.gols_mandante:
                return 'vitoria_visitante'
            else:
                return 'empate'
        return None

    def data_hora_completa(self):
        """Retorna data e horário combinados se ambos estiverem definidos"""
        if self.data_partida and self.horario:
            from datetime import datetime
            return datetime.combine(self.data_partida, self.horario)
        return None

    def save(self, *args, **kwargs):
        # Se não há local definido, usar o local padrão da rodada
        if not self.local and self.rodada.local_padrao:
            self.local = self.rodada.local_padrao

        # Se não há data definida, usar a data da rodada
        if not self.data_partida and self.rodada.data_rodada:
            self.data_partida = self.rodada.data_rodada

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
