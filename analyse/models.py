# bert_app/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Sondage(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=200)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sondages')
    active_sex_option=models.BooleanField(default=0)

    def __str__(self):
        return f"{self.titre} - {self.user.username}"
    
class Tranche_age(models.Model):
    id=models.AutoField(primary_key=True)
    sondage=models.ForeignKey(Sondage, on_delete=models.CASCADE, related_name='tranche_age')
    debut=models.IntegerField()
    fin=models.IntegerField()
    
    def __str__(self):
        return f"{self.debut} - {self.fin}"
    
class Categorie(models.Model):
    id=models.AutoField(primary_key=True)
    sondage=models.ForeignKey(Sondage, on_delete=models.CASCADE, related_name='sondage_categorie')
    titre=models.CharField(max_length=200)

    def __str__(self):
        return self.titre
    
class Categorie_option(models.Model):
    id=models.AutoField(primary_key=True)
    categorie=models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='categorie_option')
    option=models.CharField(max_length=200)

    def __str__(self):
        return self.option
    
    
class Question(models.Model):
    id=models.AutoField(primary_key=True)
    sondage=models.ForeignKey(Sondage, on_delete=models.CASCADE, related_name='sondage_question')
    question = models.TextField()
    
    def __str__(self):
        return self.question

class Reponse(models.Model):
    Sex = (
        (1, 'Masculin'),
        (2, 'Feminin'),
    )
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reponses')
    reponse = models.TextField()
    sex = models.IntegerField(choices=Sex, blank=True, null=True)
    tranche_age = models.ForeignKey(Tranche_age, on_delete=models.CASCADE, related_name='reponses', blank=True, null=True)

    def __str__(self):
        return f"Réponse à {self.question.sondage.titre}"