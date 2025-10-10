# Automatische Blog Generator

## 📝 Overzicht

De automatische blog generator is een nieuwe feature die stap 4 (Tekstschrijver) van de artikel-generator workflow volledig automatiseert. Deze functionaliteit genereert complete, professionele blogs met:

- ✅ Automatisch gezochte afbeeldingen van Pixabay, Pexels en Unsplash
- ✅ Automatisch gevonden interne links via sitemap scraping
- ✅ Geïntegreerde affiliate links (Booking.com, GetYourGuide, etc.)
- ✅ Complete blog structuur met headings, tips, FAQ, etc.
- ✅ Markdown en HTML output formaten
- ✅ Werkt voor ELKE website die wordt toegevoegd

## 🏗️ Architectuur

### Nieuwe Modules

1. **blog_generator.py** - Hoofdmodule die alle componenten orkestreert
2. **image_fetcher.py** - Haalt afbeeldingen op van meerdere bronnen
3. **sitemap_parser.py** - Parse sitemaps en vindt relevante interne links
4. **affiliate_linker.py** - Genereert affiliate links op basis van onderwerp
5. **markdown_generator.py** - Converteert tussen HTML en Markdown

### Workflow

```
Content Planning (Stap 3)
    ↓
Automatische Blog Generatie (Stap 4)
    ↓
1. Afbeeldingen zoeken (Pixabay/Pexels/Unsplash)
    ↓
2. Interne links extraheren (Sitemap parsing)
    ↓
3. Affiliate links genereren (Configureerbaar)
    ↓
4. Blog content genereren (AI met alle elementen)
    ↓
5. Markdown conversie
    ↓
Opslaan in database
```

## 🚀 Gebruik

### Via Content Planning

1. Maak een content plan aan in stap 3
2. Koppel een WordPress site (optioneel maar aanbevolen)
3. Klik op "Genereer Artikel" bij het content plan
4. De automatische blog generator wordt gebruikt als:
   - Pixabay API key is geconfigureerd
   - Een website URL beschikbaar is

### API Endpoint

```http
POST /api/content-plans/{plan_id}/generate-article
```

**Response:**
```json
{
  "success": true,
  "content": "<html content>",
  "markdown": "# Markdown content",
  "metadata": {
    "topic": "Valencia met kinderen",
    "word_count": 1500,
    "images_count": 3,
    "internal_links_count": 8,
    "affiliate_links_count": 4
  },
  "article_id": 123,
  "message": "Blog succesvol gegenereerd met afbeeldingen en links"
}
```

## ⚙️ Configuratie

### API Keys

De blog generator heeft de volgende API keys nodig:

1. **Pixabay** (verplicht) - Voor afbeeldingen
2. **Pexels** (optioneel) - Extra afbeeldingenbron
3. **Unsplash** (optioneel) - Extra afbeeldingenbron
4. **OpenAI** (verplicht) - Voor content generatie

API keys worden geladen uit:
- Environment variabelen
- `/home/ubuntu/.config/abacusai_auth_secrets.json`

### Affiliate Links Configuratie

Affiliate links worden per website geconfigureerd in de database:

```sql
INSERT INTO affiliate_links (site_id, anchor_text, url)
VALUES 
  (1, 'Boek je hotel', 'https://www.booking.com/...?aid=YOUR_ID'),
  (1, 'Boek tours', 'https://www.getyourguide.com/...?partner_id=YOUR_ID');
```

Ondersteunde platforms:
- Booking.com
- GetYourGuide
- Viator
- RentalCars

## 🎨 Features

### Afbeeldingen

- **Automatisch zoeken**: 1 afbeelding per 500 woorden
- **Meerdere bronnen**: Pixabay → Pexels → Unsplash fallback
- **Relevante zoektermen**: AI-gegenereerde zoektermen in het Engels
- **Metadata**: Volledige attributie en alt-text

### Interne Links

- **Sitemap parsing**: Automatisch detecteren en parsen van sitemaps
- **Relevantie filtering**: Alleen relevante pagina's op basis van onderwerp
- **Natuurlijke integratie**: Links worden natuurlijk in de tekst verwerkt

### Affiliate Links

- **Configureerbaar**: Per website instelbaar
- **Contextgevoelig**: Alleen relevante affiliate links worden toegevoegd
- **Natuurlijke anchor text**: Automatisch gegenereerde, natuurlijke linkteksten

### Content Structuur

Gegenereerde blogs bevatten:
- Professionele inleiding
- Meerdere hoofdsecties met subsecties
- Praktische tips sectie
- FAQ sectie (minimaal 5 vragen)
- Conclusie
- Gelijkmatig verdeelde afbeeldingen
- Natuurlijk geïntegreerde links

## 🔧 Technische Details

### Image Fetcher

```python
from image_fetcher import ImageFetcher

fetcher = ImageFetcher(
    pixabay_api_key="YOUR_KEY",
    pexels_api_key="YOUR_KEY",  # Optioneel
    unsplash_access_key="YOUR_KEY"  # Optioneel
)

result = fetcher.search_images(
    query="Valencia beach",
    source="pixabay",
    limit=5
)
```

### Sitemap Parser

```python
from sitemap_parser import SitemapParser

parser = SitemapParser()

result = parser.parse_sitemap(
    website_url="https://goholidays.nl",
    sitemap_url=None  # Auto-detect
)

relevant_links = parser.find_relevant_urls(
    urls=result['urls'],
    topic="Valencia met kinderen",
    limit=10
)
```

### Affiliate Linker

```python
from affiliate_linker import AffiliateLinker

linker = AffiliateLinker()

config = {
    'booking.com': {
        'base_url': 'https://www.booking.com/searchresults.html',
        'params': {
            'aid': 'YOUR_AFFILIATE_ID',
            'ss': '{destination}'
        }
    }
}

links = linker.generate_links(
    topic="Valencia met kinderen",
    config=config
)
```

### Blog Generator

```python
from blog_generator import BlogGenerator

generator = BlogGenerator(
    pixabay_api_key="YOUR_KEY"
)

result = generator.generate_blog(
    topic="Valencia met kinderen",
    word_count=1500,
    website_url="https://goholidays.nl",
    sitemap_url=None,  # Auto-detect
    affiliate_config=config,
    extra_context="Focus op familie-vriendelijke activiteiten",
    model="gpt-4o"
)
```

## 📊 Database Schema

### Content Plans Table

```sql
CREATE TABLE content_plans (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    keyword TEXT,
    target_date DATE,
    status TEXT DEFAULT 'draft',
    article_id INTEGER,
    wordpress_site_id INTEGER,
    word_count INTEGER DEFAULT 1000,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Affiliate Links Table

```sql
CREATE TABLE affiliate_links (
    id INTEGER PRIMARY KEY,
    site_id INTEGER,
    anchor_text TEXT,
    url TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES wordpress_sites(id)
);
```

## 🎯 Voorbeelden

### Voorbeeld 1: Valencia met kinderen

**Input:**
- Topic: "Valencia met kinderen"
- Word count: 1500
- Website: goholidays.nl

**Output:**
- 3 afbeeldingen van Valencia stranden en attracties
- 8 interne links naar relevante pagina's
- 4 affiliate links (Booking.com, GetYourGuide)
- Complete blog met tips, FAQ en praktische informatie

### Voorbeeld 2: Romantische Praag

**Input:**
- Topic: "Romantisch weekend Praag"
- Word count: 1200
- Website: goholidays.nl

**Output:**
- 2-3 afbeeldingen van Praag
- 6 interne links
- 3 affiliate links
- Blog met romantische tips en restaurant aanbevelingen

## 🔄 Fallback Mechanisme

Als de automatische blog generator niet beschikbaar is:
1. Check of Pixabay API key aanwezig is
2. Check of website URL beschikbaar is
3. Zo niet → gebruik standaard `generate_general_article()` functie
4. Gebruiker krijgt nog steeds een artikel, maar zonder automatische features

## 🚨 Error Handling

De blog generator heeft robuuste error handling:
- API failures worden gracefully afgehandeld
- Fallback naar alternatieve afbeeldingenbronnen
- Duidelijke error messages in logs
- Geen crashes bij ontbrekende data

## 📈 Toekomstige Uitbreidingen

Mogelijke verbeteringen:
- [ ] Video integratie (YouTube embeds)
- [ ] Meer affiliate platforms
- [ ] AI-gegenereerde afbeeldingen (DALL-E)
- [ ] Automatische SEO optimalisatie
- [ ] Multi-language support
- [ ] Scheduled publishing
- [ ] A/B testing voor verschillende versies

## 🤝 Integratie met Bestaande Workflow

De automatische blog generator integreert naadloos met:
1. **Website toevoegen** - Gebruikt toegevoegde websites voor interne links
2. **Zoekwoordonderzoek** - Gebruikt keywords voor relevante content
3. **Content planning** - Genereert blogs op basis van planning
4. **WordPress publicatie** - Blogs kunnen direct gepubliceerd worden

## 📝 Licentie

Deze functionaliteit is onderdeel van WritgoAI en volgt dezelfde licentie.
