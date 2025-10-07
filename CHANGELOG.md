# 📝 Changelog - Writgo Academy Content Generator

## Version 14 (7 oktober 2025)

### 🌟 Grote Nieuwe Features

#### 🏆 Best of All Mode
- **Revolutionaire combinatie van 3 AI modellen in één artikel!**
- Gebruikt GPT-4.1 voor structuur & SEO
- Gebruikt Claude Sonnet 4 voor natuurlijk schrijven
- Gebruikt Claude Opus 4 voor creativiteit & diepgang
- Combineert automatisch de beste elementen van alle drie
- Ultieme kwaliteit voor professionele content

#### 🟣 Claude AI Modellen Ondersteuning
- **Claude Sonnet 4** ⭐ - Beste voor natuurlijk, menselijk schrijven
- **Claude Opus 4** - Meest creatief & diepgaand
- **Claude Sonnet 3.7** - Uitstekende balans
- **Claude Sonnet 3.5** - Snelle variant
- Volledige integratie met Anthropic API
- Betere schrijfstijl dan GPT voor content

#### 📱 Mobile Responsive Design
- **Volledig geoptimaliseerd voor mobiele apparaten**
- Hamburger menu (☰) voor sidebar navigatie
- Sidebar schuift automatisch weg op mobiel
- Touch-friendly interface
- Geen meer geknepen invulvelden
- Overlay voor betere UX
- Font-size optimalisatie (voorkomt zoom op iOS)
- Responsive grid layouts voor alle secties

### 🔧 Technische Verbeteringen

#### API Integratie
- Anthropic API client toegevoegd
- Model mapping voor Claude modellen
- Fallback mechanisme bij API failures
- Error handling voor beide API's

#### Code Optimalisaties
- `call_claude_api()` functie voor Claude calls
- `generate_with_best_of_all()` voor multi-model generatie
- Verbeterde model detectie (GPT vs Claude)
- Unified prompt system voor beide platforms

#### UI/UX Verbeteringen
- Gegroepeerde model selectie met optgroups
- Duidelijke labels: "🔵 OpenAI GPT" en "🟣 Anthropic Claude"
- "🌟 Best of All" als premium optie
- Mobile-first CSS met @media queries
- Fixed positioning voor mobile menu button
- Smooth transitions en animaties

### 📦 Dependencies
- `anthropic==0.39.0` toegevoegd aan requirements.txt
- Backwards compatible met bestaande OpenAI setup

### 📚 Documentatie
- README.md volledig geüpdatet met v14 features
- Uitleg over "Best of All" mode
- Claude modellen documentatie
- Mobile usage instructies
- API key configuratie voor beide platforms

---

## Version 13 (eerder)

### Features
- Extra elementen: tabellen, FAQ, bold text
- Pixabay afbeeldingen integratie
- DALL-E 3 AI afbeeldingen
- YouTube video placeholders
- Verbeterde placeholder processing
- Model selectie beperkt tot GPT-5, GPT-4.1, GPT-4.0

---

## Version 12 (eerder)

### Features
- GPT-5 modellen ondersteuning
- GPT-4.1 modellen ondersteuning
- Verbeterde model selectie
- Performance optimalisaties

---

## Version 11 en eerder

### Core Features
- Linkbuilding artikel generator
- Algemene AI schrijver
- WordPress multi-site beheer
- Afbeeldingen generatie (Pixabay + DALL-E)
- Opgeslagen artikelen database
- Originality.AI score checking
- Forbidden words filter
- HTML/TXT export
- Internal & affiliate links management

---

## 🚀 Upgrade Instructies

### Van v13 naar v14:

1. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Voeg Anthropic API key toe aan .env:**
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-jouw-key-hier
   ```

3. **Vervang bestanden:**
   - `app.py` - Nieuwe versie met Claude support
   - `index.html` - Nieuwe versie met mobile responsive design
   - `requirements.txt` - Inclusief anthropic library

4. **Herstart de app:**
   ```bash
   python app.py
   ```

5. **Test op mobiel:**
   - Open op je smartphone
   - Klik op hamburger menu (☰)
   - Test alle functies

### Optioneel:
- Als je alleen GPT wilt gebruiken: Anthropic API key is niet verplicht
- Voor "Best of All" mode: Beide API keys zijn vereist
- Mobile design werkt automatisch zonder extra configuratie

---

## 🐛 Bug Fixes in v14

- ✅ Mobile sidebar overlapping content - OPGELOST
- ✅ Input fields te klein op mobiel - OPGELOST
- ✅ Menu niet toegankelijk op kleine schermen - OPGELOST
- ✅ iOS zoom bij input focus - OPGELOST
- ✅ Touch targets te klein - OPGELOST

---

## 📊 Performance

### Best of All Mode
- Genereert 3 artikelen parallel (waar mogelijk)
- Combineert in ~30-60 seconden
- Hoogste kwaliteit output

### Individuele Modellen
- GPT modellen: ~10-20 seconden
- Claude modellen: ~10-20 seconden
- Afhankelijk van artikel lengte

### Mobile Performance
- Snelle laadtijd op mobiel
- Smooth animaties (60fps)
- Geoptimaliseerde CSS
- Geen onnodige JavaScript

---

## 🔮 Toekomstige Features (Roadmap)

- [ ] Gemini AI modellen ondersteuning
- [ ] Bulk artikel generatie
- [ ] Template systeem
- [ ] A/B testing voor modellen
- [ ] Analytics dashboard
- [ ] API endpoint voor externe integraties
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Voice input voor mobiel
- [ ] PWA (Progressive Web App) support

---

## 💡 Tips & Tricks

### Best of All Mode
- Gebruik voor belangrijke, high-value content
- Beste resultaten bij 500-1000 woorden
- Combineert SEO + creativiteit + natuurlijkheid

### Claude vs GPT
- **Claude**: Beter voor blogs, verhalen, natuurlijke content
- **GPT**: Beter voor technische content, lijsten, structured data
- **Best of All**: Beste van beide werelden

### Mobile Usage
- Gebruik landscape mode voor meer ruimte
- Hamburger menu sluit automatisch na selectie
- Swipe van links om menu te openen (toekomstige feature)

---

**Gemaakt met ❤️ door Writgo Academy Team**
