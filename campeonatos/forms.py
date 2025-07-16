from django import forms
from django.forms import ModelForm
from .models import Campeonato, Equipe, Partida, Participacao, ConfiguracaoRodada, Rodada


class ConfiguracaoRodadaForm(ModelForm):
    class Meta:
        model = ConfiguracaoRodada
        fields = ['tipo_configuracao', 'partidas_por_rodada',
                  'dias_entre_rodadas', 'data_inicio_campeonato']
        widgets = {
            'tipo_configuracao': forms.Select(attrs={
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
            'data_inicio_campeonato': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_configuracao'].help_text = "Manual: Você escolhe as partidas. Automática: Sistema distribui aleatoriamente."
        self.fields['partidas_por_rodada'].help_text = "Quantas partidas por rodada/data."
        self.fields['dias_entre_rodadas'].help_text = "Intervalo de dias entre as rodadas."


class RodadaForm(ModelForm):
    class Meta:
        model = Rodada
        fields = ['nome', 'data_rodada', 'local_padrao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da rodada'
            }),
            'data_rodada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'local_padrao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local padrão para todas as partidas desta rodada'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['local_padrao'].help_text = "Local que será usado para todas as partidas desta rodada se não especificado individualmente."


class CampeonatoForm(ModelForm):
    class Meta:
        model = Campeonato
        fields = ['nome', 'ano', 'tipo', 'numero_grupos',
                  'times_por_grupo', 'classificados_por_grupo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do campeonato'
            }),
            'ano': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2020,
                'max': 2030
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].required = True
        self.fields['ano'].required = True


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


class PartidaForm(ModelForm):
    class Meta:
        model = Partida
        fields = ['local', 'data_partida', 'horario',
                  'gols_mandante', 'gols_visitante', 'status', 'observacoes']
        widgets = {
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local da partida'
            }),
            'data_partida': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'horario': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'gols_mandante': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'gols_visitante': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a partida'
            })
        }


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
    horario = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    data_partida = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Se não especificado, usará a data da rodada"
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
