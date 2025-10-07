# WritgoAI - Render Deployment Guide

## ✅ Wat je al hebt gedaan:
- ✅ Environment variables ingesteld in Render
- ✅ API keys toegevoegd (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

## 🔧 Wat de app nu doet:
De app laadt API keys **automatisch** in deze volgorde:
1. **Eerst**: Environment variables (Render) ✅
2. **Daarna**: Secrets file (lokale development)

## 📋 Checklist voor Render:

### 1. PostgreSQL Database (verplicht voor Render)
- [ ] Maak PostgreSQL database aan in Render
- [ ] Kopieer de **Internal Database URL**
- [ ] Voeg toe als environment variable: `DATABASE_URL`

### 2. Environment Variables (al ingesteld ✅)
Je hebt al deze variables in Render:
```
✅ OPENAI_API_KEY
✅ ANTHROPIC_API_KEY
✅ ORIGINALITY_API_KEY
✅ PIXABAY_API_KEY
✅ PYTHON_VERSION
```

**Voeg nog toe:**
```
DATABASE_URL=<postgresql_internal_url>
SECRET_KEY=<genereer_random_string_bijv_writgoai2025secret>
STRIPE_SECRET_KEY=sk_test_... (of sk_live_...)
STRIPE_PRICE_ID=price_... (€99/maand)
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Stripe Setup (voor betalingen)

#### Product aanmaken:
1. Ga naar https://dashboard.stripe.com/products
2. Klik "Add product"
3. Naam: **WritgoAI Pro**
4. Prijs: **€99/maand** (recurring)
5. Kopieer de **Price ID** → voeg toe als `STRIPE_PRICE_ID`

#### Webhook instellen:
1. Ga naar https://dashboard.stripe.com/webhooks
2. Klik "Add endpoint"
3. URL: `https://jouw-app.onrender.com/api/stripe-webhook`
4. Events selecteren:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Kopieer **Signing secret** → voeg toe als `STRIPE_WEBHOOK_SECRET`

### 4. Render Build Settings

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python app.py
```

### 5. Deploy & Test

Na deployment:
1. Open je Render URL
2. Log in met superadmin:
   - **Email**: info@writgo.nl
   - **Wachtwoord**: Writgo2025!
3. Test artikel generatie
4. Test nieuwe gebruiker registratie
5. Test Stripe checkout (test mode eerst!)

## 🐛 Troubleshooting

### "API key not configured" errors:
✅ **OPGELOST!** De app laadt nu eerst environment variables.
- Check of de keys correct zijn ingesteld in Render Environment
- Herstart de service na het toevoegen van nieuwe variables

### Database errors:
- Check of `DATABASE_URL` correct is ingesteld
- Zorg dat PostgreSQL database running is in Render

### Stripe errors:
- Test eerst in **test mode** (keys beginnen met `sk_test_`)
- Check of webhook URL correct is
- Verifieer dat alle 3 subscription events zijn geselecteerd

## 📦 Bestanden in deze versie:
- `app.py` - Hoofdapplicatie met auth + Stripe + PostgreSQL support
- `index.html` - Frontend met responsive design
- `requirements.txt` - Alle Python dependencies
- `RENDER_SETUP.md` - Deze guide

## 🎉 Features:
- ✅ Authenticatie & gebruikersbeheer
- ✅ Stripe abonnementen (€99/maand)
- ✅ PostgreSQL database support
- ✅ Environment variables voor API keys
- ✅ Superadmin account
- ✅ Mobile responsive design
- ✅ GPT-4, GPT-5, Claude AI support
- ✅ Pixabay & DALL-E afbeeldingen
- ✅ YouTube video integratie
- ✅ WordPress export
