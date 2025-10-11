
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Sparkles, Loader2, Check } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';

const PRESETS = [
  {
    id: 'scary-stories',
    name: 'Scary stories',
    description: 'Scary stories that give you goosebumps',
    formats: ['Storytelling'],
    emoji: '😱'
  },
  {
    id: 'history',
    name: 'History',
    description: 'Viral videos about history spanning from ancient times to the modern day.',
    formats: ['Storytelling', 'What if', '5 things you didn\'t know'],
    emoji: '🏛️'
  },
  {
    id: 'true-crime',
    name: 'True Crime',
    description: 'Viral videos about true crime stories.',
    formats: ['Storytelling'],
    emoji: '🔪'
  },
  {
    id: 'stoic-motivation',
    name: 'Stoic Motivation',
    description: 'Viral videos about stoic philosophy and life lessons.',
    formats: ['Storytelling', 'Random fact'],
    emoji: '🏛️'
  },
  {
    id: 'good-morals',
    name: 'Good morals',
    description: 'Viral videos that teach people good morals and life lessons.',
    formats: ['Storytelling'],
    emoji: '💡'
  },
];

const CUSTOM_FORMATS = [
  { id: 'storytelling', name: 'Storytelling', emoji: '📖' },
  { id: 'what-if', name: 'What if', emoji: '🤔' },
  { id: '5-things', name: '5 things you didn\'t know', emoji: '🔢' },
  { id: 'random-fact', name: 'Random fact', emoji: '💭' },
];

const ART_STYLES = [
  { id: 'comic', name: 'Comic', description: 'Levendige comic book stijl met dikke lijnen', preview: '/examples/comic.jpg' },
  { id: 'creepy-comic', name: 'Creepy Comic', description: 'Donkere horror comic met dramatische schaduwen', preview: '/examples/creepy-comic.jpg' },
  { id: 'painting', name: 'Painting', description: 'Klassieke schilderij stijl met rijke texturen', preview: '/examples/painting.jpg' },
  { id: 'ghibli', name: 'Studio Ghibli', description: 'Dromerige anime zoals Studio Ghibli films', preview: '/examples/ghibli.jpg' },
  { id: 'anime', name: 'Anime', description: 'Moderne anime met levendige kleuren', preview: '/examples/anime.jpg' },
  { id: 'dark-fantasy', name: 'Dark Fantasy', description: 'Mystieke fantasy met dramatische belichting', preview: '/examples/dark-fantasy.jpg' },
  { id: 'lego', name: 'LEGO', description: 'Gemaakt van LEGO blokjes met speelgoed look', preview: '/examples/lego.jpg' },
  { id: 'polaroid', name: 'Polaroid', description: 'Vintage polaroid foto met retro 70s look', preview: '/examples/polaroid.jpg' },
  { id: 'disney', name: 'Disney', description: 'Disney animatie met magische visuals', preview: '/examples/disney.jpg' },
  { id: 'realism', name: 'Realism', description: 'Fotorealistische professionele fotografie', preview: '/examples/realism.jpg' },
  { id: 'fantastic', name: 'Fantastic', description: 'Surrealistische fantasy met dromerige elementen', preview: '/examples/fantastic.jpg' },
];

const CAPTION_STYLES = [
  { id: 'bold-stroke', name: 'Bold Stroke', description: 'Dikke witte rand voor maximale leesbaarheid', preview: '/examples/caption-bold-stroke.jpg' },
  { id: 'red-highlight', name: 'Red Highlight', description: 'Rode highlight voor extra impact', preview: '/examples/caption-red-highlight.jpg' },
  { id: 'sleek', name: 'Sleek', description: 'Minimalistisch en elegant', preview: '/examples/caption-sleek.jpg' },
  { id: 'karaoke', name: 'Karaoke', description: 'Woord-voor-woord bounce effect', preview: '/examples/caption-karaoke.jpg' },
  { id: 'majestic', name: 'Majestic', description: 'Koninklijke serif stijl met goud', preview: '/examples/caption-majestic.jpg' },
  { id: 'beast', name: 'Beast', description: 'Agressief met vurige effecten', preview: '/examples/caption-beast.jpg' },
];

const ELEVENLABS_VOICES = [
  // Dutch voices
  { id: 'pNInz6obpgDQGcFmaJgB', name: 'Adam (Male, Deep)', language: 'dutch' },
  { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Bella (Female, Soft)', language: 'dutch' },
  { id: 'ErXwobaYiN019PkySvjV', name: 'Antoni (Male, Warm)', language: 'dutch' },
  { id: 'MF3mGyEYCl7XYWbV9V6O', name: 'Elli (Female, Young)', language: 'dutch' },
  { id: 'TxGEqnHWrfWFTfGW9XjX', name: 'Josh (Male, Strong)', language: 'dutch' },
  { id: 'VR6AewLTigWG4xSOukaG', name: 'Arnold (Male, Mature)', language: 'dutch' },
  { id: 'pqHfZKP75CvOlQylNhV4', name: 'Bill (Male, Documentary)', language: 'dutch' },
  { id: 'N2lVS1w4EtoT3dr4eOWO', name: 'Callum (Male, Raspy)', language: 'dutch' },
  { id: 'IKne3meq5aSn9XLyUdCD', name: 'Charlie (Male, Casual)', language: 'dutch' },
  { id: 'XB0fDUnXU5powFXDhCwa', name: 'Charlotte (Female, Energetic)', language: 'dutch' },
  { id: 'iP95p4xoKVk53GoZ742B', name: 'Chris (Male, Calm)', language: 'dutch' },
  { id: 'nPczCjzI2devNBz1zQrb', name: 'Daniel (Male, British)', language: 'dutch' },
  { id: 'ThT5KcBeYPX3keUQqHPh', name: 'Dorothy (Female, Pleasant)', language: 'dutch' },
  { id: 'CwhRBWXzGAHq8TQ4Fs17', name: 'Drew (Male, Deep)', language: 'dutch' },
  { id: 'zrHiDhphv9ZnVXBqCLjz', name: 'Ethan (Male, Young)', language: 'dutch' },
  { id: 'g5CIjZEefAph4nQFvHAz', name: 'Fin (Male, Irish)', language: 'dutch' },
  { id: 'jBpfuIE2acCO8z3wKNLl', name: 'Gigi (Female, Animated)', language: 'dutch' },
  { id: 'zcAOhNBS3c14rBihAFp1', name: 'Giovanni (Male, Italian)', language: 'dutch' },
  { id: 'XrExE9yKIg1WjnnlVkGX', name: 'Glinda (Female, Witch)', language: 'dutch' },
  { id: 'z9fAnlkpzviPz146aGWa', name: 'Grace (Female, Southern)', language: 'dutch' },
  { id: 'SOYHLrjzK2X1ezoPC6cr', name: 'Harry (Male, Anxious)', language: 'dutch' },
  { id: 'TX3LPaxmHKxFdv7VOQHJ', name: 'James (Male, Calm)', language: 'dutch' },
  { id: 'cgSgspJ2msm6clMCkdW9', name: 'Jeremy (Male, Excited)', language: 'dutch' },
  { id: 'bVMeCyTHy58xNoL34h3p', name: 'Jessie (Female, Raspy)', language: 'dutch' },
  { id: 'FGY2WhTYpPnrIDTdsKH5', name: 'Lily (Female, Warm)', language: 'dutch' },
  { id: '2EiwWnXFnvU5JabPnv8n', name: 'Clyde (Male, Strong)', language: 'dutch' },
  { id: 'ODq5zmih8GrVes37Dizd', name: 'Patrick (Male, Deep)', language: 'dutch' },
  { id: 'onwK4e9ZLuTAKqWW03F9', name: 'Daniel (Male, Calm)', language: 'dutch' },
  // English voices
  { id: 'pNInz6obpgDQGcFmaJgB', name: 'Adam (Male, Deep)', language: 'english' },
  { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Bella (Female, Soft)', language: 'english' },
  { id: 'ErXwobaYiN019PkySvjV', name: 'Antoni (Male, Warm)', language: 'english' },
  { id: 'MF3mGyEYCl7XYWbV9V6O', name: 'Elli (Female, Young)', language: 'english' },
  { id: 'TxGEqnHWrfWFTfGW9XjX', name: 'Josh (Male, Strong)', language: 'english' },
  { id: 'VR6AewLTigWG4xSOukaG', name: 'Arnold (Male, Mature)', language: 'english' },
  { id: 'pqHfZKP75CvOlQylNhV4', name: 'Bill (Male, Documentary)', language: 'english' },
  { id: 'N2lVS1w4EtoT3dr4eOWO', name: 'Callum (Male, Raspy)', language: 'english' },
  { id: 'IKne3meq5aSn9XLyUdCD', name: 'Charlie (Male, Casual)', language: 'english' },
  { id: 'XB0fDUnXU5powFXDhCwa', name: 'Charlotte (Female, Energetic)', language: 'english' },
];

const MUSIC_OPTIONS = [
  { id: 'ambient', name: 'Ambient', emoji: '🎹', description: 'Rustige achtergrondmuziek, perfect voor focus en concentratie' },
  { id: 'dramatic', name: 'Dramatic', emoji: '🎻', description: 'Intense spanning en emotie, ideaal voor verhalen met impact' },
  { id: 'upbeat', name: 'Upbeat', emoji: '🎸', description: 'Energieke en vrolijke muziek voor positieve content' },
  { id: 'chill', name: 'Chill', emoji: '🎵', description: 'Relaxte vibes voor ontspannen en informatieve video\'s' },
  { id: 'epic', name: 'Epic', emoji: '🎺', description: 'Grootse orkestrale muziek voor heldhaftige content' },
  { id: 'none', name: 'Geen muziek', emoji: '🔇', description: 'Alleen voice-over zonder achtergrondmuziek' },
];

export default function CreateVideoPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formatType, setFormatType] = useState<'preset' | 'custom'>('preset');
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [selectedFormats, setSelectedFormats] = useState<string[]>([]);
  
  const [formData, setFormData] = useState({
    topic: '',
    niche: '',
    duration: 'medium',
    language: 'dutch',
    voice: 'pNInz6obpgDQGcFmaJgB',
    voiceStyle: 'calm',
    artStyle: 'realism',
    captionStyle: 'bold-stroke',
    backgroundMusic: 'ambient',
  });

  const handleFormatToggle = (formatId: string) => {
    setSelectedFormats(prev => 
      prev.includes(formatId) 
        ? prev.filter(id => id !== formatId)
        : [...prev, formatId]
    );
  };

  const handleGenerate = async () => {
    // Validation
    if (!formData.topic && !selectedPreset) {
      toast.error('Selecteer een preset of vul een onderwerp in');
      return;
    }

    if (formatType === 'custom' && selectedFormats.length === 0) {
      toast.error('Selecteer minstens één format');
      return;
    }

    if (formatType === 'custom' && !formData.niche) {
      toast.error('Beschrijf je niche');
      return;
    }

    setLoading(true);

    try {
      // Determine niche
      let niche = formData.niche;
      if (formatType === 'preset' && selectedPreset) {
        const preset = PRESETS.find(p => p.id === selectedPreset);
        niche = preset?.description || '';
      }

      // Determine format
      let format = formatType;
      let presetType = selectedPreset || undefined;
      let customFormat = selectedFormats.length > 0 ? selectedFormats.join(',') : undefined;

      // Create a series for the video
      const seriesResponse = await fetch('/api/series', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.topic || PRESETS.find(p => p.id === selectedPreset)?.name || 'New Video',
          format,
          presetType,
          customFormat,
          niche,
          language: formData.language,
          voice: formData.voice,
          voiceStyle: formData.voiceStyle,
          backgroundMusic: formData.backgroundMusic === 'none' ? undefined : formData.backgroundMusic,
          artStyle: formData.artStyle,
          captionStyle: formData.captionStyle,
          duration: formData.duration,
          videoCount: 1,
        }),
      });

      const seriesData = await seriesResponse.json();

      if (!seriesData.id) {
        throw new Error('Failed to create series');
      }

      // Generate video
      const videoResponse = await fetch(`/api/series/${seriesData.id}/generate-next-video`, {
        method: 'POST',
      });

      const videoData = await videoResponse.json();

      if (videoData.success) {
        toast.success('Video wordt gegenereerd!', {
          description: 'Dit kan enkele minuten duren.',
        });
        router.push(`/dashboard/series/${seriesData.id}`);
      } else {
        throw new Error(videoData.error || 'Failed to generate video');
      }
    } catch (error: any) {
      console.error('Error:', error);
      toast.error('Genereren mislukt', {
        description: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const availableVoices = ELEVENLABS_VOICES.filter(v => v.language === formData.language);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <Link href="/" className="inline-flex items-center text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Terug naar Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">🎬 Maak je Video</h1>
          <p className="text-xl text-gray-600">Selecteer alle opties en genereer direct je video</p>
        </div>

        <div className="space-y-8">
          {/* Step 1: Format & Niche */}
          <Card className="border-2 border-purple-100">
            <CardHeader>
              <CardTitle className="text-2xl">📋 Stap 1: Kies Format & Niche</CardTitle>
              <p className="text-gray-600">Selecteer een preset of maak je eigen format</p>
            </CardHeader>
            <CardContent>
              <Tabs value={formatType} onValueChange={(v) => setFormatType(v as 'preset' | 'custom')}>
                <TabsList className="grid w-full max-w-md grid-cols-2">
                  <TabsTrigger 
                    value="preset"
                    onClick={() => setFormatType('preset')}
                  >
                    🎯 Presets
                  </TabsTrigger>
                  <TabsTrigger 
                    value="custom"
                    onClick={() => setFormatType('custom')}
                  >
                    ✨ Custom
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="preset" className="space-y-4 mt-6">
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {PRESETS.map((preset) => (
                      <Card
                        key={preset.id}
                        className={`cursor-pointer transition-all hover:shadow-lg ${
                          selectedPreset === preset.id
                            ? 'ring-2 ring-purple-500 bg-purple-50'
                            : 'hover:border-purple-300'
                        }`}
                        onClick={() => setSelectedPreset(preset.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <span className="text-3xl">{preset.emoji}</span>
                            {selectedPreset === preset.id && (
                              <Check className="w-5 h-5 text-purple-600" />
                            )}
                          </div>
                          <h3 className="font-bold text-lg mb-1">{preset.name}</h3>
                          <p className="text-sm text-gray-600 mb-3">{preset.description}</p>
                          <div className="flex flex-wrap gap-1">
                            {preset.formats.map((format) => (
                              <span
                                key={format}
                                className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full"
                              >
                                {format}
                              </span>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="custom" className="space-y-4 mt-6">
                  <div>
                    <Label className="text-lg font-semibold mb-3 block">Formats</Label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {CUSTOM_FORMATS.map((format) => (
                        <div
                          key={format.id}
                          className={`flex items-center space-x-2 p-3 border-2 rounded-lg cursor-pointer transition-all ${
                            selectedFormats.includes(format.id)
                              ? 'border-purple-500 bg-purple-50'
                              : 'border-gray-200 hover:border-purple-300'
                          }`}
                          onClick={() => handleFormatToggle(format.id)}
                        >
                          <Checkbox
                            checked={selectedFormats.includes(format.id)}
                            onCheckedChange={() => handleFormatToggle(format.id)}
                          />
                          <span className="text-xl">{format.emoji}</span>
                          <Label className="cursor-pointer">{format.name}</Label>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="custom-niche" className="text-lg font-semibold">Niche</Label>
                    <Textarea
                      id="custom-niche"
                      placeholder="Bijv: History videos about events that aren't well known"
                      value={formData.niche}
                      onChange={(e) => setFormData({ ...formData, niche: e.target.value })}
                      className="mt-2 min-h-[100px]"
                    />
                    <p className="text-sm text-gray-500 mt-1">Beschrijf je video niche in detail (0/5000 characters)</p>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Step 2: Language & Voice */}
          <Card className="border-2 border-purple-100">
            <CardHeader>
              <CardTitle className="text-2xl">🗣️ Stap 2: Taal & Stem</CardTitle>
              <p className="text-gray-600">Kies de taal en voice-over stijl</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="language" className="text-lg font-semibold">Taal</Label>
                  <Select
                    value={formData.language}
                    onValueChange={(value) => setFormData({ ...formData, language: value })}
                  >
                    <SelectTrigger id="language" className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="dutch">🇳🇱 Nederlands</SelectItem>
                      <SelectItem value="english">🇬🇧 Engels</SelectItem>
                      <SelectItem value="spanish">🇪🇸 Spaans</SelectItem>
                      <SelectItem value="french">🇫🇷 Frans</SelectItem>
                      <SelectItem value="german">🇩🇪 Duits</SelectItem>
                      <SelectItem value="hindi">🇮🇳 Hindi</SelectItem>
                      <SelectItem value="italian">🇮🇹 Italiaans</SelectItem>
                      <SelectItem value="japanese">🇯🇵 Japans</SelectItem>
                      <SelectItem value="korean">🇰🇷 Koreaans</SelectItem>
                      <SelectItem value="polish">🇵🇱 Pools</SelectItem>
                      <SelectItem value="portuguese">🇵🇹 Portugees</SelectItem>
                      <SelectItem value="turkish">🇹🇷 Turks</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="voice" className="text-lg font-semibold">ElevenLabs Stem</Label>
                  <Select
                    value={formData.voice}
                    onValueChange={(value) => setFormData({ ...formData, voice: value })}
                  >
                    <SelectTrigger id="voice" className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="max-h-80">
                      {availableVoices.map((voice) => (
                        <SelectItem key={voice.id} value={voice.id}>
                          {voice.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Step 3: Music */}
          <Card className="border-2 border-purple-100">
            <CardHeader>
              <CardTitle className="text-2xl">🎵 Stap 3: Achtergrond Muziek</CardTitle>
              <p className="text-gray-600">Kies rechtenvrije muziek voor je video</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {MUSIC_OPTIONS.map((music) => (
                  <div
                    key={music.id}
                    className={`relative cursor-pointer rounded-lg p-4 border-2 transition-all hover:shadow-md ${
                      formData.backgroundMusic === music.id
                        ? 'border-purple-500 bg-purple-50 ring-2 ring-purple-200'
                        : 'border-gray-200 hover:border-purple-300 bg-white'
                    }`}
                    onClick={() => setFormData({ ...formData, backgroundMusic: music.id })}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`text-4xl p-2 rounded-lg ${
                        formData.backgroundMusic === music.id ? 'bg-purple-100' : 'bg-gray-100'
                      }`}>
                        {music.emoji}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className={`font-semibold ${
                            formData.backgroundMusic === music.id ? 'text-purple-900' : 'text-gray-900'
                          }`}>
                            {music.name}
                          </h4>
                          {formData.backgroundMusic === music.id && (
                            <Check className="w-5 h-5 text-purple-600" />
                          )}
                        </div>
                        <p className={`text-sm ${
                          formData.backgroundMusic === music.id ? 'text-purple-700' : 'text-gray-600'
                        }`}>
                          {music.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Step 4: Art Style */}
          <Card className="border-2 border-purple-100">
            <CardHeader>
              <CardTitle className="text-2xl">🎨 Stap 4: Art Style</CardTitle>
              <p className="text-gray-600">Kies de visuele stijl voor je video</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {ART_STYLES.map((style) => (
                  <div
                    key={style.id}
                    className={`relative cursor-pointer rounded-lg overflow-hidden transition-all hover:shadow-lg border-2 ${
                      formData.artStyle === style.id
                        ? 'border-purple-500 ring-2 ring-purple-200'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                    onClick={() => setFormData({ ...formData, artStyle: style.id })}
                  >
                    <div className="aspect-[4/3] relative bg-gray-100">
                      <img
                        src={style.preview}
                        alt={style.name}
                        className="w-full h-full object-cover"
                      />
                      {formData.artStyle === style.id && (
                        <div className="absolute inset-0 bg-purple-600/20 flex items-center justify-center">
                          <div className="bg-purple-600 rounded-full p-2">
                            <Check className="w-5 h-5 text-white" />
                          </div>
                        </div>
                      )}
                    </div>
                    <div className={`p-3 ${
                      formData.artStyle === style.id
                        ? 'bg-purple-50'
                        : 'bg-white'
                    }`}>
                      <h4 className={`font-semibold text-sm mb-1 ${
                        formData.artStyle === style.id ? 'text-purple-900' : 'text-gray-900'
                      }`}>
                        {style.name}
                      </h4>
                      <p className={`text-xs ${
                        formData.artStyle === style.id ? 'text-purple-700' : 'text-gray-600'
                      }`}>
                        {style.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Step 5: Caption Style */}
          <Card className="border-2 border-purple-100">
            <CardHeader>
              <CardTitle className="text-2xl">💬 Stap 5: Caption Style</CardTitle>
              <p className="text-gray-600">Kies hoe captions verschijnen in je video</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {CAPTION_STYLES.map((style) => (
                  <button
                    key={style.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, captionStyle: style.id })}
                    className={`group relative overflow-hidden rounded-lg border-2 transition-all ${
                      formData.captionStyle === style.id
                        ? 'border-purple-500 shadow-lg scale-105'
                        : 'border-gray-200 hover:border-purple-300 hover:scale-102'
                    }`}
                  >
                    <div className="relative aspect-[4/3] bg-gray-100">
                      <Image
                        src={style.preview}
                        alt={style.name}
                        fill
                        className="object-cover"
                      />
                    </div>
                    <div className="p-3 bg-white">
                      <p className="text-sm font-semibold text-gray-900">{style.name}</p>
                      <p className="text-xs text-gray-500 mt-1">{style.description}</p>
                    </div>
                    {formData.captionStyle === style.id && (
                      <div className="absolute top-2 right-2 bg-purple-500 text-white rounded-full p-1">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Step 6: Duration & Topic */}
          <Card className="border-2 border-purple-100">
            <CardHeader>
              <CardTitle className="text-2xl">⏱️ Stap 6: Duur & Onderwerp</CardTitle>
              <p className="text-gray-600">Bepaal de lengte en onderwerp</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="duration" className="text-lg font-semibold">Video Lengte</Label>
                <Select
                  value={formData.duration}
                  onValueChange={(value) => setFormData({ ...formData, duration: value })}
                >
                  <SelectTrigger id="duration" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="short">⚡ Kort (30-60 sec)</SelectItem>
                    <SelectItem value="medium">📽️ Normaal (1-3 min)</SelectItem>
                    <SelectItem value="long">🎬 Lang (3-5 min)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="topic" className="text-lg font-semibold">
                  Onderwerp <span className="text-gray-500">(Optioneel)</span>
                </Label>
                <Input
                  id="topic"
                  placeholder="Bijv: 5 Tips voor Succes"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  className="mt-2"
                />
                <p className="text-sm text-gray-500 mt-1">Laat leeg voor een random onderwerp binnen je niche</p>
              </div>
            </CardContent>
          </Card>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white h-14 text-xl"
          >
            {loading ? (
              <>
                <Loader2 className="w-6 h-6 mr-2 animate-spin" />
                Video wordt gegenereerd...
              </>
            ) : (
              <>
                <Sparkles className="w-6 h-6 mr-2" />
                🎬 Genereer Video Nu!
              </>
            )}
          </Button>
        </div>
      </main>
    </div>
  );
}
