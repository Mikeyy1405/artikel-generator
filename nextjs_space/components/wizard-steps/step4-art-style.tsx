
'use client';

import { Check } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { SeriesFormData, ArtStyleOption } from '@/lib/types';

interface Step4Props {
  formData: Partial<SeriesFormData>;
  updateFormData: (data: Partial<SeriesFormData>) => void;
}

// Art styles with actual visual examples showing the style characteristics
const artStyles: ArtStyleOption[] = [
  {
    id: 'comic',
    title: 'Comic',
    description: 'Levendige comic book stijl met dikke lijnen en felle kleuren',
    imageUrl: '/examples/comic.jpg',
  },
  {
    id: 'creepy-comic',
    title: 'Creepy Comic',
    description: 'Donkere horror comic stijl met dramatische schaduwen',
    imageUrl: '/examples/creepy-comic.jpg',
  },
  {
    id: 'painting',
    title: 'Painting',
    description: 'Klassieke schilderij stijl met rijke texturen',
    imageUrl: '/examples/painting.jpg',
  },
  {
    id: 'ghibli',
    title: 'Studio Ghibli',
    description: 'Dromerige anime stijl zoals Studio Ghibli films',
    imageUrl: '/examples/ghibli.jpg',
  },
  {
    id: 'anime',
    title: 'Anime',
    description: 'Moderne anime stijl met levendige kleuren',
    imageUrl: '/examples/anime.jpg',
  },
  {
    id: 'dark-fantasy',
    title: 'Dark Fantasy',
    description: 'Mystieke fantasy art met dramatische belichting',
    imageUrl: '/examples/dark-fantasy.jpg',
  },
  {
    id: 'lego',
    title: 'LEGO',
    description: 'Gemaakt van LEGO blokjes met speelgoed uitstraling',
    imageUrl: '/examples/lego.jpg',
  },
  {
    id: 'polaroid',
    title: 'Polaroid',
    description: 'Vintage polaroid foto met retro 70s look',
    imageUrl: '/examples/polaroid.jpg',
  },
  {
    id: 'disney',
    title: 'Disney',
    description: 'Disney animatie stijl met magische visuals',
    imageUrl: '/examples/disney.jpg',
  },
  {
    id: 'realism',
    title: 'Realism',
    description: 'Fotorealistische stijl met professionele fotografie',
    imageUrl: '/examples/realism.jpg',
  },
  {
    id: 'fantastic',
    title: 'Fantastic',
    description: 'Surrealistische fantasy art met dromerige elementen',
    imageUrl: '/examples/fantastic.jpg',
  },
];

export default function Step4ArtStyle({ formData, updateFormData }: Step4Props) {
  const handleStyleSelect = (styleId: string) => {
    updateFormData({ artStyle: styleId });
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Art Style
        </h2>
        <p className="text-gray-600">
          Kies de visuele stijl voor je video's
        </p>
      </div>

      <div className="space-y-4">
        <Label className="text-lg font-semibold text-gray-900">Selecteer een stijl</Label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          {artStyles.map((style) => (
            <div
              key={style.id}
              className={`relative cursor-pointer rounded-lg overflow-hidden transition-all duration-200 ${
                formData.artStyle === style.id
                  ? 'ring-4 ring-purple-500 shadow-lg'
                  : 'hover:shadow-md'
              }`}
              onClick={() => handleStyleSelect(style.id)}
            >
              <div className="aspect-[3/2] relative">
                <img
                  src={style.imageUrl}
                  alt={style.title}
                  className="w-full h-full object-cover"
                />
                {formData.artStyle === style.id && (
                  <div className="absolute inset-0 bg-purple-600/20 flex items-center justify-center">
                    <div className="bg-purple-600 rounded-full p-2">
                      <Check className="w-6 h-6 text-white" />
                    </div>
                  </div>
                )}
              </div>
              <div className={`p-3 text-center ${
                formData.artStyle === style.id
                  ? 'bg-purple-50 border-t border-purple-200'
                  : 'bg-white'
              }`}>
                <h3 className={`font-semibold mb-1 ${
                  formData.artStyle === style.id ? 'text-purple-900' : 'text-gray-900'
                }`}>
                  {style.title}
                </h3>
                <p className={`text-xs ${
                  formData.artStyle === style.id ? 'text-purple-700' : 'text-gray-600'
                }`}>
                  {style.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Style Info */}
      {formData.artStyle && (
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg overflow-hidden">
              <img
                src={artStyles.find(s => s.id === formData.artStyle)?.imageUrl}
                alt="Selected style"
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h4 className="font-medium text-purple-900">Geselecteerde Stijl</h4>
              <p className="text-purple-700 text-sm">
                {artStyles.find(s => s.id === formData.artStyle)?.title}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
