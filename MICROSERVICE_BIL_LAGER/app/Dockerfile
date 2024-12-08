# Brug en letvægts Python-basisimage
FROM python:3.10-slim

# Angiv arbejdsmappen i containeren
WORKDIR /app

# Kopiér alle filer fra dit projekt til containerens arbejdsmappe
COPY . .

# Installer afhængigheder fra requirements.txt (opret den, hvis du ikke allerede har)
RUN pip install Flask

# Eksponer porten, som Flask kører på
EXPOSE 5000

# Kommando til at køre Flask-serveren
CMD ["python", "app.py"]