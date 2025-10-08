# WritgoAI v18 - Modern Editor

## 🎯 Nieuwe Functies

### ✨ Moderne Rich Text Editor
- **Quill Editor** - Professionele WYSIWYG editor
- **Real-time bewerking** - Direct zien wat je typt
- **HTML output** - Geen markdown meer, alleen HTML
- **Clean interface** - Overzichtelijke, moderne layout

### 🎥 YouTube Embed
- **Echte video embed** - YouTube video wordt direct in de post geplaatst
- **Automatische conversie** - Plak gewoon de YouTube URL
- **Responsive** - Werkt op alle schermformaten

### 💬 AI Chat Assistent
- **Directe aanpassingen** - Vraag de AI om specifieke wijzigingen
- **Conversational** - Natuurlijke gesprekken met de AI
- **Context-aware** - AI begrijpt je artikel en past het aan

### 📝 Vier Content Types

1. **SEO Schrijver**
   - Keyword optimalisatie
   - SEO titel (max 55 tekens)
   - Meta beschrijving (max 130 tekens)
   - Woordenaantal controle

2. **Perplexity Artikel**
   - Diepgaande research artikelen
   - Feitelijke, goed onderbouwde content

3. **YouTube Post**
   - Embedded YouTube video
   - Boeiende post content
   - Perfect voor video blogs

4. **Lijst Artikel**
   - Genummerde lijsten
   - Configureerbaar aantal items
   - Woorden per item instelbaar

## 🚀 Installatie

1. **Clone of download het project**
```bash
cd writgoai_v18_modern
```

2. **Installeer dependencies**
```bash
pip install -r requirements.txt
```

3. **Configureer API Keys**
```bash
cp .env.example .env
# Bewerk .env en voeg je API keys toe
```

**Benodigde API Keys:**
- `OPENAI_API_KEY` - Voor GPT models en DALL-E (verplicht)
- `ANTHROPIC_API_KEY` - Voor Claude models (optioneel)
- `ORIGINALITY_API_KEY` - Voor AI detectie scoring (optioneel)
- `PIXABAY_API_KEY` - Voor stock afbeeldingen (optioneel)

**⚠️ Security Best Practices:**
- Bewaar API keys NOOIT in de code
- Gebruik altijd environment variables
- Commit nooit je `.env` bestand naar Git
- Voor Render deployment: voeg keys toe als Environment Variables in de dashboard

4. **Start de applicatie**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📋 Gebruik

### SEO Artikel Genereren
1. Selecteer "SEO Schrijver" in het menu
2. Vul alle velden in:
   - Onderwerp
   - Aantal woorden
   - Hoofd keyword
   - SEO titel (max 55 tekens)
   - Meta beschrijving (max 130 tekens)
3. Klik op "Genereer Artikel"
4. Artikel verschijnt in de editor

### Artikel Aanpassen met AI
1. Typ je vraag in de AI Chat:
   - "Maak de inleiding korter"
   - "Voeg een paragraaf toe over..."
   - "Herschrijf de conclusie"
   - "Maak het informeler"
2. Klik op "Verstuur"
3. AI past het artikel aan

### YouTube Post Maken
1. Selecteer "YouTube Post"
2. Plak de YouTube URL
3. Vul onderwerp en woordenaantal in
4. Klik op "Genereer Post"
5. Video wordt automatisch embedded in de post

### Lijst Artikel Maken
1. Selecteer "Lijst Artikel"
2. Vul onderwerp in (bijv: "10 tips voor...")
3. Kies aantal items
4. Kies woorden per item
5. Klik op "Genereer Lijst"

## 🛠️ Editor Functies

- **📋 Kopieer** - Kopieer HTML naar klembord
- **💾 Download HTML** - Download als HTML bestand
- **🗑️ Wissen** - Maak editor leeg

## 🎨 Features

### HTML Formatting
- Alle content wordt gegenereerd in **proper HTML**
- Geen markdown meer
- Echte HTML lijsten: `<ul>`, `<ol>`, `<li>`
- Proper headings: `<h1>`, `<h2>`, `<h3>`
- Paragrafen: `<p>`

### YouTube Embed
```html
<div class="youtube-embed">
    <iframe src="https://www.youtube.com/embed/VIDEO_ID" 
            frameborder="0" 
            allowfullscreen>
    </iframe>
</div>
```

### Responsive Design
- Werkt op desktop, tablet en mobiel
- Sidebar klapt in op kleine schermen
- Editor past zich aan aan schermgrootte

## 🔧 Technische Details

### Frontend
- **Quill.js** - Rich text editor
- **Vanilla JavaScript** - Geen frameworks
- **Modern CSS** - Flexbox layout
- **Responsive** - Mobile-first design

### Backend
- **Flask** - Python web framework
- **OpenAI GPT-4** - AI content generatie
- **RESTful API** - Clean API endpoints

### API Endpoints

```
POST /api/generate-seo-article
POST /api/generate-perplexity-article
POST /api/generate-youtube-post
POST /api/generate-list-article
POST /api/modify-article
```

## 📦 Deployment

### Render.com
1. Push naar GitHub
2. Maak nieuwe Web Service op Render
3. Voeg environment variable toe: `OPENAI_API_KEY`
4. Deploy!

### Heroku
```bash
heroku create writgoai
heroku config:set OPENAI_API_KEY=your-key
git push heroku main
```

## 🎯 Verbeteringen t.o.v. v17

### ❌ Verwijderd
- AI suggesties systeem (te complex)
- Markdown formatting
- Blauwe headers en underlines
- Complexe UI elementen

### ✅ Toegevoegd
- Modern rich text editor (Quill)
- AI chat voor aanpassingen
- YouTube embed functionaliteit
- Proper HTML lijsten
- Clean, overzichtelijke layout
- Character counters voor SEO velden
- Real-time editing

## 💡 Tips

1. **SEO Optimalisatie**
   - Gebruik het keyword 2-3 keer per 100 woorden
   - Houd SEO titel onder 55 tekens
   - Houd meta beschrijving onder 130 tekens

2. **AI Chat Gebruik**
   - Wees specifiek in je vragen
   - Vraag om één aanpassing tegelijk
   - Test verschillende formuleringen

3. **YouTube Posts**
   - Gebruik korte, pakkende titels
   - Schrijf een nieuwsgierig makende inleiding
   - Plaats video vroeg in de post

4. **Lijst Artikelen**
   - Gebruik duidelijke, beschrijvende titels
   - Houd items ongeveer even lang
   - Voeg een conclusie toe

## 🐛 Troubleshooting

### Editor laadt niet
- Check of Quill CDN bereikbaar is
- Ververs de pagina
- Check browser console voor errors

### API errors
- Controleer OpenAI API key
- Check API rate limits
- Bekijk Flask logs

### YouTube embed werkt niet
- Controleer URL format
- Test met verschillende YouTube URLs
- Check browser console

## 📄 Licentie

Proprietary - WritgoAI

## 👨‍💻 Versie

**v18 - Modern Editor**
- Release datum: Oktober 2025
- Status: Stable
- Python: 3.8+
- Flask: 2.3.0
- OpenAI: 0.27.8

---

**Gemaakt met ❤️ voor moderne content creators**
