# Définir l'image de base
FROM python:3.11.2

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requis dans le conteneur
COPY requirements.txt .
# Installer les dépendances
RUN pip install -r requirements.txt

# Copier le reste de l'application dans le conteneur
COPY . .

# Exposer le port 8000
EXPOSE 8000

# Définir la commande pour exécuter l'application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
