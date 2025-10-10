# DeepAgent & Website Management Update

## Datum: 10 Oktober 2025

## Samenvatting
Grote update met volledige website management functionaliteit en DeepAgent integratie voor automatische keyword research en content planning.

---

## 🔄 Wat is er veranderd?

### 1. ⚡ DeepAgent Integratie (vervangen van Perplexity)

**Nieuwe module:** `deepagent_research.py`

DeepAgent wordt nu gebruikt voor:
- ✅ **Keyword Research**: Genereert 150+ SEO keywords per website
- ✅ **Content Planning**: Creëert gedetailleerde content plannen
- ✅ **Web Search**: Voor research doeleinden (uitbreidbaar)

**Voordelen:**
- Intelligentere keyword analyse
- Betere content afstemming op niche en doelgroep
- Meer controle over research proces
- OpenAI fallback ingebouwd

**Bestanden:**
- `deepagent_research.py` - DeepAgent module
- `app.py` - Geïntegreerd in onboarding flow

---

### 2. 🌐 Website Management Systeem

**Nieuwe module:** `website_management_api.py`

Complete website management met 5 categorieën:

#### 📋 **Basis Informatie**
- Website naam
- Niche/industrie
- Doelgroep
- Tone of voice (6 opties)

#### 💡 **Context & Knowledgebase**
- Website context (korte beschrijving)
- Uitgebreide knowledgebase (bedrijfsinfo, producten, diensten, USPs)
- Wordt gebruikt voor relevantere content generatie

#### 🔗 **Externe Links**
- Beheer externe links die in artikelen moeten worden opgenomen
- Perfect voor affiliate links, product pages, landingspagina's
- URL + anchor tekst per link

#### 📅 **Posting Planning**
- Posting schema (dagelijks/3x/5x week/wekelijks/maandelijks)
- Posting dagen selectie
- Posting tijd
- Auto-publish toggle

#### 🔌 **WordPress Integratie**
- WordPress URL
- Username
- Application Password
- Verbindingsstatus indicator

**Bestanden:**
- `website_management_api.py` - Backend API
- `static/website_management_modal.js` - Frontend interface
- `app.py` - API routes toegevoegd

---

### 3. 🗄️ Database Updates

**Nieuwe velden in `websites` tabel:**

```sql
niche TEXT                    -- Niche/industrie
target_audience TEXT          -- Doelgroep  
tone_of_voice TEXT            -- Schrijfstijl (default: 'professional')
context TEXT                  -- Algemene context
knowledgebase TEXT            -- Uitgebreide kennis (JSON format)
external_links TEXT           -- Externe links (JSON format)
```

**Migratie script:** `migrate_website_management.py`

**JSON Formats:**

```json
// knowledgebase (flexible)
{
  "bedrijf": "...",
  "producten": "...",
  "usps": "...",
  "custom_fields": "..."
}

// external_links
[
  {
    "url": "https://example.com/page",
    "anchor": "Anchor tekst"
  }
]
```

---

## 📁 Nieuwe Bestanden

| Bestand | Doel |
|---------|------|
| `deepagent_research.py` | DeepAgent integratie module |
| `website_management_api.py` | Website management backend |
| `static/website_management_modal.js` | Website management UI (tabs) |
| `migrate_website_management.py` | Database migratie script |
| `DEEPAGENT_WEBSITE_MANAGEMENT.md` | Deze documentatie |

---

## 🔧 Gewijzigde Bestanden

### `app.py`
- DeepAgent imports toegevoegd
- Website management API imports
- `/api/websites/<id>/management` endpoint (GET/PUT)
- Onboarding keyword research gebruikt nu DeepAgent
- Onboarding content planning gebruikt nu DeepAgent

### `templates/index.html`
- Script include voor website management modal
- Gebruikt bestaande "Instellingen Bewerken" button

---

## 🎨 UI Features

### Website Management Modal

**5 Tabs met Moderne Styling:**
1. 📋 **Basis Info** - Kern website gegevens
2. 💡 **Context** - Context en knowledgebase
3. 🔗 **Externe Links** - Link management met add/remove
4. 📅 **Planning** - Posting schema instellingen
5. 🔌 **WordPress** - Integratie credentials

**Features:**
- ✅ Moderne gradient header
- ✅ Tab navigatie met visuele feedback
- ✅ Responsive design
- ✅ Real-time validatie
- ✅ Inline help text en tips
- ✅ Status indicators (WordPress verbonden, laatste post, etc.)
- ✅ Dynamic form fields (posting dagen alleen bij relevante schema's)

---

## 🚀 Gebruik

### Voor Gebruikers:

1. **Website Selecteren**
   - Ga naar dashboard
   - Klik op "⚙️ Instellingen Bewerken" bij een website

2. **Basis Info Invullen**
   - Vul niche, doelgroep en tone of voice in
   - Dit helpt de AI betere content te maken

3. **Context Toevoegen**
   - Beschrijf je bedrijf/website
   - Voeg uitgebreide kennis toe in knowledgebase
   - Hoe meer detail, hoe beter de content!

4. **Externe Links (Optioneel)**
   - Voeg links toe die je in artikelen wilt
   - Klik "➕ Nieuwe Link Toevoegen"
   - Vul URL en anchor tekst in

5. **Planning Instellen**
   - Kies posting schema
   - Selecteer dagen (indien nodig)
   - Stel posting tijd in
   - Toggle auto-publish aan/uit

6. **WordPress Verbinden**
   - Voeg WordPress URL toe
   - Vul username in
   - Genereer Application Password in WordPress
   - Plak het hier

7. **Opslaan**
   - Klik "💾 Opslaan"
   - Instellingen worden toegepast op alle toekomstige content

### Voor Ontwikkelaars:

**API Endpoints:**

```python
# Get website management data
GET /api/websites/<website_id>/management
Response: {
    'success': True,
    'website': {...},  # All website data
    'schedule': {...}  # Schedule settings
}

# Update website management
PUT /api/websites/<website_id>/management
Body: {
    'name': 'Website Name',
    'niche': 'Digital Marketing',
    'target_audience': 'Entrepreneurs',
    'tone_of_voice': 'professional',
    'context': 'Website description...',
    'knowledgebase': 'Extended knowledge...',
    'external_links': [
        {'url': 'https://...', 'anchor': '...'}
    ],
    'posting_schedule': 'weekly',
    'posting_days': ['monday', 'wednesday'],
    'posting_time': '09:00',
    'auto_publish': True,
    'wordpress_url': 'https://...',
    'wordpress_username': '...',
    'wordpress_password': '...'
}
```

**DeepAgent Functions:**

```python
from deepagent_research import (
    deepagent_keyword_research,
    deepagent_content_planning,
    deepagent_web_search
)

# Keyword research
result = deepagent_keyword_research(
    domain="example.com",
    niche="Digital Marketing",
    country="Nederland",
    language="Dutch",
    num_keywords=150
)

# Content planning
plan = deepagent_content_planning(
    keywords_data=keywords_text,
    domain="example.com",
    niche="Digital Marketing",
    num_articles=10,
    posting_schedule="weekly"
)
```

---

## 📊 Database Schema

```sql
CREATE TABLE websites (
    -- Existing fields
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL DEFAULT 1,
    
    -- Scheduling
    posting_schedule TEXT DEFAULT "weekly",
    posting_days TEXT,
    posting_time TEXT DEFAULT "09:00",
    auto_publish INTEGER DEFAULT 0,
    last_post_date TEXT,
    
    -- WordPress
    wordpress_url TEXT,
    wordpress_username TEXT,
    wordpress_password TEXT,
    
    -- NEW: Website Management
    niche TEXT,
    target_audience TEXT,
    tone_of_voice TEXT DEFAULT 'professional',
    context TEXT,
    knowledgebase TEXT,
    external_links TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP
);
```

---

## ✅ Migratie

De database wordt automatisch gemigreerd bij het draaien van:

```bash
python3 migrate_website_management.py
```

**Output:**
```
✓ Added column: niche
✓ Added column: target_audience
✓ Added column: tone_of_voice
✓ Added column: context
✓ Added column: knowledgebase
✓ Added column: external_links

✓ Migration completed successfully!
```

---

## 🎯 Benefits

### Voor Gebruikers:
- ✅ **Meer controle** over website instellingen
- ✅ **Betere content** door context en knowledgebase
- ✅ **Externe links** automatisch in artikelen
- ✅ **Alles op één plek** - geen zoeken meer
- ✅ **Intuïtieve interface** met tabs en helpers

### Voor Content Kwaliteit:
- ✅ **Relevantere keywords** door DeepAgent
- ✅ **Betere content planning** met AI
- ✅ **Context-aware** content generatie
- ✅ **Consistent tone of voice**
- ✅ **Doelgroep-specifieke** content

### Voor Automation:
- ✅ **WordPress integratie** centraal beheerd
- ✅ **Flexibele planning** opties
- ✅ **Auto-publish** per website instelbaar
- ✅ **Externe links** automatisch verwerkt

---

## 🔮 Toekomstige Uitbreidingen

Mogelijke features:
- 📊 Analytics integratie
- 🎨 Template management per website
- 🔍 SEO score tracking
- 📱 Social media integratie
- 🤖 A/B testing voor titles
- 📈 Performance metrics per website

---

## 📝 Notities

- Database migratie is backwards compatible
- Bestaande websites krijgen default waarden
- OpenAI fallback voor DeepAgent (als API key beschikbaar)
- Alle nieuwe velden zijn optioneel
- UI is volledig responsive

---

## 🐛 Known Issues

Geen bekende issues op dit moment.

---

## 👨‍💻 Auteur

DeepAgent by Abacus.AI
Implementatie: 10 Oktober 2025

---

## 📞 Support

Voor vragen of problemen, zie de hoofddocumentatie of neem contact op met het development team.
