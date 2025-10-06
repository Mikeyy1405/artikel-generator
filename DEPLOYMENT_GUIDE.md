# 🚀 DEPLOYMENT GUIDE - RENDER.COM

## Snelle Start (5 minuten)

### 1️⃣ GITHUB REPOSITORY MAKEN

```bash
# Optie A: Via GitHub website
1. Ga naar https://github.com/new
2. Repository naam: artikel-generator
3. Maak repository (public of private)
4. Upload alle bestanden uit /home/ubuntu/render_deploy/

# Optie B: Via command line (als je git hebt)
cd /home/ubuntu/render_deploy
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/JOUW-USERNAME/artikel-generator.git
git push -u origin main
```

### 2️⃣ RENDER.COM ACCOUNT

1. Ga naar: https://render.com
2. Klik op "Get Started for Free"
3. Sign up met GitHub account (makkelijkst)
4. Verify je email

### 3️⃣ WEB SERVICE AANMAKEN

1. In Render dashboard, klik "New +" (rechtsboven)
2. Selecteer "Web Service"
3. Connect je GitHub repository
4. Klik "Connect" bij je artikel-generator repo

### 4️⃣ CONFIGURATIE

Vul in:

**Basic Settings:**
- Name: `artikel-generator` (of eigen naam)
- Region: `Frankfurt (EU Central)` (dichtbij Nederland)
- Branch: `main`
- Root Directory: (leeg laten)
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

**Instance Type:**
- Selecteer: `Free` (€0/maand, 750 uur)

### 5️⃣ ENVIRONMENT VARIABLES

Scroll naar beneden naar "Environment Variables"

Klik "Add Environment Variable" en voeg toe:

```
Key: OPENAI_API_KEY
Value: sk-proj-... (jouw OpenAI key)

Key: ORIGINALITY_API_KEY
Value: ... (jouw Originality.AI key)
```

⚠️ **BELANGRIJK**: Zonder deze keys werkt de app niet!

### 6️⃣ DEPLOY

1. Klik "Create Web Service" (onderaan)
2. Wacht 2-3 minuten terwijl Render de app bouwt
3. Je ziet logs verschijnen
4. Wanneer je ziet: "Your service is live 🎉"
5. Klik op de URL bovenaan (bijv. `https://artikel-generator.onrender.com`)

### 7️⃣ KLAAR! 🎉

Je app is nu live en bereikbaar via je eigen URL!

---

## 📋 CHECKLIST

- [ ] GitHub repository gemaakt
- [ ] Alle bestanden geüpload
- [ ] Render.com account aangemaakt
- [ ] Web Service aangemaakt
- [ ] Environment variables toegevoegd
- [ ] Deployment succesvol
- [ ] App getest en werkt

---

## 🔧 TROUBLESHOOTING

### "Build failed"
- Check of requirements.txt correct is
- Kijk in de logs welke package faalt
- Mogelijk Python versie issue

### "Application Error"
- Check of environment variables correct zijn
- Kijk in de logs (Logs tab in Render)
- Mogelijk API key issue

### "App is slow"
- Free tier gaat in sleep mode na 15 min inactiviteit
- Eerste request duurt 30-60 seconden (cold start)
- Daarna normaal snel

### App werkt niet
1. Check logs in Render dashboard
2. Verify environment variables
3. Test API keys lokaal eerst

---

## 💡 TIPS

### Custom Domain
1. Koop een domein (bijv. bij TransIP)
2. In Render: Settings → Custom Domain
3. Voeg je domein toe
4. Update DNS records bij je provider

### Auto-Deploy
- Elke push naar GitHub = automatische deploy
- Handig voor updates

### Monitoring
- Render dashboard toont:
  - CPU/Memory gebruik
  - Request logs
  - Error logs
  - Deployment history

### Upgraden naar Paid
- $7/maand voor altijd-aan instance
- Geen cold starts
- Meer resources
- Betere performance

---

## 📞 HULP NODIG?

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Of vraag mij!

