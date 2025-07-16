from django.contrib import admin
from django.utils.html import format_html
from .models import Equipe, Campeonato, Participacao, Rodada, Partida, Classificacao


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'representante',
                    'escudo_preview', 'criado_em')
    list_filter = ('cidade', 'criado_em')
    search_fields = ('nome', 'cidade', 'representante')
    readonly_fields = ('criado_em',)

    def escudo_preview(self, obj):
        if obj.escudo:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.escudo.url)
        return "Sem escudo"
    escudo_preview.short_description = "Escudo"


@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ano', 'tipo', 'status',
                    'total_equipes', 'data_inicio', 'criado_em')
    list_filter = ('ano', 'tipo', 'status', 'classificacao_inicial', 'criado_em')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em')

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ano', 'tipo', 'status')
        }),
        ('Datas e Local', {
            'fields': ('data_inicio', 'data_fim_prevista', 'local_padrao')
        }),
        ('Configurações de Grupos (apenas para Grupos + Mata-mata)', {
            'fields': ('numero_grupos', 'times_por_grupo', 'classificados_por_grupo', 'fase_inicial_mata_mata'),
            'classes': ('collapse',)
        }),
        ('Configurações de Equipes', {
            'fields': ('max_equipes', 'classificacao_inicial', 'permite_empate')
        }),
        ('Configurações de Rodadas', {
            'fields': ('tipo_geracao_rodada', 'partidas_por_rodada', 'dias_entre_rodadas'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        })
    )


class ParticipacaoInline(admin.TabularInline):
    model = Participacao
    extra = 0
    autocomplete_fields = ('equipe',)


@admin.register(Participacao)
class ParticipacaoAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'campeonato', 'grupo')
    list_filter = ('campeonato', 'grupo')
    search_fields = ('equipe__nome', 'campeonato__nome')
    autocomplete_fields = ('equipe', 'campeonato')


@admin.register(Rodada)
class RodadaAdmin(admin.ModelAdmin):
    list_display = ('campeonato', 'numero', 'nome', 'tipo_rodada',
                    'data_inicio', 'grupo', 'total_partidas')
    list_filter = ('campeonato', 'tipo_rodada', 'grupo', 'data_inicio')
    search_fields = ('campeonato__nome', 'nome')
    readonly_fields = ('criado_em', 'atualizado_em')

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('campeonato', 'numero', 'nome', 'tipo_rodada')
        }),
        ('Datas e Local', {
            'fields': ('data_inicio', 'data_fim', 'local_padrao')
        }),
        ('Configurações', {
            'fields': ('grupo', 'partidas_simultaneas', 'observacoes')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        })
    )

    def total_partidas(self, obj):
        return obj.partida_set.count()
    total_partidas.short_description = "Total de Partidas"


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'rodada', 'local', 'data_hora',
                    'status', 'arbitro', 'resultado_display')
    list_filter = ('status', 'rodada__campeonato', 'rodada__tipo_rodada')
    search_fields = ('equipe_mandante__nome',
                     'equipe_visitante__nome', 'local', 'arbitro')
    autocomplete_fields = ('equipe_mandante', 'equipe_visitante')
    readonly_fields = ('criado_em', 'atualizado_em', 'resultado_registrado_em')

    fieldsets = (
        ('Partida', {
            'fields': ('rodada', 'equipe_mandante', 'equipe_visitante')
        }),
        ('Local e Horário', {
            'fields': ('local', 'data_hora', 'duracao_prevista')
        }),
        ('Status e Observações', {
            'fields': ('status', 'arbitro', 'observacoes')
        }),
        ('Resultado', {
            'fields': ('gols_mandante', 'gols_visitante', 'penaltis_mandante', 'penaltis_visitante'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'resultado_registrado_em'),
            'classes': ('collapse',)
        })
    )

    def resultado_display(self, obj):
        if obj.status == 'finalizada':
            return f"{obj.gols_mandante} x {obj.gols_visitante}"
        return "Pendente"
    resultado_display.short_description = "Resultado"


@admin.register(Classificacao)
class ClassificacaoAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'campeonato', 'grupo', 'pontos',
                    'jogos', 'vitorias', 'empates', 'derrotas', 'saldo_gols')
    list_filter = ('campeonato', 'grupo')
    search_fields = ('equipe__nome', 'campeonato__nome')
    readonly_fields = ('jogos', 'vitorias', 'empates', 'derrotas',
                       'gols_pro', 'gols_contra', 'saldo_gols', 'pontos')

    def has_add_permission(self, request):
        # Classificações são criadas automaticamente
        return False


# Personalização do site admin
admin.site.site_header = "EsporteMuz - Administração"
admin.site.site_title = "EsporteMuz Admin"
admin.site.index_title = "Gerenciamento de Campeonatos"
