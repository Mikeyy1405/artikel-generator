# Deployment Instructies - Stripe Payment Integration

## Wat is er toegevoegd?

✅ Stripe betalingssysteem (€99/maand abonnement)
✅ Gebruikers moeten betalen voordat ze kunnen inloggen
✅ Betaalpagina met moderne UI
✅ Webhook handlers voor subscription events
✅ Database migratie voor subscription velden
✅ Success en cancel pagina's

## Stap 1: Push naar GitHub

Voer de volgende commando's uit in je lokale terminal:

```bash
cd /pad/naar/artikel-generator
git pull origin main
git push origin main
```

Als je geen toegang hebt, download dan de patch file en pas deze toe:
```bash
git apply 0001-Add-Stripe-payment-integration.patch
git push origin main
```

## Stap 2: Stripe Keys Toevoegen op Render

1. Ga naar https://dashboard.render.com
2. Selecteer je "artikel-generator" web service
3. Ga naar **Environment** tab
4. Voeg de volgende environment variables toe:

```
STRIPE_SECRET_KEY=sk_test_51QVxxx... (of sk_live_...)
STRIPE_PUBLISHABLE_KEY=pk_test_51QVxxx... (of pk_live_...)
STRIPE_WEBHOOK_SECRET=whsec_xxx...
```

### Waar vind je deze keys?

**Stripe Dashboard**: https://dashboard.stripe.com

1. **API Keys** (Secret & Publishable):
   - Ga naar: Developers → API keys
   - Kopieer "Publishable key" (pk_test_... of pk_live_...)
   - Kopieer "Secret key" (sk_test_... of sk_live_...)

2. **Webhook Secret**:
   - Ga naar: Developers → Webhooks
   - Klik "Add endpoint"
   - URL: `https://artikel-generator-xxx.onrender.com/api/stripe/webhook`
   - Selecteer events:
     * checkout.session.completed
     * customer.subscription.updated
     * customer.subscription.deleted
     * invoice.payment_succeeded
     * invoice.payment_failed
   - Kopieer de "Signing secret" (whsec_...)

## Stap 3: Database Migratie (Automatisch)

De database wordt automatisch gemigreerd bij de eerste start. Er worden nieuwe velden toegevoegd:
- stripe_customer_id
- stripe_subscription_id
- subscription_status
- subscription_start_date
- subscription_end_date

## Stap 4: Test de Betaling

### Test Mode (Aanbevolen eerst)
1. Gebruik test keys (sk_test_... en pk_test_...)
2. Maak een nieuw account aan
3. Je wordt doorgestuurd naar de betaalpagina
4. Gebruik test creditcard: `4242 4242 4242 4242`
5. Expiry: elke toekomstige datum (bijv. 12/25)
6. CVC: 123
7. Postcode: 1234AB

### Live Mode (Productie)
1. Vervang test keys door live keys (sk_live_... en pk_live_...)
2. Echte betalingen worden nu verwerkt
3. Zorg dat je Stripe account volledig is ingesteld

## Stap 5: Superuser Aanmaken (Optioneel)

Als je zelf toegang wilt zonder te betalen:

```sql
-- Verbind met je database en voer uit:
UPDATE users 
SET is_superuser = 1, subscription_status = 'active' 
WHERE email = 'jouw@email.com';
```

## Verificatie Checklist

✅ Environment variables toegevoegd op Render
✅ Webhook endpoint geconfigureerd in Stripe
✅ Test betaling succesvol afgerond
✅ Gebruiker kan inloggen na betaling
✅ Webhook events worden ontvangen

## Troubleshooting

### "Payment required" bij inloggen
- Check of subscription_status = 'active' in database
- Controleer of webhook is ontvangen (Stripe Dashboard → Webhooks)

### Webhook errors
- Controleer of STRIPE_WEBHOOK_SECRET correct is
- Check of de webhook URL klopt
- Bekijk logs in Render dashboard

### Betaling succesvol maar geen toegang
- Check database: `SELECT subscription_status FROM users WHERE email = '...'`
- Bekijk webhook logs in Stripe Dashboard
- Check Render logs voor errors

## Support

Zie `STRIPE_SETUP.md` voor gedetailleerde Stripe configuratie instructies.
