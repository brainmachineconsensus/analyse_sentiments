# Étape 1 : Builder - Installation des dépendances
FROM python:3.10-slim AS builder

WORKDIR /app

# Installer pip et les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 2 : Image finale
FROM python:3.10-slim

WORKDIR /app

# Copier uniquement les dépendances
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copier le code de l’application
COPY . /app

# Exposer le port 8080 (pour Cloud Run)
EXPOSE 8080
ENV PORT=8080

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "--timeout", "120", "analyse_sentiments.wsgi:application"]