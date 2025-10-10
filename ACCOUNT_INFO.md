# 🔐 WritgoAI Account Informatie

## Superuser Account

**Email:** info@writgo.nl  
**Wachtwoord:** WritgoAI2025!

## Database Migratie

Als je de applicatie voor het eerst start of na een update, voer dan de database migratie uit:

```bash
python3 migrate_db.py
```

Dit script:
- ✅ Maakt de users tabel aan
- ✅ Voegt user_id toe aan alle bestaande tabellen
- ✅ Creëert het superuser account
- ✅ Behoudt alle bestaande data

## Wat is er veranderd?

### 🎯 Account Systeem
- Alle data wordt nu per gebruiker opgeslagen
- Session-based authenticatie
- Auto-login voor superuser (tijdelijk voor development)

### 📊 Database Structuur
- **users** tabel met email, password_hash, is_superuser
- **user_id** kolom toegevoegd aan:
  - articles
  - wordpress_sites
  - websites
  - internal_links (via site_id)
  - affiliate_links (via site_id)
  - knowledge_base (via site_id)

### 🔒 Beveiliging
- Password hashing met SHA256
- Session management
- Login/logout endpoints

## API Endpoints

### Login
```bash
POST /api/auth/login
{
  "email": "info@writgo.nl",
  "password": "WritgoAI2025!"
}
```

### Logout
```bash
POST /api/auth/logout
```

### Get Current User
```bash
GET /api/auth/me
```

## Deployment op Render

Na deployment op Render:
1. De database wordt automatisch aangemaakt
2. Het superuser account wordt automatisch gecreëerd
3. Je kunt direct inloggen met de bovenstaande credentials

## Toekomstige Verbeteringen

- [ ] Login pagina UI
- [ ] Wachtwoord reset functionaliteit
- [ ] Gebruikersbeheer voor superusers
- [ ] OAuth integratie (Google, Microsoft)
- [ ] 2FA (Two-Factor Authentication)
- [ ] Betere password hashing (bcrypt)
