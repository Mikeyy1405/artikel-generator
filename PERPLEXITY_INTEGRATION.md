# WritgoAI v16 - Perplexity AI Integration 🔍

## Nieuwe Features

### 🌟 Perplexity AI Research
WritgoAI v16 integreert **Perplexity AI** voor automatisch online onderzoek voordat content wordt gegenereerd.

#### Wat doet het?
1. **🔍 Zoekt top Google resultaten** - Analyseert de beste content online
2. **📊 Verzamelt actuele informatie** - Gebruikt real-time web data
3. **🎯 Identificeert key points** - Vindt belangrijke onderwerpen om te behandelen
4. **🔗 Voegt bronnen toe** - Automatische bronvermelding in artikel
5. **✨ Schrijft betere content** - Gebruikt research als basis voor superieure artikelen

#### Hoe werkt het?
- **Toggle in UI**: Checkbox "🔍 Gebruik Perplexity AI Research"
- **Automatisch proces**: 
  1. Perplexity zoekt en analyseert top content
  2. Extraheert belangrijkste punten en trends
  3. Geeft deze context aan je AI model
  4. AI schrijft beter artikel met actuele info
  5. Bronnen worden automatisch toegevoegd

#### Voordelen
✅ **Betere content dan concurrenten** - Gebaseerd op analyse van beste artikelen
✅ **Actuele informatie** - Real-time web search
✅ **Diepgaander** - Meer context en details
✅ **Bronvermelding** - Automatisch toegevoegd
✅ **SEO-vriendelijk** - Behandelt alle belangrijke aspecten

## Technische Details

### API Integratie
- **Model**: `llama-3.1-sonar-large-128k-online`
- **Endpoint**: `https://api.perplexity.ai/chat/completions`
- **Features**: 
  - Real-time web search
  - Citation tracking
  - Recency filter (laatste maand)
  - Temperature: 0.2 (accurate results)

### Code Changes

#### Backend (app.py)
1. **Nieuwe functie**: `perplexity_research(topic, num_results=5)`
   - Voert research uit via Perplexity API
   - Retourneert summary, sources, key_points
   - Error handling voor timeouts en API errors

2. **Updated functie**: `generate_general_article(..., use_research=False)`
   - Nieuwe parameter: `use_research`
   - Voegt research context toe aan prompt
   - Integreert bronnen in artikel

3. **API endpoint**: `/api/generate-general-article`
   - Accepteert `use_research` parameter
   - Geeft research status door aan frontend

#### Frontend (index.html)
1. **Nieuwe UI element**: Research toggle checkbox
   - Prominent geplaatst met gradient background
   - Duidelijke uitleg van voordelen
   - Visual feedback tijdens research

2. **Updated JavaScript**: `generateGeneralArticle()`
   - Leest research toggle status
   - Toont research progress indicator
   - Stuurt parameter naar backend

### Environment Variables

Voor **Render deployment**, voeg toe:
```
PERPLEXITY_API_KEY=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
```

Voor **lokale development**, API key staat al in:
```
/home/ubuntu/.config/abacusai_auth_secrets.json
```

## Gebruik

### In de UI
1. Ga naar "Algemene Content Schrijver"
2. Vul onderwerp in
3. ✅ **Vink aan**: "🔍 Gebruik Perplexity AI Research"
4. Klik "🚀 Genereer Artikel"
5. Wacht 10-20 seconden voor research + generatie
6. Ontvang artikel met actuele info en bronnen

### Aanbevolen Settings
- **Research**: ✅ AAN (voor beste resultaten)
- **Model**: GPT-5 of Claude Sonnet 4
- **Word count**: 1000+ (voor diepgaande content)
- **Extra elements**: FAQ, Bold, Afbeeldingen

## Kosten

### Perplexity API Pricing
- **Model**: Sonar Large (128K context)
- **Kosten**: ~$0.001 per request
- **Zeer goedkoop** vergeleken met waarde

### Vergelijking
- Google Custom Search API: $5 per 1000 queries
- Perplexity: $1 per 1000 queries + betere resultaten
- **ROI**: Veel beter dan handmatig research doen

## Testing

### Lokaal testen
```bash
cd /home/ubuntu/writgo_app_v16_perplexity
python3 app.py
```

### Test scenario's
1. **Met research**: Onderwerp "yoga voor beginners"
   - Verwacht: Actuele tips, trends, bronnen
   
2. **Zonder research**: Zelfde onderwerp
   - Vergelijk: Diepgang en actualiteit

3. **Complexe onderwerpen**: "AI in gezondheidszorg 2025"
   - Test: Actualiteit van informatie

## Deployment naar Render

### Stap 1: Update Environment Variables
In Render dashboard, voeg toe:
```
PERPLEXITY_API_KEY=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
```

### Stap 2: Deploy nieuwe versie
```bash
# Zip de nieuwe versie
cd /home/ubuntu
zip -r writgoai_v16_perplexity.zip writgo_app_v16_perplexity/

# Upload naar GitHub
# Deploy via Render
```

### Stap 3: Verificatie
1. Check logs voor: "✅ Perplexity API key loaded"
2. Test research functie in UI
3. Controleer of bronnen worden toegevoegd

## Troubleshooting

### "Perplexity API key not configured"
- Check environment variable in Render
- Verify secrets file lokaal
- Restart app

### "Research timeout"
- Normaal bij complexe queries
- Verhoog timeout in code (nu 30s)
- Probeer opnieuw

### "No sources returned"
- Perplexity vond geen relevante bronnen
- Probeer specifieker onderwerp
- Check API quota

## Changelog v16

### ✨ Nieuw
- Perplexity AI research integratie
- Automatische bronvermelding
- Research toggle in UI
- Real-time web search capability

### 🔧 Verbeterd
- Betere content kwaliteit door research
- Actuele informatie in artikelen
- Diepgaandere behandeling van onderwerpen

### 📝 Documentatie
- PERPLEXITY_INTEGRATION.md toegevoegd
- API documentatie
- Deployment instructies

## Volgende Stappen

### Mogelijke uitbreidingen
1. **Research rapport** - Toon research resultaten apart
2. **Concurrent analyse** - Vergelijk met top 3 artikelen
3. **Keyword research** - Integreer SEO keywords
4. **Fact checking** - Verify claims met Perplexity
5. **Multi-language** - Research in andere talen

---

**Versie**: v16  
**Datum**: 7 oktober 2025  
**Status**: ✅ Production Ready
