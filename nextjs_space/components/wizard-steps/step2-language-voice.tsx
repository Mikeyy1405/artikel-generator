
'use client';

import { Play, User, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { SeriesFormData, Voice } from '@/lib/types';

interface Step2Props {
  formData: Partial<SeriesFormData>;
  updateFormData: (data: Partial<SeriesFormData>) => void;
}

const languages = [
  'Nederlands',
  'English',
  'Spanish',
  'French',
  'German',
  'Hindi',
  'Italian',
  'Japanese',
  'Korean',
  'Polish',
  'Portuguese',
  'Turkish',
];

const voices: Voice[] = [
  { id: 'adam', name: 'Adam', gender: 'Male', description: 'Diep en professioneel' },
  { id: 'john', name: 'John', gender: 'Male', description: 'Warm en vriendelijk' },
  { id: 'marcus', name: 'Marcus', gender: 'Male', description: 'Energiek en dynamisch' },
  { id: 'sarah', name: 'Sarah', gender: 'Female', description: 'Helder en vertrouwd' },
  { id: 'emma', name: 'Emma', gender: 'Female', description: 'Zachte en kalme stem' },
  { id: 'lisa', name: 'Lisa', gender: 'Female', description: 'Expressief en levendig' },
];

export default function Step2LanguageVoice({ formData, updateFormData }: Step2Props) {
  const handleLanguageChange = (language: string) => {
    updateFormData({ language });
  };

  const handleVoiceSelect = (voiceId: string) => {
    const selectedVoice = voices.find(v => v.id === voiceId);
    if (selectedVoice) {
      updateFormData({ 
        voice: voiceId,
        voiceStyle: selectedVoice.name,
      });
    }
  };

  const handlePreview = (voiceId: string) => {
    // Demo preview functionality
    console.log(`Preview voice: ${voiceId}`);
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Taal & Stem
        </h2>
        <p className="text-gray-600">
          Selecteer de taal en stem voor je video's
        </p>
      </div>

      {/* Language Selection */}
      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900">Taal</Label>
        <Select value={formData.language || ''} onValueChange={handleLanguageChange}>
          <SelectTrigger className="w-full border-purple-200 focus:border-purple-500 focus:ring-purple-500">
            <SelectValue placeholder="Selecteer een taal" />
          </SelectTrigger>
          <SelectContent>
            {languages.map((language) => (
              <SelectItem key={language} value={language}>
                {language}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Voice Selection */}
      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900">Stem Stijl</Label>
        <div className="grid gap-4">
          {voices.map((voice) => (
            <div
              key={voice.id}
              className={`selection-card ${
                formData.voice === voice.id
                  ? 'selection-card-selected'
                  : 'selection-card-unselected'
              }`}
              onClick={() => handleVoiceSelect(voice.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <User className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {voice.name} - {voice.gender}
                    </h3>
                    <p className="text-gray-600 text-sm">{voice.description}</p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePreview(voice.id);
                  }}
                  className="border-purple-200 text-purple-600 hover:bg-purple-50"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Preview
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Voice Info */}
      {formData.voice && (
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <Volume2 className="w-5 h-5 text-purple-600" />
            <div>
              <h4 className="font-medium text-purple-900">Geselecteerde Stem</h4>
              <p className="text-purple-700 text-sm">
                {voices.find(v => v.id === formData.voice)?.name} - {voices.find(v => v.id === formData.voice)?.description}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
