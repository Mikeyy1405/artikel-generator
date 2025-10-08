
"""
Test script voor Pixabay API integratie
"""

from pixabay_api import PixabayAPI, search_pixabay_images, search_pixabay_videos
import os


def test_pixabay_integration():
    """Test de Pixabay API integratie"""
    
    # Haal API key op
    api_key = "21915564-045cceaec9b477dd17642057e"
    
    if not api_key:
        print("❌ Geen Pixabay API key gevonden")
        return False
    
    print("=" * 60)
    print("🧪 PIXABAY API INTEGRATIE TEST")
    print("=" * 60)
    
    # Test 1: Initialisatie
    print("\n📋 Test 1: API Client Initialisatie")
    try:
        client = PixabayAPI(api_key)
        print("✅ Client succesvol geïnitialiseerd")
    except Exception as e:
        print(f"❌ Fout bij initialisatie: {e}")
        return False
    
    # Test 2: Zoek afbeeldingen
    print("\n📋 Test 2: Zoek Afbeeldingen")
    result = client.search_images(
        query="yoga",
        per_page=3,
        image_type="photo",
        orientation="horizontal"
    )
    
    if result['success']:
        print(f"✅ {result['data']['count']} afbeeldingen gevonden")
        if result['data']['hits']:
            img = result['data']['hits'][0]
            print(f"   - Eerste afbeelding ID: {img['id']}")
            print(f"   - Tags: {img['tags']}")
            print(f"   - Preview URL: {img['previewURL'][:50]}...")
            print(f"   - Large URL: {img['largeImageURL'][:50]}...")
    else:
        print(f"❌ Fout: {result['error']}")
        return False
    
    # Test 3: Zoek video's
    print("\n📋 Test 3: Zoek Video's")
    result = client.search_videos(
        query="nature",
        per_page=2,
        video_type="film"
    )
    
    if result['success']:
        print(f"✅ {result['data']['count']} video's gevonden")
        if result['data']['hits']:
            vid = result['data']['hits'][0]
            print(f"   - Eerste video ID: {vid['id']}")
            print(f"   - Tags: {vid['tags']}")
            print(f"   - Duur: {vid['duration']} seconden")
            print(f"   - Medium URL: {vid['videos']['medium']['url'][:50]}...")
    else:
        print(f"❌ Fout: {result['error']}")
        return False
    
    # Test 4: Convenience functies
    print("\n📋 Test 4: Convenience Functies")
    images = search_pixabay_images(api_key, "cat", per_page=2)
    if images:
        print(f"✅ {len(images)} afbeeldingen via convenience functie")
    else:
        print("❌ Geen afbeeldingen gevonden")
        return False
    
    videos = search_pixabay_videos(api_key, "ocean", per_page=2)
    if videos:
        print(f"✅ {len(videos)} video's via convenience functie")
    else:
        print("❌ Geen video's gevonden")
        return False
    
    # Test 5: Error handling - ongeldige query
    print("\n📋 Test 5: Error Handling")
    result = client.search_images(query="x" * 101)  # Te lang
    if not result['success']:
        print(f"✅ Error correct afgehandeld: {result['error']}")
    else:
        print("❌ Error handling werkt niet correct")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALLE TESTS GESLAAGD!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_pixabay_integration()
    exit(0 if success else 1)
