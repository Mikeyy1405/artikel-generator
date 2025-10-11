
'use client';

import { Sparkles, FileText, Video, Image, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-violet-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent">
                ContentStudio
              </h1>
            </div>
            <Link href="/dashboard">
              <Button variant="outline" className="border-purple-200 text-purple-600 hover:bg-purple-50">
                Dashboard →
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Maak{' '}
            <span className="bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent">
              professionele content
            </span>
            <br />
            in enkele minuten
          </h2>
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            Super simpel. Mega hoge kwaliteit. Kies wat je wilt maken en laat AI het werk doen.
          </p>
        </div>

        {/* Main Action Cards */}
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-6 px-4">
          {/* Blog Post Card */}
          <Link href="/create/blog">
            <Card className="group hover:shadow-2xl transition-all duration-300 border-2 border-purple-100 hover:border-purple-300 cursor-pointer h-full">
              <CardContent className="pt-8 pb-8 text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <FileText className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">Blog Post</h3>
                <p className="text-gray-600 mb-6">
                  SEO-geoptimaliseerde artikelen van 1000-3000 woorden
                </p>
                <Button className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white">
                  Start Blog Post
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </Link>

          {/* Video Card */}
          <Link href="/create/video">
            <Card className="group hover:shadow-2xl transition-all duration-300 border-2 border-purple-100 hover:border-purple-300 cursor-pointer h-full">
              <CardContent className="pt-8 pb-8 text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Video className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">Video</h3>
                <p className="text-gray-600 mb-6">
                  Professionele faceless video's van 30 sec tot 5 minuten
                </p>
                <Button className="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white">
                  Start Video
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </Link>

          {/* Social Media Post Card */}
          <Link href="/create/social">
            <Card className="group hover:shadow-2xl transition-all duration-300 border-2 border-purple-100 hover:border-purple-300 cursor-pointer h-full">
              <CardContent className="pt-8 pb-8 text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Image className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">Social Post</h3>
                <p className="text-gray-600 mb-6">
                  Eye-catching posts met AI-gegenereerde afbeeldingen
                </p>
                <Button className="w-full bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700 text-white">
                  Start Social Post
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Waarom ContentStudio?
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Supersimpel</h4>
              <p className="text-gray-600">
                Kies wat je wilt maken, vul een paar velden in, en klaar. Geen gedoe.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Mega Hoge Kwaliteit</h4>
              <p className="text-gray-600">
                AI-gegenereerde content die eruitziet alsof het door professionals is gemaakt.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Razendsnel</h4>
              <p className="text-gray-600">
                Content genereren in minuten, niet uren. Meer tijd voor wat echt telt.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-50 py-12 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-violet-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent">
              ContentStudio
            </h1>
          </div>
          <p className="text-gray-600">
            © 2024 ContentStudio. Professionele content in enkele minuten.
          </p>
        </div>
      </footer>
    </div>
  );
}
