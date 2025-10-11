
'use client';

import { useState } from 'react';
import { BookOpen, History, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SeriesFormData, PresetOption, CustomFormat } from '@/lib/types';

interface Step1Props {
  formData: Partial<SeriesFormData>;
  updateFormData: (data: Partial<SeriesFormData>) => void;
}

const presetOptions: PresetOption[] = [
  {
    id: 'scary-stories',
    title: 'Scary stories',
    description: 'Enge verhalen die je aandacht vasthouden',
    popularity: 'Storytelling',
  },
  {
    id: 'history',
    title: 'History',
    description: 'Interessante video\'s over geschiedenes die je niet wist',
    popularity: 'Storytelling',
  },
  {
    id: 'true-crime',
    title: 'True Crime',
    description: 'Echte video\'s over true crime stories',
    popularity: 'Storytelling',
  },
];

const customFormats: CustomFormat[] = [
  { id: 'storytelling', title: 'Storytelling' },
  { id: 'what-if', title: 'What if' },
  { id: '5-things', title: '5 things you didn\'t know' },
  { id: 'random-fact', title: 'Random fact' },
];

const getPresetIcon = (id: string) => {
  switch (id) {
    case 'scary-stories':
      return <BookOpen className="w-6 h-6" />;
    case 'history':
      return <History className="w-6 h-6" />;
    case 'true-crime':
      return <Shield className="w-6 h-6" />;
    default:
      return <BookOpen className="w-6 h-6" />;
  }
};

export default function Step1FormatNiche({ formData, updateFormData }: Step1Props) {
  const [customNiche, setCustomNiche] = useState(formData.niche || '');

  const handleFormatChange = (format: 'preset' | 'custom') => {
    updateFormData({ 
      format,
      presetType: format === 'preset' ? formData.presetType : undefined,
      customFormat: format === 'custom' ? formData.customFormat : undefined,
    });
  };

  const handlePresetSelect = (presetType: string) => {
    updateFormData({ presetType: presetType as any });
  };

  const handleCustomFormatSelect = (customFormat: string) => {
    updateFormData({ customFormat: customFormat as any });
  };

  const handleNicheChange = (niche: string) => {
    setCustomNiche(niche);
    updateFormData({ niche });
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Kies Format & Niche
        </h2>
        <p className="text-gray-600">
          Selecteer een preset of customize je eigen format en niche
        </p>
      </div>

      {/* Format Selection */}
      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900">Format Type</Label>
        <div className="flex space-x-4">
          <Button
            variant={formData.format === 'preset' ? 'default' : 'outline'}
            onClick={() => handleFormatChange('preset')}
            className={formData.format === 'preset' ? 'gradient-button' : 'border-purple-200 text-purple-600 hover:bg-purple-50'}
          >
            Preset
          </Button>
          <Button
            variant={formData.format === 'custom' ? 'default' : 'outline'}
            onClick={() => handleFormatChange('custom')}
            className={formData.format === 'custom' ? 'gradient-button' : 'border-purple-200 text-purple-600 hover:bg-purple-50'}
          >
            Custom
          </Button>
        </div>
      </div>

      {/* Preset Options */}
      {formData.format === 'preset' && (
        <div className="space-y-4">
          <Label className="text-lg font-semibold text-gray-900">Kies een Preset</Label>
          <div className="grid gap-4">
            {presetOptions.map((option) => (
              <div
                key={option.id}
                className={`selection-card ${
                  formData.presetType === option.id
                    ? 'selection-card-selected'
                    : 'selection-card-unselected'
                }`}
                onClick={() => handlePresetSelect(option.id)}
              >
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
                    {getPresetIcon(option.id)}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{option.title}</h3>
                    <p className="text-gray-600 text-sm mb-2">{option.description}</p>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      Format: {option.popularity}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Custom Format */}
      {formData.format === 'custom' && (
        <div className="space-y-4">
          <Label className="text-lg font-semibold text-gray-900">Kies Custom Format</Label>
          <div className="grid grid-cols-2 gap-3">
            {customFormats.map((format) => (
              <div
                key={format.id}
                className={`selection-card text-center ${
                  formData.customFormat === format.id
                    ? 'selection-card-selected'
                    : 'selection-card-unselected'
                }`}
                onClick={() => handleCustomFormatSelect(format.id)}
              >
                <h3 className="font-semibold text-gray-900">{format.title}</h3>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Niche Input */}
      <div className="space-y-2">
        <Label htmlFor="niche" className="text-lg font-semibold text-gray-900">
          Niche
        </Label>
        <Input
          id="niche"
          placeholder="Bijv. Geschiedenis, Technologie, Lifestyle..."
          value={customNiche}
          onChange={(e) => handleNicheChange(e.target.value)}
          className="border-purple-200 focus:border-purple-500 focus:ring-purple-500"
        />
        <p className="text-sm text-gray-500">
          Beschrijf de specifieke niche waar je video's over gaan
        </p>
      </div>
    </div>
  );
}
