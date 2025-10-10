
# Website Beheer - Affiliate Links & Feeds

## 📝 Overzicht

De Website Beheer sectie biedt complete controle over affiliate links en product feeds per website. Deze functionaliteit is **flexibel voor elke niche** - niet alleen reizen, maar ook e-commerce, software, diensten, en meer.

## 🎯 Features

### 1. Affiliate Links Management
- ✅ Directe affiliate links toevoegen per website
- ✅ Anchor text en URL configureren
- ✅ Categorieën toewijzen voor intelligente matching
- ✅ Prioriteit instellen (hogere prioriteit = vaker gebruikt)
- ✅ Links activeren/deactiveren
- ✅ Notities toevoegen voor intern gebruik

### 2. Product Feeds
- ✅ XML, JSON en CSV feeds importeren
- ✅ Automatische product import en caching
- ✅ Update frequentie instellen (hourly, daily, weekly)
- ✅ Product categorieën en metadata
- ✅ Automatische feed refresh

### 3. Intelligente Link Matching
- ✅ Automatische selectie van relevante links op basis van blog onderwerp
- ✅ Categorie-gebaseerde filtering
- ✅ Prioriteit-gebaseerde sortering
- ✅ Natuurlijke integratie in blog content

## 🚀 Gebruik

### Via de UI

1. **Navigeer naar Website Beheer**
   - Klik op "🌐 Website Beheer" in het menu
   - Selecteer een website uit de lijst

2. **Affiliate Links Toevoegen**
   - Klik op "➕ Affiliate Link Toevoegen"
   - Vul de velden in:
     - **Anchor Text**: De linktekst (bijv. "Boek je hotel")
     - **URL**: De affiliate URL
     - **Categorie**: Optioneel (bijv. "hotels", "tours", "producten")
     - **Prioriteit**: 0-100 (hoger = vaker gebruikt)
     - **Notities**: Interne notities
   - Klik op "Opslaan"

3. **Product Feed Toevoegen**
   - Klik op "📦 Product Feed Toevoegen"
   - Vul de velden in:
     - **Feed Naam**: Beschrijvende naam
     - **Feed URL**: URL van de XML/JSON/CSV feed
     - **Feed Type**: xml, json of csv
     - **Update Frequentie**: hourly, daily of weekly
   - Klik op "Importeren"

4. **Links Beheren**
   - Bekijk alle links in de lijst
   - Klik op "✏️" om te bewerken
   - Klik op "🗑️" om te verwijderen
   - Toggle de schakelaar om te activeren/deactiveren

### Via de API

#### Affiliate Links

**GET** `/api/websites/{website_id}/affiliate-links`
```json
{
  "success": true,
  "links": [
    {
      "id": 1,
      "website_id": 1,
      "anchor_text": "Boek je hotel",
      "url": "https://booking.com/...",
      "category": "hotels",
      "priority": 10,
      "link_type": "direct",
      "is_active": true
    }
  ]
}
```

**POST** `/api/websites/{website_id}/affiliate-links`
```json
{
  "anchor_text": "Boek je hotel",
  "url": "https://booking.com/...",
  "category": "hotels",
  "priority": 10,
  "notes": "Booking.com affiliate link"
}
```

**PUT** `/api/websites/{website_id}/affiliate-links/{link_id}`
```json
{
  "anchor_text": "Vind je hotel",
  "priority": 15
}
```

**DELETE** `/api/websites/{website_id}/affiliate-links/{link_id}`

#### Affiliate Feeds

**GET** `/api/websites/{website_id}/affiliate-feeds`
```json
{
  "success": true,
  "feeds": [
    {
      "id": 1,
      "website_id": 1,
      "feed_name": "Bol.com Products",
      "feed_url": "https://...",
      "feed_type": "xml",
      "product_count": 150,
      "last_updated": "2025-10-10T10:00:00"
    }
  ]
}
```

**POST** `/api/websites/{website_id}/affiliate-feeds`
```json
{
  "feed_name": "Bol.com Products",
  "feed_url": "https://partnerprogramma.bol.com/feed.xml",
  "feed_type": "xml",
  "update_frequency": "daily"
}
```

**POST** `/api/websites/{website_id}/affiliate-feeds/{feed_id}/import`
- Importeert producten uit de feed

**DELETE** `/api/websites/{website_id}/affiliate-feeds/{feed_id}`

## 📚 Voorbeelden per Niche

### Reizen Website

```python
# Hotels
{
  "anchor_text": "Boek je hotel in Amsterdam",
  "url": "https://www.booking.com/searchresults.html?aid=YOUR_ID&ss=Amsterdam",
  "category": "hotels",
  "priority": 10
}

# Tours
{
  "anchor_text": "Boek tours en activiteiten",
  "url": "https://www.getyourguide.com/amsterdam-l36/?partner_id=YOUR_ID",
  "category": "tours",
  "priority": 8
}

# Autoverhuur
{
  "anchor_text": "Huur een auto",
  "url": "https://www.rentalcars.com/?affiliateCode=YOUR_ID",
  "category": "transport",
  "priority": 5
}
```

### E-commerce Website

```python
# Bol.com affiliate
{
  "anchor_text": "Bekijk op Bol.com",
  "url": "https://partner.bol.com/click/click?p=2&t=url&s=YOUR_SITE_ID&url=...",
  "category": "producten",
  "priority": 10
}

# Amazon affiliate
{
  "anchor_text": "Koop op Amazon",
  "url": "https://www.amazon.nl/dp/PRODUCT_ID?tag=YOUR_TAG",
  "category": "producten",
  "priority": 8
}

# Product feed
{
  "feed_name": "Bol.com Product Feed",
  "feed_url": "https://partnerprogramma.bol.com/feed/YOUR_ID.xml",
  "feed_type": "xml",
  "update_frequency": "daily"
}
```

### Software/SaaS Website

```python
# Software affiliate
{
  "anchor_text": "Probeer gratis",
  "url": "https://software.com/?ref=YOUR_ID",
  "category": "software",
  "priority": 10
}

# Hosting affiliate
{
  "anchor_text": "Beste hosting provider",
  "url": "https://hosting.com/aff/YOUR_ID",
  "category": "hosting",
  "priority": 8
}
```

### Diensten Website

```python
# Verzekeringen
{
  "anchor_text": "Vergelijk verzekeringen",
  "url": "https://verzekeringen.nl/?partner=YOUR_ID",
  "category": "verzekeringen",
  "priority": 10
}

# Energie
{
  "anchor_text": "Vergelijk energieleveranciers",
  "url": "https://energie.nl/?ref=YOUR_ID",
  "category": "energie",
  "priority": 8
}
```

## 🔧 Integratie met Blog Generator

De affiliate links worden automatisch gebruikt door de blog generator:

1. **Automatische Selectie**
   - Blog generator analyseert het onderwerp
   - Selecteert relevante links op basis van categorie en prioriteit
   - Integreert links natuurlijk in de content

2. **Intelligente Plaatsing**
   - Links worden verspreid over de blog
   - Natuurlijke anchor text
   - Contextgevoelige plaatsing

3. **Feed Producten**
   - Producten uit feeds kunnen automatisch worden toegevoegd
   - Relevante producten op basis van blog onderwerp
   - Complete product informatie (naam, prijs, afbeelding)

## 📊 Database Schema

### website_affiliate_links
```sql
CREATE TABLE website_affiliate_links (
    id INTEGER PRIMARY KEY,
    website_id INTEGER,
    anchor_text TEXT,
    url TEXT,
    category TEXT,
    priority INTEGER DEFAULT 0,
    link_type TEXT DEFAULT 'direct',
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### website_affiliate_feeds
```sql
CREATE TABLE website_affiliate_feeds (
    id INTEGER PRIMARY KEY,
    website_id INTEGER,
    feed_name TEXT,
    feed_url TEXT,
    feed_type TEXT DEFAULT 'xml',
    update_frequency TEXT DEFAULT 'daily',
    last_updated TIMESTAMP,
    product_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### feed_products
```sql
CREATE TABLE feed_products (
    id INTEGER PRIMARY KEY,
    feed_id INTEGER,
    product_id TEXT,
    product_name TEXT,
    product_url TEXT,
    product_price TEXT,
    product_category TEXT,
    product_image TEXT,
    product_description TEXT,
    created_at TIMESTAMP
)
```

## 🎨 UI Componenten

De Website Beheer sectie bevat:

1. **Website Selector**
   - Dropdown met alle websites
   - Snelle navigatie tussen websites

2. **Tabs**
   - Affiliate Links tab
   - Product Feeds tab
   - Preview tab

3. **Affiliate Links Lijst**
   - Tabel met alle links
   - Edit/Delete knoppen
   - Active/Inactive toggle
   - Sorteerbaar op prioriteit

4. **Add Link Form**
   - Inline formulier
   - Validatie
   - Direct opslaan

5. **Feeds Lijst**
   - Feed naam en URL
   - Product count
   - Last updated timestamp
   - Import knop

6. **Preview Sectie**
   - Voorbeeld van hoe links verschijnen in blogs
   - Test met sample content

## 🔄 Automatische Updates

Product feeds worden automatisch geüpdatet op basis van de ingestelde frequentie:

- **Hourly**: Elk uur
- **Daily**: Dagelijks om 00:00
- **Weekly**: Wekelijks op zondag om 00:00

Updates kunnen ook handmatig worden getriggerd via de UI of API.

## 🛡️ Best Practices

1. **Categorieën Gebruiken**
   - Gebruik duidelijke categorieën voor betere matching
   - Voorbeelden: "hotels", "tours", "producten", "software"

2. **Prioriteit Instellen**
   - Belangrijkste links krijgen hogere prioriteit
   - Gebruik 0-100 schaal
   - Hoogste prioriteit = meest gebruikt

3. **Feeds Monitoren**
   - Check regelmatig of feeds nog werken
   - Monitor product count
   - Update feed URLs indien nodig

4. **Link Testing**
   - Test affiliate links regelmatig
   - Controleer of tracking werkt
   - Update broken links

5. **Notities Bijhouden**
   - Gebruik notities voor interne documentatie
   - Noteer affiliate IDs en tracking info
   - Documenteer speciale configuraties

## 🚨 Troubleshooting

### Feed Import Faalt
- Controleer of feed URL toegankelijk is
- Verificeer feed format (XML/JSON/CSV)
- Check feed structuur (moet standaard format volgen)

### Links Verschijnen Niet in Blogs
- Controleer of links actief zijn (is_active = 1)
- Verificeer categorie matching met blog onderwerp
- Check prioriteit (hogere prioriteit = meer kans)

### Producten Niet Geïmporteerd
- Controleer feed format
- Verificeer product structuur in feed
- Check error logs in console

## 📞 Support

Voor vragen of problemen:
- Check de documentatie
- Bekijk de voorbeelden
- Contact: info@writgo.nl
