from django import forms
from django.forms import ModelForm
from .models import Campeonato, Equipe, Partida, Participacao, Rodada


class CampeonatoForm(ModelForm):
    class Meta:
        model = Campeonato
        fields = [
            'nome', 'descricao', 'ano', 'tipo', 
            'data_inicio', 'data_fim_prevista', 'local_padrao',
            'numero_grupos', 'times_por_grupo', 'classificados_por_grupo',
            'fase_inicial_mata_mata', 'max_equipes', 'classificacao_inicial',
            'permite_empate', 'tipo_geracao_rodada', 'partidas_por_rodada',
            'dias_entre_rodadas'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do campeonato'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do campeonato'
            }),
            'ano': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2020,
                'max': 2030
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim_prevista': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'local_padrao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local padrão das partidas'
            }),
            'numero_grupos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 8
            }),
            'times_por_grupo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2,
                'max': 20
            }),
            'classificados_por_grupo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'fase_inicial_mata_mata': forms.Select(attrs={
                'class': 'form-select'
            }),
            'max_equipes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2
            }),
            'classificacao_inicial': forms.Select(attrs={
                'class': 'form-select'
            }),
            'permite_empate': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tipo_geracao_rodada': forms.Select(attrs={
                'class': 'form-select'
            }),
            'partidas_por_rodada': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'dias_entre_rodadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 30
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].required = True
        self.fields['ano'].required = True
        
        # Condicionalmente esconder campos baseado no tipo
        if 'tipo' in self.data:
            tipo = self.data['tipo']
            if tipo == 'pontos_corridos':
                # Para pontos corridos, esconder campos de grupos
                for field in ['numero_grupos', 'times_por_grupo', 'classificados_por_grupo', 'fase_inicial_mata_mata']:
                    self.fields[field].widget = forms.HiddenInput()


class RodadaForm(ModelForm):
    class Meta:
        model = Rodada
        fields = ['nome', 'tipo_rodada', 'data_inicio', 'data_fim', 'local_padrao', 
                 'grupo', 'partidas_simultaneas', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da rodada'
            }),
            'tipo_rodada': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'local_padrao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local padrão para todas as partidas desta rodada'
            }),
            'grupo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'partidas_simultaneas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a rodada'
            }),
        }

    def __init__(self, *args, **kwargs):
        campeonato = kwargs.pop('campeonato', None)
        super().__init__(*args, **kwargs)
        
        if campeonato:
            # Configurar choices de grupo baseado no campeonato
            if campeonato.tipo == 'grupos_mata_mata':
                grupos_choices = [('', '--- Todos os grupos ---')]
                for i, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']):
                    if i < campeonato.numero_grupos:
                        grupos_choices.append((letter, f'Grupo {letter}'))
                self.fields['grupo'].choices = grupos_choices
            else:
                self.fields['grupo'].widget = forms.HiddenInput()


class PartidaForm(ModelForm):
    class Meta:
        model = Partida
        fields = ['equipe_mandante', 'equipe_visitante', 'local', 'data_hora',
                 'duracao_prevista', 'arbitro', 'observacoes']
        widgets = {
            'equipe_mandante': forms.Select(attrs={
                'class': 'form-select'
            }),
            'equipe_visitante': forms.Select(attrs={
                'class': 'form-select'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local da partida'
            }),
            'data_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duracao_prevista': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 30,
                'max': 180
            }),
            'arbitro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do árbitro'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a partida'
            }),
        }

    def __init__(self, *args, **kwargs):
        rodada = kwargs.pop('rodada', None)
        super().__init__(*args, **kwargs)
        
        if rodada:
            # Filtrar equipes baseado no campeonato e grupo (se aplicável)
            participacoes = rodada.campeonato.participacao_set.all()
            
            if rodada.grupo:
                participacoes = participacoes.filter(grupo=rodada.grupo)
            
            equipes = [p.equipe for p in participacoes]
            choices = [(e.id, e.nome) for e in equipes]
            
            self.fields['equipe_mandante'].choices = [('', '--- Selecione ---')] + choices
            self.fields['equipe_visitante'].choices = [('', '--- Selecione ---')] + choices


class ResultadoPartidaForm(forms.Form):
    gols_mandante = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0
        })
    )
    gols_visitante = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0
        })
    )
    penaltis_mandante = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0
        })
    )
    penaltis_visitante = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0
        })
    )
    arbitro = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do árbitro'
        })
    )
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observações sobre a partida'
        })
    )


class EquipeForm(ModelForm):
    class Meta:
        model = Equipe
        fields = ['nome', 'escudo', 'cidade', 'representante']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da equipe'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade da equipe'
            }),
            'representante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do representante'
            }),
            'escudo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].required = True
        self.fields['cidade'].required = True
        self.fields['representante'].required = True


class PartidaManualForm(forms.Form):
    """Formulário para adicionar partidas manualmente a uma rodada"""
    equipe_mandante = forms.ModelChoiceField(
        queryset=Equipe.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Equipe Mandante"
    )
    equipe_visitante = forms.ModelChoiceField(
        queryset=Equipe.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Equipe Visitante"
    )
    local = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Local da partida (opcional)'
        })
    )
    data_hora = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        help_text="Se não especificado, usará a data da rodada"
    )
    duracao_prevista = forms.IntegerField(
        initial=90,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 30,
            'max': 180
        }),
        help_text="Duração em minutos"
    )
    arbitro = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do árbitro (opcional)'
        })
    )

    def __init__(self, campeonato=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if campeonato:
            equipes = Equipe.objects.filter(
                participacao__campeonato=campeonato)
            self.fields['equipe_mandante'].queryset = equipes
            self.fields['equipe_visitante'].queryset = equipes

    def clean(self):
        cleaned_data = super().clean()
        equipe_mandante = cleaned_data.get('equipe_mandante')
        equipe_visitante = cleaned_data.get('equipe_visitante')

        if equipe_mandante and equipe_visitante and equipe_mandante == equipe_visitante:
            raise forms.ValidationError(
                "Uma equipe não pode jogar contra si mesma.")

        return cleaned_data


class ParticipacaoForm(ModelForm):
    class Meta:
        model = Participacao
        fields = ['equipe', 'grupo']
        widgets = {
            'equipe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'grupo': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, campeonato=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if campeonato:
            # Mostrar apenas equipes que não estão no campeonato
            equipes_no_campeonato = Equipe.objects.exclude(
                participacao__campeonato=campeonato
            )
            self.fields['equipe'].queryset = equipes_no_campeonato


class FiltroPartidaForm(forms.Form):
    """Formulário para filtrar partidas"""
    campeonato = forms.ModelChoiceField(
        queryset=Campeonato.objects.all(),
        required=False,
        empty_label="Todos os campeonatos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Partida.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class FiltroCampeonatoForm(forms.Form):
    """Formulário para filtrar campeonatos"""
    ano = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ano'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Campeonato.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome...'
        })
    )
