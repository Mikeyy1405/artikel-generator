# Changelog - Writgo Academy v13

## Version 13.0.0 - October 2025

### 🎉 Major Features

#### 1. Extra Elementen Systeem
Volledig nieuw systeem voor het toevoegen van extra elementen aan artikelen:

**Nieuwe Opties:**
- 📊 **Tabellen** - Automatisch relevante tabellen genereren
- ❓ **FAQ Secties** - 5+ veelgestelde vragen met antwoorden
- 💪 **Bold Tekst** - Automatisch belangrijke termen benadrukken
- 📺 **YouTube Videos** - Video suggesties toevoegen
- 📸 **Pixabay Afbeeldingen** - 0-5 gratis stockfoto's
- 🎨 **DALL-E Afbeeldingen** - 0-3 AI-gegenereerde afbeeldingen

#### 2. Pixabay API Integratie
Volledige integratie met Pixabay voor gratis stockfoto's:

**Features:**
- Automatische zoekterm vertaling naar Engels
- 4.5+ miljoen afbeeldingen beschikbaar
- Meerdere formaten (preview, small, medium, full)
- Gratis voor commercieel gebruik
- 5,000 requests per maand (gratis tier)

**Nieuwe Functies:**
```python
search_pixabay_images(query, per_page, image_type, orientation)
process_article_placeholders(article, onderwerp, elements)
```

**Nieuw API Endpoint:**
```
POST /api/search-images
```

#### 3. DALL-E 3 Integratie
AI-gegenereerde afbeeldingen direct in artikelen:

**Features:**
- 5 verschillende stijlen:
  - Realistic Photo
  - Digital Art
  - Illustration
  - 3D Render
  - Minimalist
- Automatische prompt generatie
- Direct in artikel geplaatst
- $0.040 per afbeelding

#### 4. Vereenvoudigde Model Selectie
Alleen de beste GPT modellen behouden:

**Voor:**
- 13 verschillende modellen
- Verwarrende namen (mini, nano, codex, etc.)
- Onduidelijke verschillen

**Nu:**
- ✅ GPT-5 (Nieuwste & Beste)
- ✅ GPT-4.1 (Verbeterd)
- ✅ GPT-4.0 (Stabiel)

Clean, duidelijk, professioneel.

### 🔧 Technical Changes

#### Backend (app.py)

**Nieuwe Functies:**
```python
def process_article_placeholders(article, onderwerp, elements):
    """
    Verwerkt placeholders in artikel:
    - [IMAGE: description] -> Pixabay
    - [AI-IMAGE: description] -> DALL-E
    - [YOUTUBE: search term] -> YouTube
    """

def search_pixabay_images(query, per_page=10, image_type='photo', orientation='horizontal'):
    """Zoekt afbeeldingen op Pixabay"""

def generate_general_article(..., elements=None):
    """Nu met elements parameter voor extra functionaliteit"""
```

**Updated Functies:**
- `generate_general_article()` - Nieuwe `elements` parameter
- `GENERAL_ARTICLE_PROMPT` - Nieuwe `{extra_elements}` placeholder
- `/api/generate-general-article` - Nieuwe request parameters

**Nieuwe Environment Variables:**
```bash
PIXABAY_API_KEY=...  # Nieuw in v13
```

#### Frontend (index.html)

**Nieuwe UI Elementen:**
```html
<!-- Extra Elementen Sectie -->
<div class="form-group">
    <label>📋 Extra Elementen (Optioneel)</label>
    <!-- Checkboxes voor table, FAQ, bold, YouTube -->
</div>

<!-- Pixabay Afbeeldingen -->
<div class="form-group">
    <label>📸 Pixabay Afbeeldingen (Automatisch)</label>
    <input type="number" id="pixabay-images" min="0" max="5">
</div>

<!-- DALL-E Afbeeldingen -->
<div class="form-group">
    <label>🎨 AI Gegenereerde Afbeeldingen (DALL-E)</label>
    <input type="number" id="dalle-images" min="0" max="3">
    <select id="dalle-style">
        <!-- 5 stijl opties -->
    </select>
</div>
```

**Updated JavaScript:**
```javascript
async function generateGeneralArticle() {
    // Nieuwe parameters
    const include_table = document.getElementById('include-table').checked;
    const include_faq = document.getElementById('include-faq').checked;
    const include_bold = document.getElementById('include-bold').checked;
    const youtube_video = document.getElementById('youtube-video').checked;
    const pixabay_images = parseInt(document.getElementById('pixabay-images').value);
    const dalle_images = parseInt(document.getElementById('dalle-images').value);
    const dalle_style = document.getElementById('dalle-style').value;
    
    // Payload met alle nieuwe velden
    const payload = { 
        onderwerp, word_count, extra, model,
        include_table, include_faq, include_bold, youtube_video,
        pixabay_images, dalle_images, dalle_style
    };
}
```

### 📝 Prompt Engineering

**Nieuwe Prompt Instructies:**

Voor **Tabellen**:
```
TABEL VEREIST:
✅ Voeg 1 relevante tabel toe in het artikel
✅ Gebruik HTML table format: <table>, <tr>, <th>, <td>
✅ Minimaal 3 rijen en 2 kolommen
```

Voor **FAQ**:
```
FAQ SECTIE VEREIST:
✅ Voeg een FAQ sectie toe met minimaal 5 vragen
✅ Gebruik H2: Veelgestelde Vragen
✅ Elke vraag als H3: [vraag]
```

Voor **Pixabay Afbeeldingen**:
```
AFBEELDING PLACEHOLDERS VEREIST:
✅ Voeg {num} afbeelding placeholder(s) toe
✅ Gebruik format: [IMAGE: beschrijving in het Engels]
✅ Bijvoorbeeld: [IMAGE: yoga mat exercises morning routine]
✅ Beschrijvingen moeten SPECIFIEK en in ENGELS zijn
```

Voor **DALL-E Afbeeldingen**:
```
AI AFBEELDING PLACEHOLDERS VEREIST:
✅ Voeg {num} AI afbeelding placeholder(s) toe
✅ Gebruik format: [AI-IMAGE: gedetailleerde beschrijving in het Engels]
✅ Stijl: {style}
✅ Beschrijvingen moeten ZEER GEDETAILLEERD zijn
```

Voor **YouTube**:
```
YOUTUBE VIDEO PLACEHOLDER VEREIST:
✅ Voeg 1 YouTube video placeholder toe
✅ Gebruik format: [YOUTUBE: zoekterm in het Engels]
✅ Bijvoorbeeld: [YOUTUBE: best yoga exercises for beginners]
```

### 🎨 UI/UX Improvements

**Model Selectie:**
- Verwijderd: 10 oude/verwarrende modellen
- Behouden: 3 duidelijke opties
- Cleaner dropdown interface

**Extra Elementen:**
- Nieuwe sectie met duidelijke labels
- Grid layout voor checkboxes
- Number inputs voor afbeeldingen
- Dropdown voor DALL-E stijlen
- Helpful hints en tooltips

**Visuele Verbeteringen:**
- Emoji icons voor betere scanability
- Gegroepeerde form elementen
- Duidelijke cost warnings (DALL-E)
- Informative placeholders

### 📊 API Changes

#### New Endpoint Parameters

**POST /api/generate-general-article**

Nieuwe parameters:
```json
{
  "onderwerp": "string",
  "word_count": 1000,
  "extra": "string",
  "model": "gpt-5",
  
  // NIEUW in v13
  "include_table": true,
  "include_faq": true,
  "include_bold": true,
  "youtube_video": true,
  "pixabay_images": 3,
  "dalle_images": 2,
  "dalle_style": "realistic photo"
}
```

**POST /api/search-images** (Nieuw)

Request:
```json
{
  "query": "yoga exercises",
  "per_page": 10,
  "image_type": "photo",
  "orientation": "horizontal"
}
```

Response:
```json
{
  "success": true,
  "total": 10,
  "images": [
    {
      "id": 1234567,
      "preview_url": "...",
      "small_url": "...",
      "medium_url": "...",
      "full_url": "...",
      "width": 1920,
      "height": 1280,
      "tags": "yoga, meditation, fitness",
      "user": "photographer_name",
      "page_url": "..."
    }
  ]
}
```

### 🔒 Security & Performance

**API Key Management:**
- Nieuwe environment variable: `PIXABAY_API_KEY`
- Veilige opslag in environment
- Geen hardcoded keys

**Rate Limiting:**
- Pixabay: 5,000 requests/maand (gratis)
- Pixabay: 100 requests/minuut
- Automatische error handling

**Error Handling:**
- Graceful fallback bij missing images
- Duidelijke error messages
- Placeholder removal bij failures

### 📚 Documentation

**Nieuwe Documenten:**
- `PIXABAY_SETUP.md` - Complete Pixabay setup gids
- `README_V13.md` - Volledige v13 documentatie
- `CHANGELOG_V13.md` - Dit bestand

**Updated Documenten:**
- `requirements.txt` - Geen nieuwe dependencies
- `runtime.txt` - Python 3.11 (unchanged)

### 🐛 Bug Fixes

- ✅ Fixed: Model dropdown overflow
- ✅ Fixed: Placeholder processing order
- ✅ Fixed: Image URL escaping in HTML
- ✅ Fixed: YouTube embed formatting
- ✅ Fixed: Table HTML generation

### ⚠️ Breaking Changes

**Model Names:**
- Verwijderd: `gpt-5-mini`, `gpt-5-nano`, `gpt-5-chat-latest`, `gpt-5-codex`, `gpt-5-pro`
- Verwijderd: `gpt-4.1-mini`, `gpt-4.1-nano`
- Verwijderd: `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`

**Migratie:**
- Oude model namen worden automatisch gemapped naar `gpt-4o`
- Geen actie vereist voor bestaande code

### 💰 Cost Impact

**Nieuwe Kosten:**
- Pixabay: **GRATIS** (5,000/maand)
- DALL-E 3: $0.040 per afbeelding

**Voorbeeld Scenario's:**

1. **Artikel met 3 Pixabay afbeeldingen:**
   - GPT-5: ~$0.02
   - Pixabay: $0.00
   - **Totaal: ~$0.02** ✅

2. **Artikel met 2 DALL-E afbeeldingen:**
   - GPT-5: ~$0.02
   - DALL-E: $0.08
   - **Totaal: ~$0.10** 💰

3. **Uitgebreid artikel (alles):**
   - GPT-5: ~$0.03
   - Pixabay (3): $0.00
   - DALL-E (2): $0.08
   - **Totaal: ~$0.11** 💰

### 🎯 Use Cases

**Blog Posts:**
```
✅ FAQ Sectie
✅ Bold Tekst
📸 2-3 Pixabay afbeeldingen
📺 YouTube video
```

**Product Reviews:**
```
✅ Tabel (specificaties)
✅ Bold Tekst
📸 3-4 Pixabay afbeeldingen
```

**Creative Content:**
```
✅ Bold Tekst
🎨 2-3 DALL-E afbeeldingen (Digital Art)
📺 YouTube video
```

**Educational Content:**
```
✅ Tabel
✅ FAQ Sectie
✅ Bold Tekst
📸 4-5 Pixabay afbeeldingen
```

### 🚀 Performance

**Image Loading:**
- Pixabay API: ~200-500ms per request
- DALL-E 3: ~10-15 seconds per image
- Parallel processing waar mogelijk

**Article Generation:**
- Zonder afbeeldingen: 5-10 seconds
- Met Pixabay (3): 7-12 seconds
- Met DALL-E (2): 25-35 seconds

### 📈 Future Improvements

**Planned for v14:**
- [ ] Unsplash API integratie
- [ ] Pexels API integratie
- [ ] Image caching systeem
- [ ] Bulk article generation
- [ ] Custom image upload
- [ ] Video embedding (niet alleen suggesties)
- [ ] Interactive charts/graphs
- [ ] Audio content integration

### 🙏 Credits

**APIs Used:**
- OpenAI GPT-5, GPT-4.1, GPT-4.0
- OpenAI DALL-E 3
- Pixabay API
- Originality.AI

**Libraries:**
- Flask
- OpenAI Python SDK
- Requests
- SQLite3

---

## Migration Guide v12 → v13

### 1. Update Environment Variables

```bash
# Add to .env
PIXABAY_API_KEY=your_pixabay_key_here
```

### 2. Update Code (if using API directly)

**Old:**
```python
article = generate_general_article(onderwerp, word_count, extra, model)
```

**New:**
```python
elements = {
    'include_table': True,
    'pixabay_images': 3
}
article = generate_general_article(onderwerp, word_count, extra, model, elements)
```

### 3. Update Frontend (if custom)

Add new form fields for extra elements (see index.html for examples)

### 4. Test

1. Test linkbuilding (should work unchanged)
2. Test general articles without elements (should work unchanged)
3. Test general articles with elements (new functionality)
4. Test Pixabay integration
5. Test DALL-E integration

---

**Version:** 13.0.0  
**Release Date:** October 7, 2025  
**Status:** ✅ Stable  
**Compatibility:** Python 3.11+

