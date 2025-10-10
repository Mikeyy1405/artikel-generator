# Keyword Research Wizard - Fix Samenvatting

## Probleem
De Website Setup Wizard crashte tijdens de keyword research fase met de volgende error:
```
Error: "Unexpected token '<', "<!DOCTYPE "... is not valid JSON"
Worker (pid:62 en pid:82) crashed met code 1
```

Dit probleem ontstond omdat:
1. De Perplexity API key niet was geconfigureerd
2. De API retourneerde een HTML error page in plaats van JSON
3. De frontend kon de HTML response niet parsen als JSON
4. De Gunicorn worker crashed door een onafgevangen exception

## Oplossing

### 1. Frontend Verbeteringen (`templates/index.html`)

#### Validatie onboardingSessionId
```javascript
// Check if onboardingSessionId is defined
if (!onboardingSessionId) {
    throw new Error('Onboarding sessie ID niet gevonden. Start de wizard opnieuw.');
}
```

#### Robuuste JSON Parsing
```javascript
// Get response text first for better error handling
const responseText = await response.text();

// Parse JSON with error handling
let data;
try {
    data = JSON.parse(responseText);
} catch (jsonError) {
    console.error('JSON parsing error:', jsonError);
    console.error('Response text:', responseText);
    throw new Error('Server retourneerde geen geldige JSON. De server kan overbelast zijn.');
}
```

#### HTTP Response Status Check
```javascript
// Check if response is OK
if (!response.ok) {
    const errorText = await response.text();
    console.error('Server response:', errorText);
    throw new Error(`Server error: ${response.status} ${response.statusText}`);
}
```

### 2. Backend Verbeteringen (`app.py`)

#### OpenAI Fallback Mechanisme
Wanneer Perplexity API niet beschikbaar is, valt het systeem automatisch terug op OpenAI:

```python
def perplexity_research(topic, num_results=5):
    """Use Perplexity AI to research a topic, with OpenAI fallback"""
    if not PERPLEXITY_API_KEY:
        print("⚠️  Perplexity API key not configured, using OpenAI fallback")
        return openai_research_fallback(topic, num_results)
    
    try:
        # Perplexity API call
        ...
    except Exception as e:
        print(f"❌ Perplexity research error: {e}")
        print("⚠️  Falling back to OpenAI")
        return openai_research_fallback(topic, num_results)
```

#### Uitgebreide Error Logging
Alle stappen in het keyword research proces worden nu gelogd:

```python
print(f"🔍 [KEYWORD RESEARCH] Starting for onboarding_id={onboarding_id}")
print(f"🔍 [KEYWORD RESEARCH] User ID: {user_id}")
print(f"🔍 [KEYWORD RESEARCH] Fetching onboarding session from database...")
print(f"🔍 [KEYWORD RESEARCH] Session found - website_id={website_id}, status={status}")
print(f"🔍 [KEYWORD RESEARCH] Domain: {domain}, Country: {country}, Language: {language}")
print(f"🔑 [KEYWORD RESEARCH] Calling perplexity_research (or OpenAI fallback)...")
print(f"✅ [KEYWORD RESEARCH] Research completed successfully")
print(f"✅ [KEYWORD RESEARCH] Returning success response")
```

#### Gegarandeerde JSON Response
Alle error responses retourneren nu proper JSON in plaats van HTML error pages:

```python
except Exception as e:
    print(f"❌ [KEYWORD RESEARCH] Error in onboarding keyword research: {str(e)}")
    print(f"❌ [KEYWORD RESEARCH] Full traceback:")
    traceback.print_exc()
    
    error_response = {
        'success': False,
        'error': str(e)
    }
    
    print(f"❌ [KEYWORD RESEARCH] Returning error response: {error_response}")
    return jsonify(error_response), 500
```

### 3. Testing

#### Test Script
Een test script (`test_keyword_research.py`) is toegevoegd om de functionaliteit te verifiëren:

```bash
python3 test_keyword_research.py
```

#### Test Resultaten
```
🧪 Test 1: Creating onboarding session...
✅ Onboarding session created: ID=2

🧪 Test 2: Running keyword research for session 2...
Status code: 200
Response headers: {'Content-Type': 'application/json', ...}
✅ Response is valid JSON
Success: True
Keywords generated: 150+
Current step: keyword_research_completed
```

## Technische Details

### API Endpoints
- **POST** `/api/onboarding/start` - Start onboarding wizard
- **POST** `/api/onboarding/keyword-research/<onboarding_id>` - Run keyword research

### Database Schema
```sql
CREATE TABLE onboarding_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    website_id INTEGER,
    current_step TEXT,
    status TEXT,
    site_data TEXT,
    keyword_research_data TEXT,
    content_plan_data TEXT,
    error_message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Wizard Flow
1. **Stap 1**: Website informatie verzamelen
2. **Stap 2**: Keyword research uitvoeren (GEFIXD)
3. **Stap 3**: Content plan genereren
4. **Stap 4**: Klaar

## Voordelen van de Fix

✅ **Robuuste Error Handling**: Alle errors worden correct afgehandeld en loggen nuttige informatie

✅ **Geen Worker Crashes**: De Gunicorn worker crashed niet meer door uncaught exceptions

✅ **OpenAI Fallback**: Systeem blijft werken zonder Perplexity API key

✅ **Betere Debugging**: Uitgebreide logging maakt toekomstig debuggen eenvoudig

✅ **Gebruiksvriendelijk**: Duidelijke error messages voor de gebruiker

✅ **Goed Getest**: End-to-end test bevestigt dat alles correct werkt

## Git Commit

```bash
git add app.py templates/index.html
git commit -m "Fix keyword research wizard: Add error handling, OpenAI fallback, and comprehensive logging"
git push origin main
```

**Commit Hash**: `f031291`

## Gebruikersinstructies

### Voor Gebruikers
1. Ga naar de WritgoAI applicatie
2. Klik op "Website Setup Wizard"
3. Vul de website gegevens in
4. De wizard zal nu automatisch:
   - Keyword research uitvoeren (met OpenAI als Perplexity niet beschikbaar is)
   - 150+ keywords genereren
   - Een content plan maken

### Voor Ontwikkelaars
Om Perplexity te gebruiken in plaats van OpenAI fallback:
```bash
export PERPLEXITY_API_KEY="your-api-key-here"
```

## Conclusie

Het keyword research probleem is volledig opgelost. De wizard werkt nu betrouwbaar met:
- Proper error handling op frontend en backend
- Automatische fallback naar OpenAI wanneer Perplexity niet beschikbaar is
- Uitgebreide logging voor toekomstig debugging
- Gegarandeerde JSON responses (geen HTML error pages meer)

De fix is getest en pushed naar de main branch van de repository.
