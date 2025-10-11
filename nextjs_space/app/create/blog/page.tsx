
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Sparkles, Loader2 } from 'lucide-react';
import Link from 'next/link';
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

export default function CreateBlogPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    keywords: '',
    contentType: 'seo',
    tone: 'professional',
    wordCount: '1500',
  });

  const handleGenerate = async () => {
    if (!formData.title) {
      toast.error('Vul een titel in');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/blog/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: formData.title,
          keywords: formData.keywords.split(',').map((k) => k.trim()),
          contentType: formData.contentType,
          tone: formData.tone,
          wordCount: parseInt(formData.wordCount),
        }),
      });

      const data = await response.json();

      if (data.success) {
        toast.success('Blog post gegenereerd!', {
          description: 'Je artikel is klaar.',
        });
        router.push('/dashboard');
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Link href="/" className="inline-flex items-center text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Terug
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Blog Post Maken</h1>
          <p className="text-xl text-gray-600">Vul de details in en laat AI je artikel schrijven</p>
        </div>

        <Card className="border-2 border-blue-100">
          <CardHeader>
            <CardTitle>Artikel Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Titel van je artikel *</Label>
              <Input
                id="title"
                placeholder="Bijv: 10 Tips voor Betere Productiviteit"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="text-lg"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="keywords">Keywords (optioneel)</Label>
              <Input
                id="keywords"
                placeholder="Bijv: productiviteit, timemanagement, efficiëntie"
                value={formData.keywords}
                onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
              />
              <p className="text-sm text-gray-500">Scheid meerdere keywords met komma's</p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="contentType">Type Artikel</Label>
                <Select
                  value={formData.contentType}
                  onValueChange={(value) => setFormData({ ...formData, contentType: value })}
                >
                  <SelectTrigger id="contentType">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="seo">🎯 SEO Artikel</SelectItem>
                    <SelectItem value="listicle">📝 Lijstje</SelectItem>
                    <SelectItem value="howto">📚 How-to Guide</SelectItem>
                    <SelectItem value="review">⭐ Review</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="wordCount">Aantal Woorden</Label>
                <Select
                  value={formData.wordCount}
                  onValueChange={(value) => setFormData({ ...formData, wordCount: value })}
                >
                  <SelectTrigger id="wordCount">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="800">800 woorden (kort)</SelectItem>
                    <SelectItem value="1500">1500 woorden (gemiddeld)</SelectItem>
                    <SelectItem value="2500">2500 woorden (lang)</SelectItem>
                    <SelectItem value="3500">3500 woorden (uitgebreid)</SelectItem>
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
                  <SelectItem value="professional">💼 Professioneel</SelectItem>
                  <SelectItem value="casual">😊 Casual & Vriendelijk</SelectItem>
                  <SelectItem value="inspiring">✨ Inspirerend</SelectItem>
                  <SelectItem value="educational">📖 Educatief</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading || !formData.title}
              className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white h-12 text-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Artikel wordt gegenereerd...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Genereer Blog Post
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
