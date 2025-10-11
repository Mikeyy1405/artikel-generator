
'use client';

import { Calendar, Hash, PlayCircle } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { SeriesFormData } from '@/lib/types';

interface Step7Props {
  formData: Partial<SeriesFormData>;
  updateFormData: (data: Partial<SeriesFormData>) => void;
}

const scheduleOptions = [
  { value: 'daily', label: 'Dagelijks' },
  { value: 'every-2-days', label: 'Om de 2 dagen' },
  { value: 'weekly', label: 'Wekelijks' },
  { value: 'manual', label: 'Handmatig' },
];

const timeSlots = [
  '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
  '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
  '20:00', '21:00', '22:00',
];

export default function Step7SeriesDetails({ formData, updateFormData }: Step7Props) {
  const handleNameChange = (seriesName: string) => {
    updateFormData({ seriesName });
  };

  const handleVideoCountChange = (count: string) => {
    const videoCount = parseInt(count, 10);
    if (!isNaN(videoCount) && videoCount > 0 && videoCount <= 20) {
      updateFormData({ videoCount });
    }
  };

  const handleScheduleChange = (publishSchedule: string) => {
    updateFormData({ publishSchedule });
  };

  const handleTimeChange = (publishTime: string) => {
    updateFormData({ publishTime });
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Serie Details
        </h2>
        <p className="text-gray-600">
          Vul de details van je video serie in
        </p>
      </div>

      {/* Series Name */}
      <div className="space-y-2">
        <Label htmlFor="series-name" className="text-lg font-semibold text-gray-900 flex items-center">
          <PlayCircle className="w-5 h-5 mr-2 text-purple-600" />
          Serie Naam
        </Label>
        <Input
          id="series-name"
          placeholder="Bijv. Mysterieuze Verhalen, Historische Feiten..."
          value={formData.seriesName || ''}
          onChange={(e) => handleNameChange(e.target.value)}
          className="border-purple-200 focus:border-purple-500 focus:ring-purple-500"
        />
      </div>

      {/* Number of Videos */}
      <div className="space-y-2">
        <Label htmlFor="video-count" className="text-lg font-semibold text-gray-900 flex items-center">
          <Hash className="w-5 h-5 mr-2 text-purple-600" />
          Aantal Video's
        </Label>
        <div className="flex items-center space-x-4">
          <Input
            id="video-count"
            type="number"
            min="1"
            max="20"
            value={formData.videoCount || ''}
            onChange={(e) => handleVideoCountChange(e.target.value)}
            className="w-24 border-purple-200 focus:border-purple-500 focus:ring-purple-500"
          />
          <div className="flex-1 bg-purple-50 rounded-lg p-3">
            <p className="text-sm text-purple-700">
              Minimaal 1 video, maximaal 20 video's per serie
            </p>
          </div>
        </div>
      </div>

      {/* Publish Schedule */}
      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900 flex items-center">
          <Calendar className="w-5 h-5 mr-2 text-purple-600" />
          Publicatie Schema (optioneel)
        </Label>
        
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="schedule" className="text-sm font-medium text-gray-700">
              Frequentie
            </Label>
            <Select value={formData.publishSchedule || ''} onValueChange={handleScheduleChange}>
              <SelectTrigger className="border-purple-200 focus:border-purple-500 focus:ring-purple-500">
                <SelectValue placeholder="Selecteer schema" />
              </SelectTrigger>
              <SelectContent>
                {scheduleOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {formData.publishSchedule && formData.publishSchedule !== 'manual' && (
            <div>
              <Label htmlFor="time" className="text-sm font-medium text-gray-700">
                Tijd
              </Label>
              <Select value={formData.publishTime || ''} onValueChange={handleTimeChange}>
                <SelectTrigger className="border-purple-200 focus:border-purple-500 focus:ring-purple-500">
                  <SelectValue placeholder="Selecteer tijd" />
                </SelectTrigger>
                <SelectContent>
                  {timeSlots.map((time) => (
                    <SelectItem key={time} value={time}>
                      {time}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Samenvatting</h3>
        <div className="grid gap-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Serie naam:</span>
            <span className="font-medium text-gray-900">{formData.seriesName || 'Niet ingesteld'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Format:</span>
            <span className="font-medium text-gray-900">
              {formData.format === 'preset' 
                ? formData.presetType?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
                : formData.customFormat?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())
              }
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Niche:</span>
            <span className="font-medium text-gray-900">{formData.niche}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Taal:</span>
            <span className="font-medium text-gray-900">{formData.language}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Stem:</span>
            <span className="font-medium text-gray-900">{formData.voiceStyle}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Art style:</span>
            <span className="font-medium text-gray-900">{formData.artStyle}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Duur:</span>
            <span className="font-medium text-gray-900">
              {formData.duration === 'short' ? 'Short-form (30-60s)' : 'Long-form (3-5min)'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Aantal video's:</span>
            <span className="font-medium text-gray-900">{formData.videoCount}</span>
          </div>
          {formData.publishSchedule && (
            <div className="flex justify-between">
              <span className="text-gray-600">Schema:</span>
              <span className="font-medium text-gray-900">
                {scheduleOptions.find(s => s.value === formData.publishSchedule)?.label}
                {formData.publishTime && ` om ${formData.publishTime}`}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
