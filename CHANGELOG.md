# Changelog - WritgoAI v18

## v18.0.0 - Modern Editor (Oktober 2025)

### 🎉 Grote Veranderingen

#### ✨ Nieuwe Features
- **Quill Rich Text Editor** - Professionele WYSIWYG editor geïntegreerd
- **AI Chat Assistent** - Directe conversatie met AI voor artikel aanpassingen
- **YouTube Embed** - Echte video embeds in plaats van alleen links
- **HTML Formatting** - Alle content in proper HTML, geen markdown meer
- **Modern UI** - Volledig vernieuwde, cleane interface
- **Character Counters** - Real-time feedback voor SEO titel en meta beschrijving

#### 🎥 YouTube Functionaliteit
- Automatische video ID extractie uit YouTube URLs
- Responsive video embeds
- Video wordt automatisch in post geplaatst
- Ondersteuning voor youtube.com en youtu.be URLs

#### 💬 AI Chat Systeem
- Context-aware aanpassingen
- Natuurlijke conversatie met AI
- Directe updates in de editor
- Chat geschiedenis per sectie

#### 📝 Content Types
1. **SEO Schrijver**
   - Keyword optimalisatie
   - SEO titel (max 55 tekens) met counter
   - Meta beschrijving (max 130 tekens) met counter
   - Woordenaantal controle

2. **Perplexity Artikel**
   - Diepgaande research content
   - Feitelijke artikelen

3. **YouTube Post**
   - Embedded video
   - Boeiende post content

4. **Lijst Artikel**
   - Genummerde HTML lijsten
   - Configureerbaar aantal items
   - Woorden per item instelbaar

### ❌ Verwijderd
- AI suggesties systeem (te complex, vervangen door chat)
- Markdown formatting (vervangen door HTML)
- Blauwe headers en underlines
- Oude textarea editors
- Complexe UI elementen

### 🔧 Technische Verbeteringen

#### Frontend
- Quill.js editor integratie
- Modern CSS met CSS variables
- Flexbox layout systeem
- Responsive design verbeteringen
- Character counter functionaliteit
- Real-time input validatie

#### Backend
- YouTube URL parsing functie
- YouTube embed generator
- HTML formatting in AI prompts
- Verbeterde error handling
- API endpoint voor artikel modificatie

#### API Endpoints
```
POST /api/generate-seo-article
POST /api/generate-perplexity-article
POST /api/generate-youtube-post
POST /api/generate-list-article
POST /api/modify-article (NIEUW)
```

### 🎨 UI/UX Verbeteringen
- Clean, moderne interface
- Drie-kolommen layout (input, editor, chat)
- Duidelijke visuele feedback
- Betere kleurenschema's
- Verbeterde typografie
- Smooth transitions en hover effects

### 📱 Responsive Design
- Mobile-first approach
- Sidebar klapt in op kleine schermen
- Chat panel verbergt op tablets
- Touch-friendly interface
- Optimale leesbaarheid op alle devices

### 🐛 Bug Fixes
- Markdown formatting issues opgelost
- Lijst formatting nu proper HTML
- YouTube links nu embedded
- Editor layout problemen opgelost
- Character limit validatie toegevoegd

### 📦 Dependencies
- Flask 2.3.0
- OpenAI 0.27.8
- Quill.js 1.3.6 (CDN)
- Gunicorn 21.2.0

### 🚀 Performance
- Snellere editor loading
- Optimale API response times
- Efficiënte HTML rendering
- Minimale JavaScript overhead

### 📚 Documentatie
- Uitgebreide README.md
- API documentatie
- Gebruiksvoorbeelden
- Troubleshooting guide
- Deployment instructies

---

## Migratie van v17 naar v18

### Breaking Changes
1. **Editor Systeem**
   - Oude textarea vervangen door Quill editor
   - Content wordt nu opgeslagen als HTML in plaats van markdown

2. **API Responses**
   - Alle responses bevatten nu HTML in plaats van markdown
   - YouTube posts bevatten embedded video HTML

3. **UI Layout**
   - Volledig nieuwe layout structuur
   - Drie-kolommen systeem

### Migratie Stappen
1. Backup oude content
2. Installeer nieuwe dependencies
3. Update environment variables
4. Test alle functionaliteiten
5. Deploy nieuwe versie

### Data Migratie
- Oude markdown content kan handmatig geconverteerd worden naar HTML
- YouTube links moeten opnieuw gegenereerd worden voor embeds

---

## Toekomstige Plannen (v19)

### Geplande Features
- [ ] WordPress integratie
- [ ] Bulk artikel generatie
- [ ] Template systeem
- [ ] Afbeelding generatie
- [ ] Multi-taal ondersteuning
- [ ] Export naar verschillende formaten
- [ ] Collaboration features
- [ ] Version history

### Overwogen Verbeteringen
- [ ] Offline mode
- [ ] Custom AI prompts
- [ ] Plagiarism checker
- [ ] SEO score calculator
- [ ] Readability analysis
- [ ] Keyword research tool

---

## Bekende Issues

### Minor Issues
- Chat geschiedenis wordt niet opgeslagen bij refresh
- Editor toolbar kan overlappen op kleine schermen
- YouTube embed preview niet beschikbaar voor private videos

### Workarounds
- Kopieer belangrijke chat berichten naar notities
- Gebruik landscape mode op mobiel voor betere toolbar weergave
- Test met publieke YouTube videos

---

## Credits

**Ontwikkeld door:** WritgoAI Team  
**Release Datum:** Oktober 2025  
**Versie:** 18.0.0  
**Status:** Stable  

**Technologieën:**
- Flask (Python)
- OpenAI GPT-4
- Quill.js
- Modern CSS/JavaScript

---

**Voor support en vragen:** support@writgoai.com
