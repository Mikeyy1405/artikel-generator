# 🚀 Writgo Academy Content Generator v12

**De meest geavanceerde AI content generator met GPT-5 ondersteuning**

## ✨ Nieuwe Features in v12

### 🤖 GPT-5 & GPT-4.1 Modellen
Nu met volledige ondersteuning voor de nieuwste AI modellen:

**GPT-5 Serie** (Nieuwste generatie)
- ✅ GPT-5 - Beste voor programmeren & agenten
- ✅ GPT-5 Mini - Snel & kosteneffectief
- ✅ GPT-5 Nano - Zeer snel & goedkoop
- ✅ GPT-5 Chat Latest - Laatste chat optimalisatie
- ✅ GPT-5 Codex - Gespecialiseerd in code
- ✅ GPT-5 Pro - Hoogste kwaliteit (premium)

**GPT-4.1 Serie** (Verbeterde versie)
- ✅ GPT-4.1 - Nieuw, verbeterd model
- ✅ GPT-4.1 Mini - Snelle variant
- ✅ GPT-4.1 Nano - Goedkope variant

**Legacy Modellen** (Nog steeds beschikbaar)
- GPT-4o, GPT-4 Turbo, GPT-4, GPT-3.5 Turbo

---

## 📋 Alle Features

### 🎯 Content Generatie
1. **Linkbuilding Writer**
   - Genereer SEO-geoptimaliseerde artikelen
   - 2 anchor texts met URLs
   - Automatische keyword integratie
   - Forbidden words filter

2. **General AI Writer**
   - Vrije content generatie
   - Instelbaar aantal woorden (100-3000)
   - Flexibele onderwerpen
   - Direct WordPress publicatie

### 🌐 WordPress Integratie
- Multi-site management
- Application password authenticatie
- Direct publiceren vanuit de app
- Post preview & editing
- Internal & affiliate links per site

### 🖼️ Image Generatie
- **Pixabay API**: Gratis stock foto's
- **DALL-E 3**: AI-gegenereerde afbeeldingen
- Automatische image insertion in artikelen

### 📊 Content Management
- Artikel opslag in SQLite database
- Bewerk en update opgeslagen artikelen
- Export naar HTML/TXT
- Originality.ai score checking

### 🎨 Writgo Academy Branding
- Custom color scheme
- Professional sidebar navigatie
- Responsive design
- Modern UI/UX

---

## 🚀 Snelstart Gids

### 1. Installatie

```bash
# Clone of download de bestanden
cd writgo_app_v12

# Installeer dependencies
pip install -r requirements.txt
```

### 2. Configuratie

Maak een `.env` bestand aan:

```env
OPENAI_API_KEY=sk-proj-jouw-api-key-hier
ORIGINALITY_API_KEY=jouw-originality-key
PIXABAY_API_KEY=jouw-pixabay-key
```

### 3. Start de App

```bash
python app.py
```

Open je browser: `http://localhost:5000`

---

## 💰 Model Kosten Overzicht

### GPT-5 Prijzen (per 1M tokens)
| Model | Input | Cached | Output | Beste voor |
|-------|-------|--------|--------|------------|
| gpt-5 | $1.25 | $0.125 | $10.00 | Algemeen gebruik |
| gpt-5-mini | $0.25 | $0.025 | $2.00 | Bulk content |
| gpt-5-nano | $0.05 | $0.005 | $0.40 | Snelle drafts |
| gpt-5-pro | $15.00 | - | $120.00 | Premium content |

### GPT-4.1 Prijzen (per 1M tokens)
| Model | Input | Cached | Output | Beste voor |
|-------|-------|--------|--------|------------|
| gpt-4.1 | $2.00 | $0.50 | $8.00 | Kwaliteit content |
| gpt-4.1-mini | $0.40 | $0.10 | $1.60 | Snelle content |
| gpt-4.1-nano | $0.10 | $0.025 | $0.40 | Budget content |

---

## 🎯 Model Selectie Gids

### Voor Linkbuilding Artikelen
- **Hoogste kwaliteit**: GPT-5 of GPT-5 Pro
- **Beste prijs/kwaliteit**: GPT-5 Mini of GPT-4.1
- **Budget optie**: GPT-5 Nano of GPT-4.1 Nano

### Voor General Content
- **Creatieve content**: GPT-5 of GPT-5 Chat Latest
- **Technische content**: GPT-5 Codex
- **Bulk productie**: GPT-5 Mini
- **Snelle drafts**: GPT-5 Nano

### Voor WordPress Publicatie
- **Direct publiceren**: GPT-5 Mini (snelheid + kwaliteit)
- **Premium posts**: GPT-5 Pro
- **Dagelijkse updates**: GPT-5 Nano (kosteneffectief)

---

## 📦 Deployment op Render.com

### Stap 1: Repository Setup
1. Upload alle bestanden naar GitHub
2. Zorg dat `requirements.txt` en `runtime.txt` aanwezig zijn

### Stap 2: Render Configuratie
1. Maak een nieuwe Web Service aan
2. Koppel je GitHub repository
3. Configuratie:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3

### Stap 3: Environment Variables
Voeg toe in Render dashboard:
```
OPENAI_API_KEY=sk-proj-...
ORIGINALITY_API_KEY=...
PIXABAY_API_KEY=...
```

### Stap 4: Deploy
- Klik op "Create Web Service"
- Wacht tot deployment compleet is
- Open je app URL

---

## 🔧 Technische Details

### Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: SQLite
- **AI**: OpenAI GPT-5/4.1 API
- **Images**: Pixabay API, DALL-E 3
- **Quality Check**: Originality.ai API

### Bestandsstructuur
```
writgo_app_v12/
├── app.py                 # Main Flask application
├── index.html            # Frontend UI
├── requirements.txt      # Python dependencies
├── runtime.txt          # Python version
├── README.md            # Deze file
├── CHANGELOG.md         # Versie geschiedenis
└── writgo_content.db    # SQLite database (auto-created)
```

### Database Schema
```sql
-- Articles table
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content_html TEXT,
    content_text TEXT,
    article_type TEXT,
    anchor1 TEXT,
    url1 TEXT,
    anchor2 TEXT,
    url2 TEXT,
    word_count INTEGER,
    human_score REAL,
    ai_score REAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- WordPress sites table
CREATE TABLE wordpress_sites (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    url TEXT,
    username TEXT,
    app_password TEXT,
    created_at TIMESTAMP
);

-- Links tables (internal & affiliate)
CREATE TABLE internal_links (
    id INTEGER PRIMARY KEY,
    site_id INTEGER,
    anchor_text TEXT,
    url TEXT,
    FOREIGN KEY (site_id) REFERENCES wordpress_sites(id)
);
```

---

## 🛠️ Troubleshooting

### API Errors
- **401 Unauthorized**: Check je OpenAI API key
- **429 Rate Limit**: Wacht even of upgrade je OpenAI plan
- **Model not found**: Zorg dat je toegang hebt tot GPT-5 modellen

### WordPress Publicatie Problemen
- Controleer of Application Password correct is
- Zorg dat WordPress REST API enabled is
- Check firewall/security plugins

### Image Generatie Issues
- Pixabay: Controleer API key en rate limits
- DALL-E: Zorg voor voldoende OpenAI credits

---

## 📞 Support & Updates

### Changelog
Zie `CHANGELOG.md` voor volledige versie geschiedenis

### Toekomstige Features
- [ ] Bulk artikel generatie
- [ ] Scheduled publishing
- [ ] SEO score analysis
- [ ] Multi-language support
- [ ] Template systeem
- [ ] Analytics dashboard

---

## 📄 Licentie

Proprietary - Writgo Academy © 2025

---

## 🎉 Credits

Ontwikkeld met ❤️ voor Writgo Academy
Powered by OpenAI GPT-5 & GPT-4.1

**Versie**: 12.0
**Laatste Update**: 7 oktober 2025
**Status**: Production Ready ✅
