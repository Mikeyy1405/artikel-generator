# ✍️ Schrijfstijl & Affiliate Feeds - Gebruikershandleiding

## 📝 Eigen Schrijfstijl

### Wat is het?
Definieer jouw unieke schrijfstijl zodat de AI content genereert die perfect past bij jouw merk en doelgroep.

### Velden:

#### 1. **Schrijftoon**
Kies uit voorgedefinieerde tonen:
- **Professioneel** - Zakelijk en betrouwbaar
- **Casual & Toegankelijk** - Relaxed en vriendelijk
- **Vriendelijk & Persoonlijk** - Warm en betrokken
- **Formeel & Zakelijk** - Officieel en correct
- **Enthousiast & Energiek** - Positief en motiverend
- **Informatief & Educatief** - Leerzaam en duidelijk
- **Inspirerend & Motiverend** - Aanmoedigend en krachtig

#### 2. **Doelgroep**
Beschrijf wie je lezers zijn:
- Voorbeelden: "Jonge professionals 25-35 jaar", "Ouders met jonge kinderen", "Ondernemers in tech", "Studenten"
- Hoe specifieker, hoe beter de AI kan targeten

#### 3. **Schrijfstijl Beschrijving**
Gedetailleerde beschrijving van jouw stijl:
```
Voorbeeld:
"Ik schrijf in korte, krachtige zinnen. Gebruik veel praktische voorbeelden 
en concrete tips. Vermijd jargon en schrijf toegankelijk. Begin paragrafen 
met een sterke opening. Gebruik actieve zinnen in plaats van passieve. 
Voeg regelmatig vragen toe om de lezer te betrekken."
```

#### 4. **Voorbeeldteksten** (optioneel maar aanbevolen)
Plak 2-3 paragrafen van jouw beste content:
- De AI analyseert deze teksten
- Leert jouw woordkeuze, zinsstructuur en stijl
- Genereert content die hierop lijkt

**💡 Tip:** Hoe meer voorbeelden, hoe beter de AI jouw stijl kan nabootsen!

---

## 🔗 Affiliate Links & Feeds

### Ondersteunde Netwerken:

### 1. 🛒 **Bol.com Partner**

**Wat heb je nodig:**
- Client ID
- Client Secret

**Hoe te verkrijgen:**
1. Ga naar [Bol.com Partner Portal](https://partnerblog.bol.com/nl/documentatie/open-api/)
2. Registreer als partner
3. Vraag API toegang aan
4. Kopieer je Client ID en Secret

**Wat kan je ermee:**
- Automatisch productlinks toevoegen
- Real-time productinformatie ophalen
- Commissie verdienen op verkopen

---

### 2. 📊 **TradeTracker**

**Wat heb je nodig:**
- Site ID
- API Key

**Hoe te verkrijgen:**
1. Log in op [TradeTracker](https://tradetracker.com/nl/affiliate/api)
2. Ga naar Account → API
3. Genereer een nieuwe API key
4. Noteer je Site ID

**Wat kan je ermee:**
- Toegang tot duizenden merchants
- Productfeeds van verschillende shops
- Tracking en rapportage

---

### 3. 🌼 **Daisycon**

**Wat heb je nodig:**
- Publisher ID

**Hoe te verkrijgen:**
1. Log in op [Daisycon](https://www.daisycon.com/nl/publishers/)
2. Ga naar je account instellingen
3. Vind je Publisher ID

**Wat kan je ermee:**
- Nederlandse en Belgische merchants
- Diverse productcategorieën
- Betrouwbare tracking

---

### 4. ✨ **Eigen Affiliate Links**

**Formaat:**
```
Naam: URL
```

**Voorbeelden:**
```
Amazon: https://amzn.to/jouwlink
Coolblue: https://partner.coolblue.nl/click/12345
MediaMarkt: https://www.awin1.com/...
Wehkamp: https://tc.tradetracker.net/...
```

**Gebruik:**
- Voeg elke link op een nieuwe regel toe
- Gebruik duidelijke namen
- Werkt met elk affiliate netwerk

---

## 🚀 Hoe te gebruiken

### Stap 1: Vul je gegevens in
1. Ga naar **Mijn Account**
2. Scroll naar **✍️ Eigen Schrijfstijl**
3. Vul alle velden in
4. Klik op **Schrijfstijl Opslaan**

### Stap 2: Koppel affiliate netwerken
1. Scroll naar **🔗 Affiliate Links & Feeds**
2. Vul de credentials in van je netwerken
3. Voeg custom links toe indien gewenst
4. Klik op **Affiliate Instellingen Opslaan**

### Stap 3: Genereer content
- De AI gebruikt nu automatisch jouw schrijfstijl
- Affiliate links worden automatisch toegevoegd waar relevant
- Content is gepersonaliseerd naar jouw doelgroep

---

## 🔒 Beveiliging

### Hoe worden je gegevens opgeslagen?
- **Encrypted database** - Alle data is veilig opgeslagen
- **Password velden** - Gevoelige data wordt verborgen in de UI
- **Geen delen** - Je credentials worden nooit gedeeld
- **Lokale opslag** - Data blijft op de server

### Best Practices:
✅ Gebruik sterke, unieke API keys
✅ Vernieuw je keys regelmatig
✅ Deel je credentials nooit
✅ Check regelmatig je affiliate dashboards

---

## 💡 Tips voor beste resultaten

### Schrijfstijl:
1. **Wees specifiek** - Hoe meer detail, hoe beter
2. **Gebruik voorbeelden** - Laat de AI van je leren
3. **Update regelmatig** - Pas aan als je stijl evolueert
4. **Test verschillende tonen** - Vind wat het beste werkt

### Affiliate Links:
1. **Koppel meerdere netwerken** - Meer opties = meer inkomsten
2. **Houd credentials up-to-date** - Voorkom broken links
3. **Monitor prestaties** - Check welke netwerken het beste werken
4. **Diversifieer** - Gebruik verschillende merchants

---

## 🆘 Troubleshooting

### Schrijfstijl werkt niet?
- ✅ Check of je alle velden hebt ingevuld
- ✅ Voeg voorbeeldteksten toe voor betere resultaten
- ✅ Wees specifieker in je beschrijving

### Affiliate links werken niet?
- ✅ Controleer je credentials in het affiliate dashboard
- ✅ Zorg dat je API toegang hebt geactiveerd
- ✅ Check of je links correct zijn geformatteerd
- ✅ Vernieuw je API keys als ze verlopen zijn

### Data wordt niet opgeslagen?
- ✅ Check je internetverbinding
- ✅ Probeer opnieuw in te loggen
- ✅ Clear je browser cache
- ✅ Neem contact op met support

---

## 📊 Database Schema

### Nieuwe velden in `users` tabel:

```sql
-- Schrijfstijl
writing_tone TEXT DEFAULT 'professioneel'
target_audience TEXT
writing_style TEXT
writing_examples TEXT

-- Affiliate Feeds
bol_client_id TEXT
bol_client_secret TEXT
tradetracker_id TEXT
tradetracker_api_key TEXT
daisycon_id TEXT
custom_affiliate_links TEXT
```

---

## 🔄 Migratie

Voor bestaande databases:
```bash
python3 migrate_writing_style.py
```

Dit voegt automatisch alle nieuwe velden toe zonder data te verliezen.

---

## 📞 Support

Vragen of problemen?
- 📧 Email: info@writgo.nl
- 📖 Documentatie: Zie deze guide
- 🐛 Bug report: GitHub Issues

---

**Veel succes met het personaliseren van je content! 🚀**
