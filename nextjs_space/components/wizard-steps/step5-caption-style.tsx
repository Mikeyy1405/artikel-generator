
'use client';

import { Type } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { SeriesFormData, CaptionStyleOption } from '@/lib/types';

interface Step5Props {
  formData: Partial<SeriesFormData>;
  updateFormData: (data: Partial<SeriesFormData>) => void;
}

const captionStyles: CaptionStyleOption[] = [
  {
    id: 'bold-stroke',
    title: 'Bold Stroke',
    previewText: 'Dit is een voorbeeld tekst',
    className: 'text-white font-bold text-xl stroke-black stroke-2',
  },
  {
    id: 'red-highlight',
    title: 'Red Highlight',
    previewText: 'Dit is een voorbeeld tekst',
    className: 'text-white font-semibold text-xl bg-red-600 px-2 py-1 rounded',
  },
  {
    id: 'sleek',
    title: 'Sleek',
    previewText: 'Dit is een voorbeeld tekst',
    className: 'text-white font-medium text-lg bg-black/50 px-3 py-1 rounded-full',
  },
  {
    id: 'karaoke',
    title: 'Karaoke',
    previewText: 'Dit is een voorbeeld tekst',
    className: 'text-yellow-300 font-bold text-xl shadow-lg',
  },
  {
    id: 'majestic',
    title: 'Majestic',
    previewText: 'Dit is een voorbeeld tekst',
    className: 'text-purple-200 font-bold text-2xl',
  },
  {
    id: 'beast',
    title: 'Beast',
    previewText: 'Dit is een voorbeeld tekst',
    className: 'text-orange-400 font-black text-2xl transform rotate-1',
  },
];

export default function Step5CaptionStyle({ formData, updateFormData }: Step5Props) {
  const handleStyleSelect = (styleId: string) => {
    updateFormData({ captionStyle: styleId });
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Ondertitel Stijl
        </h2>
        <p className="text-gray-600">
          Selecteer hoe de ondertitels eruitzien in je video's
        </p>
      </div>

      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900">Kies een ondertitel stijl</Label>
        <div className="grid gap-4">
          {captionStyles.map((style) => (
            <div
              key={style.id}
              className={`selection-card ${
                formData.captionStyle === style.id
                  ? 'selection-card-selected'
                  : 'selection-card-unselected'
              }`}
              onClick={() => handleStyleSelect(style.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Type className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">{style.title}</h3>
                    <div className="bg-gray-800 rounded-lg p-4 min-w-[300px]">
                      <div className={style.className}>
                        {style.previewText}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Style Info */}
      {formData.captionStyle && (
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <Type className="w-5 h-5 text-purple-600" />
            <div>
              <h4 className="font-medium text-purple-900">Geselecteerde Stijl</h4>
              <p className="text-purple-700 text-sm">
                {captionStyles.find(s => s.id === formData.captionStyle)?.title}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
