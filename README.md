# 🎨 Writgo Academy Content Generator v8

**Complete content creation platform met WordPress integratie en Writgo Academy branding**

---

## 🆕 Nieuwe Features in v8

### ✅ Verboden Zinnen Uitgebreid
- ❌ "voordelen"
- ❌ "voordelen van"
- ❌ "Dat is best een opluchting, toch?"

### 🎨 Writgo Academy Branding
- Volledige huisstijl met jullie kleuren
- Professionele sidebar navigatie
- Modern en overzichtelijk design

### ✍️ Algemene AI Schrijver
- Schrijf artikelen over elk onderwerp
- Instelbaar aantal woorden (100-2000)
- Geen anchor teksten vereist
- Perfecte menselijke schrijfstijl

### 🌐 WordPress Multi-Site Beheer
- Meerdere WordPress websites toevoegen
- Veilig opslaan van applicatie wachtwoorden
- Direct publiceren naar WordPress (concept of live)
- Schakelen tussen websites

### 🔗 Interne Links per Website
- Beheer interne links per website
- Anchor teksten en URLs opslaan
- Makkelijk hergebruiken in artikelen

### 💰 Affiliate Links per Website
- Beheer affiliate links per website
- Specifieke links per site
- Overzichtelijk beheer

### 📚 Verbeterde Artikel Opslag
- Artikelen opslaan met type (linkbuilding/algemeen)
- Bekijken en verwijderen
- Statistieken per artikel

---

## 🎨 Writgo Academy Kleuren

```css
Donkerblauw achtergrond: #0C1E43
Lichtblauw (WRITGO): #00AEEF
Diepblauw (WRITGO): #004E92
Oranje (ACADEMY): #FFA62B
Donkeroranje (verloop): #E36C1E
Geel/oranje driehoek: #FFB443
Lichtblauw icoon: #0098D8
Donkerblauw icoonrand: #004C91
```

---

## 📋 Features Overzicht

### 1. 🔗 Linkbuilding Artikelen
- Auto topic generatie op basis van anchor teksten
- 500 woorden artikelen
- Subtiele verwerking van anchor teksten
- H1/H2/H3 structuur
- Originality.AI check
- Chat-based refinement

### 2. ✍️ Algemene AI Schrijver
- Vrije onderwerp keuze
- Instelbaar aantal woorden
- Professionele schrijfstijl
- Originality.AI check
- Chat-based refinement

### 3. 📚 Artikel Beheer
- Opslaan van artikelen
- Bekijken en verwijderen
- Type badges (linkbuilding/algemeen)
- Statistieken per artikel

### 4. 🌐 WordPress Beheer
- Meerdere sites toevoegen
- Applicatie wachtwoorden
- Direct publiceren (concept/live)
- Veilige opslag credentials

### 5. 🔗 Interne Links
- Per website beheren
- Anchor teksten opslaan
- URLs beheren
- Makkelijk hergebruiken

### 6. 💰 Affiliate Links
- Per website beheren
- Specifieke links per site
- Overzichtelijk beheer

---

## 🚀 Deployment naar Render.com

### Stap 1: Repository Voorbereiden
```bash
cd writgo_app_v8
git init
git add .
git commit -m "Initial commit - Writgo Academy v8"
```

### Stap 2: GitHub Repository
1. Maak nieuwe repository op GitHub
2. Push code:
```bash
git remote add origin https://github.com/jouw-username/writgo-academy.git
git branch -M main
git push -u origin main
```

### Stap 3: Render.com Setup
1. Ga naar https://render.com
2. Klik "New +" → "Web Service"
3. Connect je GitHub repository
4. Configuratie:
   - **Name**: `writgo-academy`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (of betaald voor betere performance)

### Stap 4: Environment Variables
Voeg toe in Render dashboard:
```
OPENAI_API_KEY=sk-...
ORIGINALITY_API_KEY=...
```

### Stap 5: Deploy
- Klik "Create Web Service"
- Wacht op deployment (2-3 minuten)
- Open je app op: `https://writgo-academy.onrender.com`

---

## 🔧 WordPress Applicatie Wachtwoord Aanmaken

### Stappen:
1. Log in op je WordPress admin
2. Ga naar **Gebruikers** → **Profiel**
3. Scroll naar beneden naar **Applicatie Wachtwoorden**
4. Vul een naam in (bijv: "Writgo Academy")
5. Klik **Nieuw applicatie wachtwoord toevoegen**
6. Kopieer het gegenereerde wachtwoord (formaat: `xxxx xxxx xxxx xxxx`)
7. Gebruik dit wachtwoord in de app

**Let op**: Het wachtwoord wordt maar 1 keer getoond!

---

## 📊 Database Structuur

### Articles Table
```sql
- id (PRIMARY KEY)
- title (TEXT)
- content_html (TEXT)
- content_text (TEXT)
- article_type (TEXT) - 'linkbuilding' of 'general'
- anchor1, url1, anchor2, url2 (TEXT)
- word_count (INTEGER)
- human_score, ai_score (REAL)
- created_at, updated_at (TIMESTAMP)
```

### WordPress Sites Table
```sql
- id (PRIMARY KEY)
- site_name (TEXT UNIQUE)
- site_url (TEXT)
- username (TEXT)
- app_password (TEXT)
- created_at, updated_at (TIMESTAMP)
```

### Internal Links Table
```sql
- id (PRIMARY KEY)
- site_id (FOREIGN KEY)
- anchor_text (TEXT)
- url (TEXT)
- created_at (TIMESTAMP)
```

### Affiliate Links Table
```sql
- id (PRIMARY KEY)
- site_id (FOREIGN KEY)
- anchor_text (TEXT)
- url (TEXT)
- created_at (TIMESTAMP)
```

---

## 🎯 Schrijfregels

### ✅ WEL Doen:
- Gebruik ALTIJD "je" en "jij" (NOOIT "u")
- Korte, pakkende zinnen
- Afwisselende zinslengte
- Directe aanspreking
- Natuurlijke taalfouten
- Concrete voorbeelden
- Professioneel maar toegankelijk

### ❌ NIET Doen:
- NOOIT "u" gebruiken
- NOOIT "voordelen" zeggen
- NOOIT "voordelen van" gebruiken
- NOOIT "Dat is best een opluchting, toch?" gebruiken
- GEEN keywords in headings
- GEEN productnamen in H1
- GEEN AI-clichés
- GEEN marketing-taal

---

## 🔒 Beveiliging

- API keys via environment variables
- WordPress wachtwoorden encrypted in database
- HTTPS verplicht op productie
- CORS configuratie voor veiligheid

---

## 📱 Responsive Design

- Volledig responsive
- Mobiel-vriendelijk
- Tablet-optimized
- Desktop-optimized

---

## 🆘 Troubleshooting

### Artikel genereert niet
- Check of OPENAI_API_KEY correct is ingesteld
- Controleer Render logs voor errors

### WordPress publicatie faalt
- Controleer of applicatie wachtwoord correct is
- Zorg dat site URL eindigt met `/`
- Check WordPress REST API is enabled

### Database errors
- Database wordt automatisch aangemaakt
- Bij problemen: verwijder `writgo_content.db` en herstart

---

## 📞 Support

Voor vragen of problemen:
- Check de logs in Render dashboard
- Controleer environment variables
- Test WordPress credentials handmatig

---

## 🎉 Klaar voor Gebruik!

Je Writgo Academy Content Generator is nu volledig operationeel met:
- ✅ Verboden zinnen filter
- ✅ Writgo Academy branding
- ✅ Algemene AI schrijver
- ✅ WordPress multi-site beheer
- ✅ Interne links per site
- ✅ Affiliate links per site
- ✅ Professionele sidebar navigatie
- ✅ Moderne UI/UX

**Veel succes met content creëren! 🚀**
