from django import forms
from .models import Ativo, TunelPreco, Periodicidade

class AtivoForm(forms.ModelForm):
    limite_inferior = forms.DecimalField(
        label='Limite Inferior (R$)',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    limite_superior = forms.DecimalField(
        label='Limite Superior (R$)',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    tipo_tunel = forms.ChoiceField(
        label='Tipo de Túnel',
        choices=[
            ("estatico", "Estático"),
            ("dinamico", "Dinâmico"),
            ("assincrono", "Assíncrono"),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periodicidade_minutos = forms.IntegerField(
        label='Periodicidade (minutos)',
        min_value=1,
        max_value=1440,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Ativo
        fields = ['codigo', 'nome']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PETR4'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Petrobras PN'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Se é uma edição, carregar valores existentes
            try:
                tunel = self.instance.tunel
                self.fields['limite_inferior'].initial = tunel.limite_inferior
                self.fields['limite_superior'].initial = tunel.limite_superior
                self.fields['tipo_tunel'].initial = tunel.tipo
            except TunelPreco.DoesNotExist:
                pass
            
            try:
                periodicidade = self.instance.periodicidade
                self.fields['periodicidade_minutos'].initial = periodicidade.minutos
            except Periodicidade.DoesNotExist:
                pass

    def save(self, commit=True):
        ativo = super().save(commit=False)
        if commit:
            ativo.save()
            
            # Salvar túnel de preço
            tunel, created = TunelPreco.objects.get_or_create(ativo=ativo)
            tunel.limite_inferior = self.cleaned_data['limite_inferior']
            tunel.limite_superior = self.cleaned_data['limite_superior']
            tunel.tipo = self.cleaned_data['tipo_tunel']
            tunel.save()
            
            # Salvar periodicidade
            periodicidade, created = Periodicidade.objects.get_or_create(ativo=ativo)
            periodicidade.minutos = self.cleaned_data['periodicidade_minutos']
            periodicidade.save()
            
        return ativo 