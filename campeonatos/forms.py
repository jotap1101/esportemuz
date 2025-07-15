from django import forms
from django.forms import ModelForm
from .models import Campeonato, Equipe, Partida, Participacao


class CampeonatoForm(ModelForm):
    class Meta:
        model = Campeonato
        fields = ['nome', 'ano', 'tipo', 'numero_grupos', 'times_por_grupo', 'classificados_por_grupo']
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
        fields = ['local', 'data_hora', 'gols_mandante', 'gols_visitante', 'status']
        widgets = {
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local da partida'
            }),
            'data_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
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
            })
        }


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
