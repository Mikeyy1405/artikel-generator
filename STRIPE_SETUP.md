# Stripe Payment Setup Guide

## Overzicht
Dit project gebruikt Stripe voor abonnementsbetalingen. Gebruikers moeten €99/maand betalen om toegang te krijgen tot het platform.

## Vereiste Stripe Keys

Je hebt de volgende environment variables nodig:

```bash
STRIPE_SECRET_KEY=sk_test_... of sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_test_... of pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Setup Stappen

### 1. Stripe Account Aanmaken
1. Ga naar https://stripe.com
2. Maak een account aan of log in
3. Ga naar Dashboard

### 2. API Keys Ophalen
1. Ga naar **Developers** → **API keys**
2. Kopieer de **Publishable key** (begint met `pk_`)
3. Kopieer de **Secret key** (begint met `sk_`)
4. Voeg deze toe aan je environment variables op Render

### 3. Product Configureren
Het product ID is al geconfigureerd: `prod_TBxZgD1ASfSHPc`

Als je een nieuw product wilt maken:
1. Ga naar **Products** in Stripe Dashboard
2. Klik op **Add product**
3. Naam: "WritgoAI Premium"
4. Prijs: €99.00 EUR
5. Recurring: Monthly
6. Kopieer het Product ID en update in `app.py`

### 4. Webhook Configureren
1. Ga naar **Developers** → **Webhooks**
2. Klik op **Add endpoint**
3. Endpoint URL: `https://jouw-domain.com/api/stripe/webhook`
4. Selecteer de volgende events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Kopieer de **Signing secret** (begint met `whsec_`)
6. Voeg deze toe als `STRIPE_WEBHOOK_SECRET` environment variable

### 5. Environment Variables op Render
1. Ga naar je Render dashboard
2. Selecteer je web service
3. Ga naar **Environment**
4. Voeg toe:
   ```
   STRIPE_SECRET_KEY=sk_...
   STRIPE_PUBLISHABLE_KEY=pk_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
5. Klik op **Save Changes**

### 6. Database Migratie
De database wordt automatisch gemigreerd bij de eerste start. De volgende velden worden toegevoegd aan de `users` tabel:
- `stripe_customer_id`
- `stripe_subscription_id`
- `subscription_status`
- `subscription_start_date`
- `subscription_end_date`

## Test Mode vs Live Mode

### Test Mode (Development)
- Gebruik test keys (beginnen met `sk_test_` en `pk_test_`)
- Test credit card: `4242 4242 4242 4242`
- Elke toekomstige datum voor expiry
- Elke 3-cijferige CVC
- Elke postcode

### Live Mode (Production)
- Gebruik live keys (beginnen met `sk_live_` en `pk_live_`)
- Echte betalingen worden verwerkt
- Zorg dat je bedrijfsgegevens compleet zijn in Stripe

## Payment Flow

1. **Registratie**: Gebruiker maakt account aan
2. **Redirect**: Automatisch doorgestuurd naar `/payment`
3. **Checkout**: Stripe Checkout sessie wordt aangemaakt
4. **Betaling**: Gebruiker betaalt via Stripe (iDEAL of creditcard)
5. **Webhook**: Stripe stuurt webhook naar `/api/stripe/webhook`
6. **Activatie**: Subscription status wordt op 'active' gezet
7. **Success**: Gebruiker wordt doorgestuurd naar dashboard

## Login Flow

1. **Login Poging**: Gebruiker probeert in te loggen
2. **Check Subscription**: Systeem checkt `subscription_status`
3. **Actief**: Als status = 'active' → toegang tot dashboard
4. **Inactief**: Als status = 'inactive' → redirect naar `/payment`
5. **Superuser**: Superusers hebben altijd toegang (bypass payment)

## Subscription Statussen

- `inactive`: Geen actief abonnement (default bij registratie)
- `active`: Actief betaald abonnement
- `past_due`: Betaling mislukt, grace period
- `cancelled`: Abonnement opgezegd
- `trialing`: In trial periode (optioneel)

## Troubleshooting

### Webhook niet ontvangen
- Check of de webhook URL correct is
- Controleer of de signing secret klopt
- Bekijk webhook logs in Stripe Dashboard

### Betaling succesvol maar geen toegang
- Check de webhook logs
- Controleer of `subscription_status` is geupdate in database
- Bekijk server logs voor errors

### Test betalingen werken niet
- Zorg dat je test keys gebruikt
- Gebruik test credit card nummers van Stripe
- Check of je in test mode bent in Stripe Dashboard

## Support

Voor vragen over Stripe setup:
- Stripe Documentatie: https://stripe.com/docs
- Stripe Support: https://support.stripe.com

Voor vragen over de applicatie:
- Check de server logs
- Bekijk de database voor subscription status
- Test de webhook endpoint handmatig
