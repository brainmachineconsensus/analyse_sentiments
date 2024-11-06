# bert_app/forms.py
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Sondage, Question, Tranche_age, Categorie, Categorie_option

class SondageForm(forms.ModelForm):
    class Meta:
        model = Sondage
        fields = ['titre', 'active_sex_option']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du Sondage'}),
            'active_sex_option': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question']
        widgets = {'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Question'})}

class TrancheAgeForm(forms.ModelForm):
    class Meta:
        model = Tranche_age
        fields = ['debut', 'fin']
        widgets = {
            'debut': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Début'}),
            'fin': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fin'}),
        }

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['titre']
        widgets = {'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la catégorie'})}

class CategorieOptionForm(forms.ModelForm):
    class Meta:
        model = Categorie_option
        fields = ['option']
        widgets = {'option': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option'})}

# Formsets
QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=1)
TrancheAgeFormSet = modelformset_factory(Tranche_age, form=TrancheAgeForm, extra=1)
CategorieFormSet = modelformset_factory(Categorie, form=CategorieForm, extra=1)
CategorieOptionFormSet = inlineformset_factory(Categorie, Categorie_option, form=CategorieOptionForm, extra=1)
