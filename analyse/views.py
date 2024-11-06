import os
import torch
import torch.nn as nn
from transformers import AutoTokenizer, BertModel
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Sondage, Tranche_age, Question, Reponse
from django.db.models import Q

# Obtenir le répertoire courant
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construire le chemin absolu vers le modèle
MODEL_PATH = os.path.join(BASE_DIR, "my_custom_bert_sentense_Techup.pth")

# Définir le modèle personnalisé
class CustomBert(nn.Module):
    def __init__(self, model_name_or_path="bert-base-uncased", n_classes=2):
        super(CustomBert, self).__init__()
        self.bert_pretrained = BertModel.from_pretrained(model_name_or_path)
        self.classifier = nn.Linear(self.bert_pretrained.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        x = self.bert_pretrained(input_ids=input_ids, attention_mask=attention_mask)
        x = self.classifier(x.pooler_output)
        return x

# Charger le modèle et l’évaluer
model = CustomBert()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

# Charger le tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Vue principale
def index(request):
    if request.method == 'POST':
        texte = request.POST.get('texte')
        inputs = tokenizer(texte, padding="max_length", max_length=512, truncation=True, return_tensors="pt")

        with torch.no_grad():
            output = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])

        _, pred = output.max(1)
        labels = {0: 'positive', 1: 'negative'}
        prediction = labels[pred.item()]

        return render(request, 'index.html', {'result': prediction})

    return render(request, 'index.html')

# Liste des sondages de l'utilisateur
@login_required
def sondage_list(request):
    sondages = Sondage.objects.filter(user=request.user)
    return render(request, 'sondage_list.html', {'sondages': sondages})

# Création d'un sondage
@login_required
def sondage_create(request):
    if request.method == 'POST':
        sondage = Sondage.objects.create(
            titre=request.POST['titre'],
            user=request.user,
            active_sex_option=request.POST.get('active_sex_option') == 'on'
        )

        # Traitement des tranches d'âge
        for key, value in request.POST.items():
            if key.startswith('tranche_age_debut_'):
                index = key.split('_')[-1]
                debut = int(value)
                fin = int(request.POST[f'tranche_age_fin_{index}'])
                Tranche_age.objects.create(sondage=sondage, debut=debut, fin=fin)

        # Traitement des questions
        for key, value in request.POST.items():
            if key.startswith('question_'):
                Question.objects.create(sondage=sondage, question=value)

        return redirect('sondage_list')

    return render(request, 'sondage_create.html')

# Réponse au sondage
def reponse(request, sondage_id):
    sondage = get_object_or_404(Sondage, id=sondage_id)

    if request.method == 'POST':
        sex = request.POST.get('sex', None)
        tranche_age_id = request.POST.get('tranche_age', None)
        tranche_age = Tranche_age.objects.get(id=tranche_age_id) if tranche_age_id else None

        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                question = Question.objects.get(id=question_id)
                Reponse.objects.create(
                    question=question,
                    reponse=value,
                    sex=sex,
                    tranche_age=tranche_age
                )

        return redirect('sondage_list')

    return render(request, 'reponse.html', {'sondage': sondage})

# Analyse des réponses au sondage
@login_required
def sondage_analyse(request, sondage_id):
    sondage = get_object_or_404(Sondage, id=sondage_id)
    reponses = Reponse.objects.filter(question__sondage=sondage)

    # Appliquer les filtres
    if request.GET:
        if 'sex' in request.GET and request.GET['sex'] and sondage.active_sex_option:
            reponses = reponses.filter(sex=request.GET['sex'])

        if 'tranche_age' in request.GET and request.GET['tranche_age']:
            tranche_age = get_object_or_404(Tranche_age, id=request.GET['tranche_age'])
            reponses = reponses.filter(tranche_age=tranche_age)

        if 'question' in request.GET and request.GET['question']:
            reponses = reponses.filter(question_id=request.GET['question'])

    positif, negatif = 0, 0
    liste_positif, liste_negatif = [], []

    # Analyse des réponses avec BERT
    for rep in reponses:
        inputs = tokenizer(rep.reponse, padding="max_length", max_length=512, truncation=True, return_tensors="pt")
        with torch.no_grad():
            output = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        _, pred = output.max(1)
        if pred.item() == 0:
            positif += 1
            liste_positif.append(rep.reponse)
        else:
            negatif += 1
            liste_negatif.append(rep.reponse)

    context = {
        'sondage': sondage,
        'liste_positif': liste_positif,
        'liste_negatif': liste_negatif,
        'positif': positif,
        'negatif': negatif,
    }
    return render(request, 'sondage_analyse.html', context)

# Suppression du sondage
@login_required
def sondage_delete(request, sondage_id):
    sondage = get_object_or_404(Sondage, id=sondage_id)
    sondage.delete()
    return redirect('sondage_list')
