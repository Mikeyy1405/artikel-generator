
'use client';

import { Music, Play, Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { SeriesFormData, MusicOption } from '@/lib/types';

interface Step3Props {
  formData: Partial<SeriesFormData>;
  updateFormData: (data: Partial<SeriesFormData>) => void;
}

const musicOptions: MusicOption[] = [
  {
    id: 'happy-rhythm',
    title: 'Happy rhythm',
    description: 'Vrolijke en energieke achtergrondmuziek',
  },
  {
    id: 'quiet-storm',
    title: 'Quiet before storm',
    description: 'Spannende en mysterieuze sfeer',
  },
  {
    id: 'peaceful-vibes',
    title: 'Peaceful vibes',
    description: 'Rustige en ontspannende melodieën',
  },
  {
    id: 'brilliant-symphony',
    title: 'Brilliant symphony',
    description: 'Orkestrale en dramatische muziek',
  },
];

export default function Step3BackgroundMusic({ formData, updateFormData }: Step3Props) {
  const handleMusicSelect = (musicId: string) => {
    const selectedMusic = musicOptions.find(m => m.id === musicId);
    updateFormData({ 
      backgroundMusic: musicId === formData.backgroundMusic ? undefined : musicId,
      musicDescription: selectedMusic ? selectedMusic.description : undefined,
    });
  };

  const handlePreview = (musicId: string) => {
    // Demo preview functionality
    console.log(`Preview music: ${musicId}`);
  };

  const handleNoMusic = () => {
    updateFormData({ 
      backgroundMusic: undefined,
      musicDescription: undefined,
    });
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Achtergrond Muziek
        </h2>
        <p className="text-gray-600">
          Selecteer achtergrondmuziek voor je video's (optioneel)
        </p>
      </div>

      {/* No Music Option */}
      <div className="space-y-4">
        <div
          className={`selection-card ${
            !formData.backgroundMusic
              ? 'selection-card-selected'
              : 'selection-card-unselected'
          }`}
          onClick={handleNoMusic}
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
              <VolumeX className="w-6 h-6 text-gray-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Geen muziek</h3>
              <p className="text-gray-600 text-sm">Video's zonder achtergrondmuziek</p>
            </div>
          </div>
        </div>
      </div>

      {/* Music Options */}
      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900">Muziek Opties</Label>
        <div className="grid gap-4">
          {musicOptions.map((music) => (
            <div
              key={music.id}
              className={`selection-card ${
                formData.backgroundMusic === music.id
                  ? 'selection-card-selected'
                  : 'selection-card-unselected'
              }`}
              onClick={() => handleMusicSelect(music.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Music className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{music.title}</h3>
                    <p className="text-gray-600 text-sm">{music.description}</p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePreview(music.id);
                  }}
                  className="border-purple-200 text-purple-600 hover:bg-purple-50"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Play
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Music Info */}
      {formData.backgroundMusic && (
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <Volume2 className="w-5 h-5 text-purple-600" />
            <div>
              <h4 className="font-medium text-purple-900">Geselecteerde Muziek</h4>
              <p className="text-purple-700 text-sm">
                {musicOptions.find(m => m.id === formData.backgroundMusic)?.title} - {formData.musicDescription}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
