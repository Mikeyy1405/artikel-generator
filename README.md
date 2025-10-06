# Linkbuilding Artikel Generator

Een professionele artikel generator voor zakelijke lease content met SEO optimalisatie.

## Features

- 🤖 GPT-4o powered artikel generatie
- 💬 Chat functie voor aanpassingen
- 🔗 Automatische anchor link verwerking
- 📊 Originality.AI integratie
- ✍️ Natuurlijke schrijfstijl met "je" en "jij"
- 🎯 SEO-geoptimaliseerde content

## Deployment op Render.com

### Stap 1: GitHub Repository
1. Maak een nieuwe GitHub repository
2. Upload alle bestanden uit deze folder
3. Push naar GitHub

### Stap 2: Render.com Setup
1. Ga naar https://render.com
2. Maak een account (gratis)
3. Klik op "New +" → "Web Service"
4. Connect je GitHub repository
5. Configureer:
   - **Name**: artikel-generator (of eigen naam)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Stap 3: Environment Variables
Voeg deze environment variables toe in Render.com:

```
OPENAI_API_KEY=sk-proj-...
ORIGINALITY_API_KEY=...
```

### Stap 4: Deploy
1. Klik op "Create Web Service"
2. Wacht tot deployment klaar is (2-3 minuten)
3. Je app is live op: `https://jouw-app-naam.onrender.com`

## Lokaal Draaien

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-proj-...
export ORIGINALITY_API_KEY=...
python app.py
```

Open: http://localhost:5000

## Technische Details

- **Framework**: Flask
- **AI Model**: GPT-4o
- **Originality Check**: Originality.AI
- **Frontend**: Vanilla JavaScript
- **Deployment**: Gunicorn WSGI server

## Support

Voor vragen of problemen, neem contact op.
