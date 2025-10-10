# 🚀 Render Deployment Fix - WritgoAI

## 📋 Probleem Diagnose

### Wat was er mis?

1. **Oude index.html in root directory**
   - Er stond een verouderde `index.html` (3015 regels) in de root
   - Deze bevatte NIET de nieuwe features (Website Beheer, Affiliate Links)
   - Deze file was per ongeluk gecommit in eerdere versies

2. **Correcte template werd overschaduwd**
   - De juiste `templates/index.html` (4647 regels) bevat WEL alle nieuwe features
   - app.py gebruikt correct `send_file('templates/index.html')`
   - Maar de oude file in root kon conflicteren tijdens deployment

3. **Database tabellen ontbraken**
   - De nieuwe tabellen (`website_affiliate_links`, `website_affiliate_feeds`, `feed_products`) werden niet automatisch aangemaakt
   - Dit gebeurt nu automatisch via `AffiliateManager.__init__()` bij eerste start

4. **Website data verdwenen**
   - De `websites` tabel was leeg
   - Dit komt doordat de database op Render mogelijk gereset is
   - Of omdat de data niet persistent was opgeslagen

## ✅ Oplossing Geïmplementeerd

### Commit: e25d3d4
```
🔧 Fix: Remove old index.html files that conflict with templates/index.html

- Removed outdated index.html from root (3015 lines, old UI)
- Removed outdated article_generator_app.html
- The correct template is templates/index.html (4647 lines, new UI)
- This fixes the issue where Render was serving the old UI
- New features now visible: Website Beheer, Affiliate Links, Affiliate Feeds
```

## 🎯 Stappen voor Deployment op Render

### 1. Automatische Deployment (Aanbevolen)

Render detecteert automatisch de nieuwe commit en start een deployment:

1. Ga naar [Render Dashboard](https://dashboard.render.com/)
2. Selecteer je `artikel-generator` service
3. Wacht tot de automatische deployment start (binnen 1-2 minuten)
4. Monitor de deployment logs voor errors

### 2. Handmatige Deployment (Als automatisch niet werkt)

Als de automatische deployment niet start:

1. Ga naar je Render service dashboard
2. Klik op **"Manual Deploy"** → **"Deploy latest commit"**
3. Selecteer de `main` branch
4. Klik op **"Deploy"**

### 3. Database Initialisatie

De database wordt automatisch geïnitialiseerd bij de eerste start:

**Wat gebeurt er automatisch:**
- `app.py` roept `init_db()` aan bij startup
- `AffiliateManager` wordt geïnitialiseerd en maakt nieuwe tabellen aan:
  - `website_affiliate_links`
  - `website_affiliate_feeds`
  - `feed_products`
- Alle bestaande tabellen blijven behouden

**Geen handmatige actie nodig!**

### 4. Verificatie na Deployment

Controleer of de deployment succesvol is:

1. **Check de logs:**
   ```
   ✓ Building...
   ✓ Installing dependencies from requirements.txt
   ✓ Starting gunicorn
   ✓ Application started successfully
   ```

2. **Test de nieuwe UI:**
   - Open je WritgoAI app op Render
   - Klik op **"Website Beheer"** in de sidebar
   - Je zou nu moeten zien:
     - ✅ "Nieuwe Website Toevoegen" knop
     - ✅ Tabs voor "Websites", "Affiliate Links", "Affiliate Feeds"
     - ✅ Moderne, blauwe UI met oranje accenten

3. **Test de functionaliteit:**
   - Voeg een nieuwe website toe
   - Controleer of deze opgeslagen wordt
   - Test het toevoegen van affiliate links

## 🔄 Website Data Herstellen

### Waarom is de website data verdwenen?

De `websites` tabel was leeg omdat:
1. De database op Render mogelijk gereset is tijdens een deployment
2. Of de data was opgeslagen in een tijdelijke database die niet persistent was

### Hoe voeg je je website opnieuw toe?

1. **Ga naar Website Beheer:**
   - Klik op "Website Beheer" in de sidebar
   - Klik op "Nieuwe Website Toevoegen"

2. **Vul de gegevens in:**
   - **Website Naam:** bijv. "Yoga Start Gids"
   - **Website URL:** bijv. "https://yogastartgids.nl"
   - **Sitemap URL:** bijv. "https://yogastartgids.nl/sitemap.xml"

3. **Klik op "Website Toevoegen"**

4. **Verifieer:**
   - De website verschijnt in de lijst
   - Je kunt nu affiliate links toevoegen
   - Je kunt de sitemap refreshen

### Data Persistentie op Render

**Belangrijk:** Render gebruikt een **persistent disk** voor de database:

- De database file `writgo_content.db` wordt opgeslagen op een persistent volume
- Data blijft behouden tussen deployments
- **LET OP:** Bij een "Clear Build Cache" of "Delete Service" gaat data verloren!

**Aanbeveling voor de toekomst:**
- Maak regelmatig backups van de database
- Gebruik een externe database (PostgreSQL) voor productie
- Of implementeer een backup systeem

## 🐛 Troubleshooting

### Probleem: Oude UI blijft zichtbaar

**Oplossing:**
1. Hard refresh in browser: `Ctrl + Shift + R` (Windows) of `Cmd + Shift + R` (Mac)
2. Clear browser cache
3. Open in incognito/private mode

### Probleem: "Table does not exist" errors

**Oplossing:**
1. Check Render logs voor database initialisatie errors
2. Trigger een nieuwe deployment (Manual Deploy)
3. De tabellen worden automatisch aangemaakt bij startup

### Probleem: Website toevoegen werkt niet

**Oplossing:**
1. Check browser console voor JavaScript errors (F12)
2. Verifieer dat de API endpoints werken:
   - `GET /api/websites` - Lijst van websites
   - `POST /api/websites` - Nieuwe website toevoegen
3. Check Render logs voor Python errors

### Probleem: Affiliate links niet zichtbaar

**Oplossing:**
1. Zorg dat je eerst een website hebt toegevoegd
2. Selecteer de website in de dropdown
3. De affiliate links sectie wordt dan zichtbaar

## 📊 Nieuwe Features Overzicht

### 1. Website Beheer
- ✅ Meerdere websites beheren
- ✅ Sitemap URL opslaan en refreshen
- ✅ Website-specifieke instellingen
- ✅ User-based filtering (elke user ziet alleen eigen websites)

### 2. Affiliate Links Management
- ✅ Affiliate links per website
- ✅ Anchor text en URL opslaan
- ✅ Categorieën en prioriteiten
- ✅ Active/inactive status
- ✅ Automatisch invoegen in content

### 3. Affiliate Feeds
- ✅ Product feeds importeren (XML/CSV)
- ✅ Automatische product cache
- ✅ Update frequentie instellen
- ✅ Feed status monitoring

### 4. Verbeterde Content Planning
- ✅ Automatische blog generator
- ✅ Kalender view
- ✅ Editorial management
- ✅ Content scheduling

## 🎉 Verwachte Resultaat

Na succesvolle deployment zie je:

```
┌─────────────────────────────────────────┐
│  WritgoAI - Content Generator v22      │
├─────────────────────────────────────────┤
│  📊 Dashboard                           │
│  🌐 Website Beheer          ← NIEUW!   │
│  🔍 Zoekwoordonderzoek                  │
│  📅 Contentplanning                     │
│  ✍️  Content Schrijver                  │
│  🖼️  Afbeeldingen & Media               │
│  📝 WordPress Publicatie                │
│  📱 Social Media                        │
│  📁 Opgeslagen Artikelen                │
│  👤 Mijn Account                        │
│  🚪 Uitloggen                           │
└─────────────────────────────────────────┘
```

En in Website Beheer:

```
┌─────────────────────────────────────────┐
│  🌐 Website Beheer                      │
├─────────────────────────────────────────┤
│  [+ Nieuwe Website Toevoegen]           │
│                                         │
│  Tabs:                                  │
│  • Websites                             │
│  • 🔗 Affiliate Links      ← NIEUW!    │
│  • 📡 Affiliate Feeds      ← NIEUW!    │
└─────────────────────────────────────────┘
```

## 📞 Support

Als je problemen ondervindt:

1. Check de Render deployment logs
2. Check browser console (F12) voor JavaScript errors
3. Verifieer dat alle environment variables correct zijn ingesteld
4. Test de API endpoints met de browser developer tools

## ✨ Volgende Stappen

1. ✅ Deploy de fix naar Render
2. ✅ Verifieer dat de nieuwe UI zichtbaar is
3. ✅ Voeg je website opnieuw toe
4. ✅ Test de affiliate links functionaliteit
5. 🎯 Begin met het toevoegen van affiliate links en feeds!

---

**Laatste update:** 10 oktober 2025
**Commit:** e25d3d4
**Status:** ✅ Fix geïmplementeerd en gepushed naar GitHub
