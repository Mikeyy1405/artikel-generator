
'use client';

import { Clock } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { SeriesFormData } from '@/lib/types';

interface Step6Props {
  formData: Partial<SeriesFormData>;
  updateFormData: (data: Partial<SeriesFormData>) => void;
}

const durationOptions = [
  {
    id: 'short',
    title: 'Short-form',
    subtitle: '30-60 seconden',
    description: 'Perfect voor TikTok, Instagram Reels en YouTube Shorts',
    icon: '🎬',
  },
  {
    id: 'long',
    title: 'Long-form',
    subtitle: '3-5 minuten',
    description: 'Ideaal voor YouTube, Facebook en uitgebreidere verhalen',
    icon: '🎥',
  },
];

export default function Step6Duration({ formData, updateFormData }: Step6Props) {
  const handleDurationSelect = (duration: 'short' | 'long') => {
    updateFormData({ duration });
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Video Duur
        </h2>
        <p className="text-gray-600">
          Kies de lengte van je video's
        </p>
      </div>

      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900">Selecteer video duur</Label>
        <div className="grid gap-6 max-w-2xl mx-auto">
          {durationOptions.map((option) => (
            <div
              key={option.id}
              className={`selection-card p-6 ${
                formData.duration === option.id
                  ? 'selection-card-selected'
                  : 'selection-card-unselected'
              }`}
              onClick={() => handleDurationSelect(option.id as 'short' | 'long')}
            >
              <div className="flex items-center space-x-4">
                <div className="text-4xl">{option.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-xl font-semibold text-gray-900">{option.title}</h3>
                    <span className="text-lg text-purple-600 font-medium">{option.subtitle}</span>
                  </div>
                  <p className="text-gray-600">{option.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Duration Info */}
      {formData.duration && (
        <div className="bg-purple-50 rounded-lg p-4 max-w-2xl mx-auto">
          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-purple-600" />
            <div>
              <h4 className="font-medium text-purple-900">Geselecteerde Duur</h4>
              <p className="text-purple-700 text-sm">
                {durationOptions.find(d => d.id === formData.duration)?.title} - {durationOptions.find(d => d.id === formData.duration)?.subtitle}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
