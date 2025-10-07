# 📋 Writgo Academy v8 - Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Bestanden Controleren
- [ ] `app.py` - Backend met alle features
- [ ] `index.html` - Frontend met Writgo branding
- [ ] `requirements.txt` - Python dependencies
- [ ] `runtime.txt` - Python versie
- [ ] `README.md` - Volledige documentatie

### 2. API Keys Verzamelen
- [ ] OpenAI API key (`sk-...`)
- [ ] Originality.AI API key (optioneel)

### 3. WordPress Voorbereiden
- [ ] WordPress site(s) klaar
- [ ] Admin toegang beschikbaar
- [ ] Applicatie wachtwoorden aangemaakt

---

## 🚀 Deployment Stappen

### Stap 1: GitHub Repository
```bash
cd writgo_app_v8
git init
git add .
git commit -m "Initial commit - Writgo Academy v8"

# Maak repository op GitHub en push:
git remote add origin https://github.com/JOUW-USERNAME/writgo-academy.git
git branch -M main
git push -u origin main
```

### Stap 2: Render.com Account
- [ ] Account aangemaakt op https://render.com
- [ ] GitHub account gekoppeld
- [ ] Betalingsmethode toegevoegd (indien betaald plan)

### Stap 3: Web Service Aanmaken
1. [ ] Klik "New +" → "Web Service"
2. [ ] Selecteer je GitHub repository
3. [ ] Configuratie invullen:
   - **Name**: `writgo-academy`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free of betaald

### Stap 4: Environment Variables Toevoegen
In Render dashboard, ga naar "Environment":
```
OPENAI_API_KEY=sk-proj-...
ORIGINALITY_API_KEY=...
```

### Stap 5: Deploy
- [ ] Klik "Create Web Service"
- [ ] Wacht op deployment (2-3 minuten)
- [ ] Check logs voor errors
- [ ] Test de app URL

---

## 🧪 Post-Deployment Testing

### Test 1: Linkbuilding Artikel
- [ ] Ga naar "Linkbuilding Artikelen"
- [ ] Vul 2 anchor teksten en URLs in
- [ ] Klik "Genereer Artikel"
- [ ] Controleer of artikel wordt gegenereerd
- [ ] Test "Pas Aan" functie
- [ ] Test "Opslaan" functie

### Test 2: Algemene AI Schrijver
- [ ] Ga naar "Algemene AI Schrijver"
- [ ] Vul een onderwerp in
- [ ] Kies aantal woorden
- [ ] Klik "Genereer Artikel"
- [ ] Controleer of artikel wordt gegenereerd
- [ ] Test "Pas Aan" functie
- [ ] Test "Opslaan" functie

### Test 3: WordPress Integratie
- [ ] Ga naar "WordPress Beheer"
- [ ] Voeg een WordPress site toe
- [ ] Vul site naam, URL, username en app wachtwoord in
- [ ] Klik "Site Toevoegen"
- [ ] Controleer of site verschijnt in lijst

### Test 4: WordPress Publicatie
- [ ] Genereer een artikel (linkbuilding of algemeen)
- [ ] Klik "Publiceer naar WordPress"
- [ ] Selecteer een website
- [ ] Kies status (concept/publiceren)
- [ ] Klik "Publiceer"
- [ ] Controleer in WordPress of artikel is aangemaakt

### Test 5: Interne Links
- [ ] Ga naar "Interne Links"
- [ ] Selecteer een website
- [ ] Voeg een interne link toe
- [ ] Controleer of link verschijnt in lijst
- [ ] Test verwijderen van link

### Test 6: Affiliate Links
- [ ] Ga naar "Affiliate Links"
- [ ] Selecteer een website
- [ ] Voeg een affiliate link toe
- [ ] Controleer of link verschijnt in lijst
- [ ] Test verwijderen van link

### Test 7: Opgeslagen Artikelen
- [ ] Ga naar "Opgeslagen Artikelen"
- [ ] Controleer of opgeslagen artikelen verschijnen
- [ ] Test "Bekijk" functie
- [ ] Test "Verwijder" functie

---

## 🔍 Verboden Zinnen Test

Genereer een artikel en controleer of deze zinnen NIET voorkomen:
- [ ] "voordelen"
- [ ] "voordelen van"
- [ ] "Dat is best een opluchting, toch?"

Als deze zinnen wel voorkomen, is er een probleem met de prompts.

---

## 🎨 Branding Controle

Controleer of de Writgo Academy kleuren correct worden gebruikt:
- [ ] Sidebar heeft donkerblauwe achtergrond (#0C1E43)
- [ ] Logo heeft lichtblauw/diepblauw verloop
- [ ] "ACADEMY" is oranje (#FFA62B)
- [ ] Buttons hebben blauwe/oranje kleuren
- [ ] Hover effecten werken correct

---

## 📱 Responsive Test

Test de app op verschillende schermformaten:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobiel (375x667)

---

## 🔒 Security Checklist

- [ ] API keys zijn NIET in code, alleen in environment variables
- [ ] WordPress wachtwoorden worden veilig opgeslagen
- [ ] HTTPS is actief (automatisch op Render)
- [ ] CORS is correct geconfigureerd

---

## 📊 Performance Check

- [ ] Artikelen genereren binnen 10-15 seconden
- [ ] Originality check werkt correct
- [ ] Database queries zijn snel
- [ ] Geen memory leaks
- [ ] Logs zijn schoon (geen errors)

---

## 🆘 Troubleshooting

### Probleem: Artikel genereert niet
**Oplossing**:
1. Check Render logs voor errors
2. Controleer of OPENAI_API_KEY correct is
3. Test OpenAI API key handmatig

### Probleem: WordPress publicatie faalt
**Oplossing**:
1. Controleer applicatie wachtwoord
2. Zorg dat site URL eindigt met `/`
3. Test WordPress REST API: `https://jouwsite.nl/wp-json/wp/v2/posts`
4. Check WordPress gebruiker heeft publicatie rechten

### Probleem: Database errors
**Oplossing**:
1. Database wordt automatisch aangemaakt
2. Check schrijfrechten op server
3. Herstart de app

### Probleem: Originality check werkt niet
**Oplossing**:
1. Check of ORIGINALITY_API_KEY is ingesteld
2. App werkt ook zonder Originality.AI (scores worden 0)

---

## 🎉 Launch Checklist

Voordat je de app officieel lanceert:
- [ ] Alle tests zijn geslaagd
- [ ] Branding is correct
- [ ] WordPress integratie werkt
- [ ] Verboden zinnen worden gefilterd
- [ ] Performance is goed
- [ ] Security is in orde
- [ ] Documentatie is compleet
- [ ] Backup van database gemaakt

---

## 📞 Support Informatie

### Render.com Support
- Dashboard: https://dashboard.render.com
- Logs: Klik op je service → "Logs" tab
- Environment: Klik op je service → "Environment" tab

### WordPress REST API Test
```bash
curl -X GET "https://jouwsite.nl/wp-json/wp/v2/posts" \
  -u "username:xxxx xxxx xxxx xxxx"
```

### Database Backup
Database bestand: `writgo_content.db`
Download via Render Shell:
```bash
cat writgo_content.db | base64
```

---

## ✅ Deployment Compleet!

Als alle checkboxes zijn aangevinkt, is je Writgo Academy Content Generator klaar voor gebruik! 🚀

**Veel succes met content creëren!**
