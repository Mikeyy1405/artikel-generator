
'use client';

import { User, Mail, CreditCard, Settings, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function AccountPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mijn Account</h1>
        <p className="text-gray-600">Beheer je account instellingen en voorkeuren</p>
      </div>

      <div className="space-y-6">
        {/* Profile Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Profiel Informatie
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Naam</Label>
                <Input id="name" placeholder="Je naam" defaultValue="Gebruiker" />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="je@email.com" defaultValue="user@example.com" />
              </div>
            </div>
            <Button 
              className="bg-[#0C1E43] hover:bg-[#004E92]"
              onClick={() => {
                alert('Profiel opgeslagen!');
              }}
            >
              Opslaan
            </Button>
          </CardContent>
        </Card>

        {/* API Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              API Instellingen
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="openai">OpenAI API Key</Label>
              <Input id="openai" type="password" placeholder="sk-..." defaultValue="••••••••••••••••" />
            </div>
            <div>
              <Label htmlFor="elevenlabs">ElevenLabs API Key</Label>
              <Input id="elevenlabs" type="password" placeholder="..." defaultValue="••••••••••••••••" />
            </div>
            <Button 
              className="bg-[#00AEEF] hover:bg-[#004E92]"
              onClick={() => {
                alert('API keys bijgewerkt!');
              }}
            >
              API Keys Updaten
            </Button>
          </CardContent>
        </Card>

        {/* Subscription */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="w-5 h-5" />
              Abonnement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gradient-to-r from-[#00AEEF] to-[#004E92] text-white p-6 rounded-lg mb-4">
              <p className="text-sm opacity-90 mb-1">Huidig Plan</p>
              <h3 className="text-2xl font-bold mb-4">Pro Plan</h3>
              <p className="text-sm opacity-90">Onbeperkte video's en blog posts</p>
            </div>
            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => {
                alert('Plan wijziging wordt binnenkort beschikbaar!');
              }}
            >
              Plan Wijzigen
            </Button>
          </CardContent>
        </Card>

        {/* Security */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Beveiliging
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="current-password">Huidig Wachtwoord</Label>
              <Input id="current-password" type="password" />
            </div>
            <div>
              <Label htmlFor="new-password">Nieuw Wachtwoord</Label>
              <Input id="new-password" type="password" />
            </div>
            <div>
              <Label htmlFor="confirm-password">Bevestig Wachtwoord</Label>
              <Input id="confirm-password" type="password" />
            </div>
            <Button 
              className="bg-[#FFA62B] hover:bg-[#E36C1E]"
              onClick={() => {
                alert('Wachtwoord wijziging succesvol!');
              }}
            >
              Wachtwoord Wijzigen
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
