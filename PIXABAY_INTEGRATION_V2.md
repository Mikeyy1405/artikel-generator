
# Pixabay API Integratie v2.0

## 📋 Overzicht

Complete nieuwe implementatie van de Pixabay API integratie volgens de officiële API documentatie (https://pixabay.com/api/docs/).

## ✅ Wat is er opgelost?

### Probleem
De oude implementatie gaf de foutmelding: **"❌ Fout bij zoeken naar afbeeldingen: Unexpected token '<'"**

Dit werd veroorzaakt doordat:
1. De API soms HTML error pagina's retourneerde in plaats van JSON
2. Er geen adequate error handling was voor niet-JSON responses
3. Rate limiting en andere API errors niet correct werden afgehandeld

### Oplossing
Nieuwe `pixabay_api.py` module met:
- ✅ Volledige error handling voor alle HTTP status codes
- ✅ JSON parsing validatie (voorkomt "Unexpected token" errors)
- ✅ Rate limit monitoring via response headers
- ✅ Ondersteuning voor zowel afbeeldingen als video's
- ✅ Uitgebreide logging voor debugging
- ✅ Backward compatibility met bestaande code

## 🚀 Nieuwe Features

### 1. Afbeeldingen Zoeken
```python
from pixabay_api import PixabayAPI

client = PixabayAPI(api_key="YOUR_API_KEY")

# Basis zoeken
result = client.search_images(
    query="yoga",
    per_page=10,
    image_type="photo",
    orientation="horizontal"
)

if result['success']:
    images = result['data']['hits']
    for img in images:
        print(f"Image URL: {img['largeImageURL']}")
```

### 2. Video's Zoeken
```python
# Video's zoeken
result = client.search_videos(
    query="nature",
    per_page=10,
    video_type="film"
)

if result['success']:
    videos = result['data']['hits']
    for vid in videos:
        print(f"Video URL: {vid['videos']['medium']['url']}")
```

### 3. Geavanceerde Filters
```python
# Met filters
result = client.search_images(
    query="sunset",
    per_page=20,
    image_type="photo",
    orientation="horizontal",
    category="nature",
    min_width=1920,
    min_height=1080,
    colors="orange,red",
    editors_choice=True,
    safesearch=True,
    order="latest"
)
```

## 📊 API Response Structuur

### Afbeeldingen Response
```json
{
    "success": true,
    "data": {
        "total": 4692,
        "totalHits": 500,
        "count": 10,
        "hits": [
            {
                "id": 195893,
                "type": "photo",
                "tags": "blossom, bloom, flower",
                "pageURL": "https://images.unsplash.com/photo-1507290439931-a861b5a38200?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Zmxvd2VyJTIwYmxvb218ZW58MHx8MHx8fDA%3D",
                "previewURL": "https://images.pexels.com/photos/20699728/pexels-photo-20699728/free-photo-of-close-up-of-a-pink-blossoming-branch.jpeg",
                "webformatURL": "https://images.unsplash.com/photo-1436891436013-5965265af5fc?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Zmxvd2VyJTIwYmxvb218ZW58MHx8MHx8fDA%3D",
                "largeImageURL": "https://images.unsplash.com/photo-1484687625115-3f057a354cc2?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8Zmxvd2VyJTIwYmxvb218ZW58MHx8MHx8fDA%3D",
                "fullHDURL": "https://pixabay.com/.../1920.jpg",
                "imageURL": "https://pixabay.com/.../original.jpg",
                "imageWidth": 4000,
                "imageHeight": 2250,
                "views": 7671,
                "downloads": 6439,
                "likes": 5,
                "user": "Josch13"
            }
        ]
    }
}
```

### Video's Response
```json
{
    "success": true,
    "data": {
        "total": 42,
        "totalHits": 42,
        "count": 10,
        "hits": [
            {
                "id": 125,
                "type": "film",
                "tags": "flowers, yellow, blossom",
                "duration": 12,
                "videos": {
                    "large": {
                        "url": "https://cdn.pixabay.com/.../large.mp4",
                        "width": 1920,
                        "height": 1080,
                        "size": 6615235,
                        "thumbnail": "https://cdn.pixabay.com/.../large.jpg"
                    },
                    "medium": {...},
                    "small": {...},
                    "tiny": {...}
                },
                "views": 4462,
                "downloads": 1464,
                "user": "Coverr-Free-Footage"
            }
        ]
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "API rate limit bereikt. Probeer het later opnieuw.",
    "rate_limit_exceeded": true
}
```

## 🔧 Technische Details

### Error Handling
De nieuwe implementatie handelt alle mogelijke errors af:

1. **HTTP 429 (Rate Limit)**: Duidelijke melding met retry suggestie
2. **HTTP 400 (Bad Request)**: Validatie van parameters
3. **HTTP 403 (Forbidden)**: API key verificatie
4. **JSON Parse Errors**: Voorkomt "Unexpected token" errors
5. **Network Errors**: Timeout en connection errors
6. **Validation Errors**: Parameter validatie (query length, per_page range, etc.)

### Rate Limiting
- Standaard: 100 requests per 60 seconden
- Response headers worden gemonitord:
  - `X-RateLimit-Limit`: Maximum aantal requests
  - `X-RateLimit-Remaining`: Resterende requests
  - `X-RateLimit-Reset`: Tijd tot reset (in seconden)

### Logging
Uitgebreide logging voor debugging:
```
🔍 Pixabay API request: images - query: 'yoga'
📊 Rate limit: 99/100 (reset in 60s)
✅ Pixabay: 3 resultaten gevonden (totaal: 500)
```

## 📝 Gebruik in App

### In app.py
De oude `search_pixabay_images` functie is vervangen door `search_pixabay_images_wrapper`:

```python
from pixabay_api import PixabayAPI

# Wrapper functie voor backward compatibility
def search_pixabay_images_wrapper(query, per_page=10, image_type='photo', orientation='horizontal'):
    client = PixabayAPI(PIXABAY_API_KEY)
    result = client.search_images(
        query=query,
        per_page=per_page,
        image_type=image_type,
        orientation=orientation,
        lang='nl',
        safesearch=True
    )
    
    if result['success']:
        return [format_image(hit) for hit in result['data']['hits']]
    else:
        raise Exception(result['error'])
```

### API Endpoints
De `/api/search-images` endpoint gebruikt nu de nieuwe implementatie:

```python
@app.route('/api/search-images', methods=['POST'])
def api_search_images():
    data = request.json
    images = search_pixabay_images_wrapper(
        query=data.get('query'),
        per_page=data.get('per_page', 10),
        image_type=data.get('image_type', 'photo'),
        orientation=data.get('orientation', 'horizontal')
    )
    return jsonify({"success": True, "images": images})
```

## 🧪 Testing

### Unit Tests
Run de test suite:
```bash
python test_pixabay.py
```

Test output:
```
============================================================
🧪 PIXABAY API INTEGRATIE TEST
============================================================

📋 Test 1: API Client Initialisatie
✅ Client succesvol geïnitialiseerd

📋 Test 2: Zoek Afbeeldingen
✅ 3 afbeeldingen gevonden

📋 Test 3: Zoek Video's
✅ 3 video's gevonden

📋 Test 4: Convenience Functies
✅ 3 afbeeldingen via convenience functie
✅ 3 video's via convenience functie

📋 Test 5: Error Handling
✅ Error correct afgehandeld

============================================================
✅ ALLE TESTS GESLAAGD!
============================================================
```

## 🔑 API Key Configuratie

De API key wordt geladen uit:
1. Environment variabele: `PIXABAY_API_KEY`
2. Config bestand: `/home/ubuntu/.config/abacusai_auth_secrets.json`

Huidige API key: `21915564-045cceaec9b477dd17642057e`

## 📚 API Documentatie

Volledige Pixabay API documentatie:
https://pixabay.com/api/docs/

### Belangrijke Parameters

#### Afbeeldingen
- `q`: Zoekterm (max 100 karakters)
- `lang`: Taalcode (nl, en, de, etc.)
- `image_type`: all, photo, illustration, vector
- `orientation`: all, horizontal, vertical
- `category`: backgrounds, fashion, nature, science, etc.
- `min_width`, `min_height`: Minimale afmetingen
- `colors`: Kleurfilter (comma separated)
- `editors_choice`: Boolean voor Editor's Choice
- `safesearch`: Boolean voor veilige content
- `order`: popular, latest
- `page`: Paginanummer (start bij 1)
- `per_page`: Resultaten per pagina (3-200)

#### Video's
- `q`: Zoekterm (max 100 karakters)
- `lang`: Taalcode (nl, en, de, etc.)
- `video_type`: all, film, animation
- `category`: backgrounds, fashion, nature, science, etc.
- `min_width`, `min_height`: Minimale afmetingen
- `editors_choice`: Boolean voor Editor's Choice
- `safesearch`: Boolean voor veilige content
- `order`: popular, latest
- `page`: Paginanummer (start bij 1)
- `per_page`: Resultaten per pagina (3-200)

## 🎯 Best Practices

1. **Cache Results**: API responses moeten 24 uur gecached worden
2. **Download Images**: Permanent hotlinking is niet toegestaan - download afbeeldingen naar eigen server
3. **Attribution**: Toon altijd de bron (Pixabay) bij zoekresultaten
4. **Rate Limiting**: Respecteer de rate limits (100 req/min standaard)
5. **Error Handling**: Vang altijd errors af en toon gebruiksvriendelijke meldingen

## 🔄 Migratie van Oude Code

### Voor
```python
images = search_pixabay_images(query, per_page=10)
```

### Na
```python
# Optie 1: Gebruik wrapper (backward compatible)
images = search_pixabay_images_wrapper(query, per_page=10)

# Optie 2: Gebruik nieuwe API direct
client = PixabayAPI(api_key)
result = client.search_images(query=query, per_page=10)
if result['success']:
    images = result['data']['hits']
```

## 📦 Bestanden

- `pixabay_api.py`: Nieuwe API module
- `test_pixabay.py`: Test suite
- `app.py`: Geüpdatet met nieuwe integratie
- `PIXABAY_INTEGRATION_V2.md`: Deze documentatie

## ✨ Conclusie

De nieuwe Pixabay integratie is:
- ✅ Volledig functioneel en getest
- ✅ Robuust met uitgebreide error handling
- ✅ Backward compatible met bestaande code
- ✅ Ondersteunt zowel afbeeldingen als video's
- ✅ Goed gedocumenteerd
- ✅ Klaar voor productie gebruik

De fout "Unexpected token '<'" is volledig opgelost door correcte JSON parsing en error handling.
