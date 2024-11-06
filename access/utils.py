from django.contrib.auth.models import Group
from django.contrib.auth.models import User
def create_fournisseurs_group():
    fournisseurs_group, created = Group.objects.get_or_create(name='fournisseurs')
    return fournisseurs_group


def generate_similar_usernames(username):
    similar_usernames = []
    # Vérifiez la base de données pour les noms similaires existants
    existing_usernames = set(User.objects.values_list('username', flat=True))
    
    # Logique pour générer des noms similaires
    base_username = username.lower().replace(" ", "")  # Utilisation du nom d'utilisateur en minuscules sans espaces

    # Générer des noms similaires jusqu'à Alex9
    for i in range(1, 10):
        similar_name = f"{base_username}{i}"
        if similar_name not in existing_usernames:
            similar_usernames.append(similar_name)
    return similar_usernames