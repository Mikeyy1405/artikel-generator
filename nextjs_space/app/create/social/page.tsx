
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Sparkles, Loader2, Download } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';

const ART_STYLES = [
  { id: 'comic', name: 'Comic', description: 'Levendige comic book stijl', preview: '/examples/comic.jpg' },
  { id: 'creepy-comic', name: 'Creepy Comic', description: 'Donkere horror comic', preview: '/examples/creepy-comic.jpg' },
  { id: 'painting', name: 'Painting', description: 'Klassieke schilderij stijl', preview: '/examples/painting.jpg' },
  { id: 'ghibli', name: 'Studio Ghibli', description: 'Dromerige anime stijl', preview: '/examples/ghibli.jpg' },
  { id: 'anime', name: 'Anime', description: 'Moderne anime stijl', preview: '/examples/anime.jpg' },
  { id: 'dark-fantasy', name: 'Dark Fantasy', description: 'Mystieke fantasy stijl', preview: '/examples/dark-fantasy.jpg' },
  { id: 'lego', name: 'LEGO', description: 'LEGO blokjes stijl', preview: '/examples/lego.jpg' },
  { id: 'polaroid', name: 'Polaroid', description: 'Vintage polaroid foto', preview: '/examples/polaroid.jpg' },
  { id: 'disney', name: 'Disney', description: 'Disney animatie stijl', preview: '/examples/disney.jpg' },
  { id: 'realism', name: 'Realism', description: 'Fotorealistische stijl', preview: '/examples/realism.jpg' },
  { id: 'fantastic', name: 'Fantastic', description: 'Surrealistische fantasy', preview: '/examples/fantastic.jpg' },
];

export default function CreateSocialPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState<any>(null);
  const [formData, setFormData] = useState({
    topic: '',
    platform: 'instagram',
    postType: 'motivational',
    tone: 'inspiring',
    artStyle: 'realism',
  });

  const handleGenerate = async () => {
    if (!formData.topic) {
      toast.error('Vul een onderwerp in');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/social/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (data.success) {
        setGenerated(data.post);
        toast.success('Social media post gegenereerd!', {
          description: 'Je post is klaar.',
        });
      } else {
        throw new Error(data.error);
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

  const handleDownloadImage = () => {
    if (generated?.imagePath) {
      window.open(generated.imagePath, '_blank');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Gekopieerd naar klembord!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <Link href="/" className="inline-flex items-center text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Terug
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Social Media Post Maken</h1>
          <p className="text-xl text-gray-600">Vul de details in en laat AI je post maken</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Form */}
          <Card className="border-2 border-pink-100">
            <CardHeader>
              <CardTitle>Post Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="topic">Onderwerp *</Label>
                <Input
                  id="topic"
                  placeholder="Bijv: Motivatie voor ondernemers"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  className="text-lg"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="platform">Platform</Label>
                  <Select
                    value={formData.platform}
                    onValueChange={(value) => setFormData({ ...formData, platform: value })}
                  >
                    <SelectTrigger id="platform">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="instagram">📷 Instagram</SelectItem>
                      <SelectItem value="facebook">👥 Facebook</SelectItem>
                      <SelectItem value="twitter">🐦 Twitter/X</SelectItem>
                      <SelectItem value="linkedin">💼 LinkedIn</SelectItem>
                      <SelectItem value="all">🌐 Alle Platforms</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="postType">Type Post</Label>
                  <Select
                    value={formData.postType}
                    onValueChange={(value) => setFormData({ ...formData, postType: value })}
                  >
                    <SelectTrigger id="postType">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="motivational">💪 Motiverend</SelectItem>
                      <SelectItem value="educational">📚 Educatief</SelectItem>
                      <SelectItem value="promotional">🎯 Promotioneel</SelectItem>
                      <SelectItem value="story">📖 Verhaal</SelectItem>
                      <SelectItem value="tips">💡 Tips</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="tone">Tone of Voice</Label>
                <Select
                  value={formData.tone}
                  onValueChange={(value) => setFormData({ ...formData, tone: value })}
                >
                  <SelectTrigger id="tone">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="inspiring">✨ Inspirerend</SelectItem>
                    <SelectItem value="professional">💼 Professioneel</SelectItem>
                    <SelectItem value="casual">😊 Casual</SelectItem>
                    <SelectItem value="energetic">⚡ Energiek</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <Label>Afbeelding Stijl</Label>
                <div className="grid grid-cols-3 gap-3">
                  {ART_STYLES.map((style) => (
                    <button
                      key={style.id}
                      type="button"
                      onClick={() => setFormData({ ...formData, artStyle: style.id })}
                      className={`group relative overflow-hidden rounded-lg border-2 transition-all ${
                        formData.artStyle === style.id
                          ? 'border-pink-500 shadow-lg scale-105'
                          : 'border-gray-200 hover:border-pink-300 hover:scale-102'
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
                      <div className="p-2 bg-white">
                        <p className="text-xs font-semibold text-gray-900">{style.name}</p>
                        <p className="text-[10px] text-gray-500 mt-0.5">{style.description}</p>
                      </div>
                      {formData.artStyle === style.id && (
                        <div className="absolute top-2 right-2 bg-pink-500 text-white rounded-full p-1">
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={loading || !formData.topic}
                className="w-full bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700 text-white h-12 text-lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Post wordt gegenereerd...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Genereer Social Post
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Preview */}
          <Card className="border-2 border-pink-100">
            <CardHeader>
              <CardTitle>Preview</CardTitle>
            </CardHeader>
            <CardContent>
              {!generated ? (
                <div className="text-center py-12 text-gray-500">
                  <Sparkles className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>Vul de details in en klik op "Genereer" om je post te zien</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Image */}
                  {generated.imagePath && (
                    <div className="relative aspect-square rounded-lg overflow-hidden bg-gray-100">
                      <Image
                        src={generated.imagePath}
                        alt={generated.title}
                        fill
                        className="object-cover"
                      />
                    </div>
                  )}

                  {/* Title */}
                  <div>
                    <Label className="text-sm text-gray-500">Titel</Label>
                    <div className="bg-gray-50 rounded-lg p-3 mt-1">
                      <p className="font-semibold">{generated.title}</p>
                    </div>
                  </div>

                  {/* Content */}
                  <div>
                    <Label className="text-sm text-gray-500">Tekst</Label>
                    <div className="bg-gray-50 rounded-lg p-3 mt-1">
                      <p className="whitespace-pre-wrap">{generated.content}</p>
                    </div>
                  </div>

                  {/* Hashtags */}
                  {generated.hashtags?.length > 0 && (
                    <div>
                      <Label className="text-sm text-gray-500">Hashtags</Label>
                      <div className="bg-gray-50 rounded-lg p-3 mt-1">
                        <p className="text-blue-600">
                          {generated.hashtags.map((tag: string) => `#${tag}`).join(' ')}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      onClick={() => copyToClipboard(generated.content + '\n\n' + generated.hashtags.map((tag: string) => `#${tag}`).join(' '))}
                      className="flex-1"
                      variant="outline"
                    >
                      📋 Kopieer Tekst
                    </Button>
                    {generated.imagePath && (
                      <Button
                        onClick={handleDownloadImage}
                        className="flex-1"
                        variant="outline"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download Afbeelding
                      </Button>
                    )}
                  </div>

                  <Button
                    onClick={() => router.push('/dashboard')}
                    className="w-full bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700"
                  >
                    ✓ Opslaan in Dashboard
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
