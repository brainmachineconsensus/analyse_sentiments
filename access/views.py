from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from .utils import generate_similar_usernames
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import uuid
from django.http import HttpResponse
from django.urls import reverse


def connectez_vous(request):
    return render (request, 'access/connectez-vous.html')

def home(request):
    return render(request, 'home.html')

def creation_compte(request):
    utilisateurs = User.objects.all()
    context = {'utilisateurs': utilisateurs}
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            username = request.POST.get('username')
            email = profile_form.cleaned_data['email']
            password = user_form.cleaned_data['password']
            confirm_password = profile_form.cleaned_data['confirm_password']
            # Vérification si le nom d'utilisateur existe déjà
            existing_users = User.objects.filter(username=username)
            similar_usernames = User.objects.filter(username__icontains=username).exclude(username=username)[:5]

            if existing_users.exists():
                existing_username_message = "Ce nom existe déjà, veuillez en choisir un autre."
                similar_usernames = generate_similar_usernames(username)
                context.update({
                    'existing_username_message': existing_username_message,
                    'similar_usernames': similar_usernames,
                    'user_form': user_form,
                    'profile_form': profile_form
                })
                return render(request, 'access/creation_compte.html', context)

            if password == confirm_password:
                user = User.objects.create_user(username=username, password=password)
                user.is_active = False  # Compte non activé
                user.save()
                # Création du profil compte
                compte_profile = profile_form.save(commit=False)
                compte_profile.user = user
                compte_profile.save()

                # Envoi du mail de confirmation
                activation_link = f"http://sentiments-analyses-client-651782289864.us-central1.run.app/activate/{compte_profile.activation_token}"

                html_message = render_to_string('access/confirmation_email.html', {'activation_link': activation_link})
                text_message = strip_tags(html_message)
                send_mail(
                    'Confirmation de compte',
                    text_message,  # Corps du message en texte brut
                    settings.EMAIL_HOST_USER,
                    [email],
                    html_message=html_message,  # Corps du message en HTML
                    fail_silently=False,
                )
                login(request, user)
                return redirect('compte_confirmation')
            else:
                return render(request, 'access/creation_compte.html', {'error': 'Les mots de passe ne correspondent pas', 'user_form': user_form, 'profile_form': profile_form})
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'access/creation_compte.html', {'user_form': user_form, 'profile_form': profile_form})

def compte_confirmation(request):
    return render (request, 'access/compte_confirmation.html')

def activate_compte(request, activation_token):
    try:
        profile = Profile.objects.get(activation_token=activation_token, user__is_active=False)
        # Vérifier si le délai de 15 minutes n'est pas dépassé
        delta = timezone.now() - profile.activation_token_created_at
        if delta.total_seconds() < 15 * 60:  # 15 minutes en secondes
            profile.user.is_active = True
            profile.user.save()
            return render(request, 'access/compte_active.html')
        else:
            # Supprimer le compte et le profile associé
            profile.user.delete()
            profile.delete()
            # Retourner un message indiquant que le délai de confirmation a expiré
            return render(request, 'access/activation_link_expired.html')
    except Profile.DoesNotExist:
        return HttpResponse("Requête invalide")

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(username=username, password=password)  # Authentification
        if user is not None:
            login(request, user)  # Connexion de l'utilisateur
            print(f"Utilisateur connecté: {request.user}")  # Débogage

            # Gestion de l'option "Rester connecté"
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 jours
            else:
                request.session.set_expiry(0)  # Expire à la fermeture du navigateur

            return redirect('index')  # Redirection après connexion réussie
        else:
            return render(request, 'access/connexion.html', {'error': 'Identifiants invalides'})

    return render(request, 'access/connexion.html')


def demande_reset_mot_de_passe(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        user = User.objects.filter(username=nom).first()

        if user:
            try:
                profile = Profile.objects.get(user=user, email=email)
            except Profile.DoesNotExist:
                # Gérer le cas où le Profile n'est pas trouvé
                return HttpResponse("Ce profil n'existe pas")

            profile.reset_password_token = str(uuid.uuid4())
            profile.reset_password_token_created_at = timezone.now()
            profile.save()

            reset_link = f"http://sentiments-analyses-client-651782289864.us-central1.run.app/reset_mot_de_passe/{profile.reset_password_token}"
            html_message = render_to_string('access/reset_password_email.html', {'reset_link': reset_link})
            text_message = strip_tags(html_message)

            send_mail(
                'Réinitialisation de mot de passe',
                text_message,  # Corps du message en texte brut
                settings.EMAIL_HOST_USER,
                [email],
                html_message=html_message,  # Corps du message en HTML
                fail_silently=False,
            )
            return render(request, 'access/demande_reset_mot_de_passe_envoyee.html')
        else:
            # Gérer le cas où l'utilisateur n'est pas trouvé
            return HttpResponse("Ce profil n'existe pas")
    return render(request, 'access/demande_reset_mot_de_passe.html')


def reset_mot_de_passe(request, reset_token):
    profile = Profile.objects.get(reset_password_token=reset_token)
    if profile:
        # Vérifier si le token est encore valide (moins de 15 minutes)
        time_difference = timezone.now() - profile.reset_password_token_created_at
        if time_difference.total_seconds() < 900:  # 15 minutes en secondes
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_new_password = request.POST.get('confirm_new_password')
                if new_password == confirm_new_password:
                    user = profile.user
                    user.set_password(new_password)
                    user.save()
                    # Réinitialiser le token pour éviter une utilisation ultérieure
                    profile.reset_password_token = None
                    profile.reset_password_token_created_at = None
                    profile.save()
                    return redirect('connexion')
                else:
                    # Gérer le cas où les mots de passe ne correspondent pas
                    return HttpResponse("Les mots de passes ne sont pas conformes, Veuillez entrer la même valeure dans les deux champs ")
            return render(request, 'access/reset_mot_de_passe.html', {'reset_token': reset_token})
        else:
            # Gérer le cas où le token a expiré
            return HttpResponse("Le delais à expiré")
    else:
        # Gérer le cas où le token n'est pas trouvé
        return HttpResponse("Requête invalide")
    

#Changement de mots de passe
def change_password(request):
    if not request.user.is_authenticated:
        return redirect (reverse('connectez_vous'))
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Garde la session de l'utilisateur active
            return redirect('connexion')  # Redirection vers connexion pour les 
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'access/changer_mot_passe.html', {'form': form})

#Changement de username
def change_username(request):
    if not request.user.is_authenticated:
        return redirect (reverse('connectez_vous'))
    if request.method == 'POST':
        form = CustomUsernameChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['new_username']

            # Vérification si le nom d'utilisateur existe déjà
            existing_users = User.objects.filter(username=new_username)
            similar_usernames = User.objects.filter(username__icontains=new_username).exclude(username=new_username)[:5]

            if existing_users.exists():
                # Si un utilisateur avec le même nom existe déjà
                context = {
                    'form': form,
                    'existing_username_message': "Ce nom existe déjà, veuillez en choisir un autre.",
                    'similar_usernames': similar_usernames,
                }
                return render(request, 'access/change_username.html', context)
            # Mettre à jour le nom d'utilisateur
            request.user.username = new_username
            request.user.save()
            return redirect('connexion')
    else:
        form = CustomUsernameChangeForm(user=request.user)

    return render(request, 'access/change_username.html', {'form': form})

#Suppression de comptes 
def delete_compte(request):
    if not request.user.is_authenticated:
        return redirect (reverse('connectez_vous'))
    if request.method == 'POST':
        password = request.POST.get('password', '')
        # Vérifie si le mot de passe est correct pour l'utilisateur actuel
        user = authenticate(username=request.user.username, password=password)

        if user is not None:
            # Le mot de passe est correct, supprimez le compte
            user.delete()
            logout(request)
            return redirect('connexion')

    return render(request, 'access/suppression_compte.html')