# Writgo Academy v13 - Complete Feature Update

## 🎉 Wat is Nieuw in v13?

### 1. **Vereenvoudigde GPT Model Selectie**
Alleen de beste modellen beschikbaar:
- **GPT-5** - Nieuwste & Beste
- **GPT-4.1** - Verbeterd
- **GPT-4.0** - Stabiel

Alle oude/verouderde modellen zijn verwijderd voor een cleaner interface.

### 2. **Extra Elementen voor Algemene Artikelen** ⭐ NIEUW!

Bij de "Algemene AI Schrijver" kun je nu kiezen uit verschillende extra elementen:

#### 📋 Basis Elementen
- **📊 Tabel** - Voegt automatisch een relevante tabel toe
- **❓ FAQ Sectie** - Genereert 5+ veelgestelde vragen met antwoorden
- **💪 Bold Tekst** - Maakt belangrijke termen automatisch bold
- **📺 YouTube Video** - Voegt een YouTube video suggestie toe

#### 📸 Afbeeldingen
- **Pixabay Afbeeldingen (0-5)**
  - Automatisch gezocht in het Engels
  - Gratis stockfoto's
  - Worden direct in het artikel geplaatst
  - Geen extra kosten

- **AI Gegenereerde Afbeeldingen (0-3)**
  - DALL-E 3 integratie
  - Keuze uit 5 stijlen:
    - Realistische Foto
    - Digitale Kunst
    - Illustratie
    - 3D Render
    - Minimalistisch
  - Kosten: $0.040 per afbeelding

### 3. **Pixabay API Integratie** 🖼️

Volledig geïntegreerde Pixabay API voor gratis stockfoto's:
- 4.5+ miljoen afbeeldingen beschikbaar
- Automatische zoekterm vertaling naar Engels
- Meerdere formaten beschikbaar (640px, 1280px, Full HD)
- Gratis voor commercieel gebruik

## 📋 Volledige Feature Lijst

### Linkbuilding Writer
- ✅ Automatische onderwerp generatie
- ✅ 2 anchor teksten met URLs
- ✅ Forbidden words filter
- ✅ GPT model selectie (5, 4.1, 4.0)
- ✅ Originality.AI check
- ✅ Direct WordPress publicatie

### Algemene AI Schrijver
- ✅ Vrij onderwerp kiezen
- ✅ Instelbaar woordenaantal (100-3000)
- ✅ Extra context toevoegen
- ✅ GPT model selectie (5, 4.1, 4.0)
- ✅ **NIEUW:** Tabel toevoegen
- ✅ **NIEUW:** FAQ sectie
- ✅ **NIEUW:** Bold tekst
- ✅ **NIEUW:** Pixabay afbeeldingen (0-5)
- ✅ **NIEUW:** DALL-E afbeeldingen (0-3)
- ✅ **NIEUW:** YouTube video suggestie
- ✅ Direct WordPress publicatie

### WordPress Integratie
- ✅ Meerdere sites beheren
- ✅ Interne links database
- ✅ Affiliate links database
- ✅ Direct publiceren of concept opslaan
- ✅ Automatische link insertie

### Artikel Beheer
- ✅ Alle artikelen opslaan in database
- ✅ Artikelen bewerken
- ✅ Artikelen verwijderen
- ✅ Zoeken en filteren
- ✅ Export functionaliteit

## 🚀 Installatie & Setup

### 1. Vereiste API Keys

```bash
# .env bestand
OPENAI_API_KEY=sk-proj-...
ORIGINALITY_API_KEY=...
PIXABAY_API_KEY=...  # NIEUW in v13
```

### 2. Pixabay API Key Verkrijgen

1. Ga naar [https://pixabay.com/](https://pixabay.com/)
2. Maak een gratis account aan
3. Ga naar [https://pixabay.com/api/docs/](https://pixabay.com/api/docs/)
4. Kopieer je API key
5. Voeg toe aan `.env` bestand

**Gratis tier:** 5,000 requests per maand

### 3. Lokale Installatie

```bash
cd writgo_app_v13
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:10000`

### 4. Render.com Deployment

1. Push naar GitHub
2. Maak nieuwe Web Service op Render.com
3. Voeg environment variables toe:
   - `OPENAI_API_KEY`
   - `ORIGINALITY_API_KEY`
   - `PIXABAY_API_KEY`
4. Deploy!

## 💡 Gebruik van Extra Elementen

### Voorbeeld 1: Blog Post met Afbeeldingen

```
Onderwerp: "Beste yoga oefeningen voor beginners"
Woorden: 1000
Extra Elementen:
  ✅ FAQ Sectie
  ✅ Bold Tekst
  📸 Pixabay: 3 afbeeldingen
```

**Resultaat:**
- Artikel met 3 relevante yoga afbeeldingen
- FAQ sectie met 5+ vragen
- Belangrijke termen in bold
- Professioneel en compleet

### Voorbeeld 2: Uitgebreide Gids

```
Onderwerp: "Complete gids voor gezond eten"
Woorden: 1500
Extra Elementen:
  ✅ Tabel
  ✅ FAQ Sectie
  ✅ Bold Tekst
  📸 Pixabay: 4 afbeeldingen
  📺 YouTube Video
```

**Resultaat:**
- Voedingswaarden tabel
- 4 relevante food afbeeldingen
- FAQ sectie
- YouTube video suggestie
- Bold belangrijke termen

### Voorbeeld 3: Creatief Artikel met AI Art

```
Onderwerp: "Toekomst van AI in design"
Woorden: 800
Extra Elementen:
  ✅ Bold Tekst
  🎨 DALL-E: 2 afbeeldingen (Digital Art stijl)
  📺 YouTube Video
```

**Resultaat:**
- 2 unieke AI-gegenereerde afbeeldingen
- Futuristische digital art stijl
- YouTube video over AI design
- Bold belangrijke AI termen

## 📊 Kosten Overzicht

### GPT Models (per 1M tokens)

| Model | Input | Output | Beste Voor |
|-------|-------|--------|------------|
| GPT-5 | $2.50 | $10.00 | Beste kwaliteit, complexe taken |
| GPT-4.1 | $2.50 | $10.00 | Verbeterde versie, goed voor alles |
| GPT-4.0 | $2.50 | $10.00 | Stabiel, betrouwbaar |

### Afbeeldingen

| Type | Kosten | Limiet |
|------|--------|--------|
| Pixabay | **GRATIS** | 5,000/maand |
| DALL-E 3 | $0.040/afbeelding | Onbeperkt |

### Voorbeeld Kosten

**Artikel met 3 Pixabay afbeeldingen:**
- GPT-5 (1000 woorden): ~$0.02
- Pixabay (3 afbeeldingen): $0.00
- **Totaal: ~$0.02**

**Artikel met 2 DALL-E afbeeldingen:**
- GPT-5 (1000 woorden): ~$0.02
- DALL-E (2 afbeeldingen): $0.08
- **Totaal: ~$0.10**

## 🔧 Technische Details

### Nieuwe Functies in app.py

```python
def process_article_placeholders(article, onderwerp, elements):
    """
    Verwerkt placeholders in artikel:
    - [IMAGE: description] -> Pixabay afbeelding
    - [AI-IMAGE: description] -> DALL-E afbeelding
    - [YOUTUBE: search term] -> YouTube embed
    """

def search_pixabay_images(query, per_page=10, image_type='photo', orientation='horizontal'):
    """
    Zoekt afbeeldingen op Pixabay
    Returns: List van image objects met URLs
    """

def generate_general_article(onderwerp, word_count=500, extra="", model="gpt-4o", elements=None):
    """
    Genereert artikel met optionele extra elementen
    Elements dict kan bevatten:
    - include_table: bool
    - include_faq: bool
    - include_bold: bool
    - pixabay_images: int
    - dalle_images: int
    - dalle_style: str
    - youtube_video: bool
    """
```

### API Endpoints

**Nieuw in v13:**

```
POST /api/search-images
Body: {
  "query": "yoga exercises",
  "per_page": 10,
  "image_type": "photo",
  "orientation": "horizontal"
}
```

**Updated:**

```
POST /api/generate-general-article
Body: {
  "onderwerp": "...",
  "word_count": 1000,
  "model": "gpt-5",
  "include_table": true,
  "include_faq": true,
  "include_bold": true,
  "pixabay_images": 3,
  "dalle_images": 0,
  "dalle_style": "realistic photo",
  "youtube_video": true
}
```

## 🎯 Best Practices

### Pixabay Afbeeldingen
1. **Gebruik Engelse zoektermen** - AI genereert automatisch Engelse beschrijvingen
2. **Beperk tot 3-5 afbeeldingen** - Meer is niet altijd beter
3. **Kies relevante momenten** - Laat AI beslissen waar afbeeldingen passen

### DALL-E Afbeeldingen
1. **Gebruik spaarzaam** - Kosten lopen snel op
2. **Kies de juiste stijl** - Pas bij je content
3. **Max 2-3 per artikel** - Voor speciale accenten

### Extra Elementen
1. **FAQ is waardevol voor SEO** - Gebruik bij informatieve content
2. **Tabellen voor data** - Vergelijkingen, specificaties, etc.
3. **Bold voor scanability** - Helpt lezers snel belangrijke info vinden

## 📝 Changelog v13

### Added
- ✅ Extra elementen sectie in algemene schrijver
- ✅ Pixabay API integratie
- ✅ DALL-E afbeeldingen met stijl keuze
- ✅ Tabel generatie
- ✅ FAQ sectie generatie
- ✅ Bold tekst automatisering
- ✅ YouTube video suggesties
- ✅ `process_article_placeholders()` functie
- ✅ `search_pixabay_images()` functie
- ✅ Uitgebreide prompt voor extra elementen

### Changed
- ✅ GPT model selectie: alleen 5, 4.1, 4.0
- ✅ `generate_general_article()` met elements parameter
- ✅ `/api/generate-general-article` endpoint uitgebreid
- ✅ Frontend UI met extra elementen controls
- ✅ Verbeterde gebruikerservaring

### Removed
- ❌ Oude GPT modellen (4-turbo, 3.5-turbo, etc.)
- ❌ Onnodige model varianten (mini, nano, codex, etc.)

## 🐛 Troubleshooting

### "Pixabay API key not configured"
**Oplossing:** Voeg `PIXABAY_API_KEY` toe aan environment variables

### Geen afbeeldingen gevonden
**Oplossing:** 
- Controleer of zoekterm in Engels is
- Probeer algemenere termen
- Check Pixabay rate limit (5000/maand)

### DALL-E afbeeldingen niet gegenereerd
**Oplossing:**
- Controleer OpenAI API key
- Verifieer dat je DALL-E 3 toegang hebt
- Check OpenAI account balance

### Artikel te lang met alle elementen
**Oplossing:**
- Verhoog woordenaantal naar 1500-2000
- Of verminder aantal extra elementen

## 📚 Documentatie

- **PIXABAY_SETUP.md** - Uitgebreide Pixabay setup gids
- **README_V13.md** - Dit bestand
- **CHANGELOG_V13.md** - Gedetailleerde wijzigingen

## 🎓 Support

Voor vragen of problemen:
1. Check de troubleshooting sectie
2. Lees PIXABAY_SETUP.md voor Pixabay specifieke vragen
3. Controleer API keys en rate limits

## 🚀 Volgende Stappen

1. ✅ Verkrijg Pixabay API key
2. ✅ Update environment variables
3. ✅ Deploy v13
4. ✅ Test alle nieuwe features
5. ✅ Genereer je eerste artikel met afbeeldingen!

---

**Writgo Academy v13** - Powered by GPT-5, Pixabay & DALL-E 🚀
