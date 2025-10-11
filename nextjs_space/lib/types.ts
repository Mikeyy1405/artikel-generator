
export interface WizardStep {
  id: number;
  title: string;
  completed: boolean;
}

export interface SeriesFormData {
  // Step 1: Format & Niche
  format: 'preset' | 'custom';
  presetType?: 'scary-stories' | 'history' | 'true-crime';
  customFormat?: 'storytelling' | 'what-if' | '5-things' | 'random-fact';
  niche: string;
  
  // Step 2: Language & Voice
  language: string;
  voice: string;
  voiceStyle: string;
  
  // Step 3: Background Music
  backgroundMusic?: string;
  musicDescription?: string;
  
  // Step 4: Art Style
  artStyle: string;
  
  // Step 5: Caption Style
  captionStyle: string;
  
  // Step 6: Video Duration
  duration: 'short' | 'long';
  
  // Step 7: Series Details
  seriesName: string;
  videoCount: number;
  publishSchedule?: string;
  publishTime?: string;
}

export interface PresetOption {
  id: string;
  title: string;
  description: string;
  popularity: string;
}

export interface CustomFormat {
  id: string;
  title: string;
}

export interface Voice {
  id: string;
  name: string;
  gender: string;
  description: string;
}

export interface MusicOption {
  id: string;
  title: string;
  description: string;
}

export interface ArtStyleOption {
  id: string;
  title: string;
  description?: string;
  imageUrl: string;
}

export interface CaptionStyleOption {
  id: string;
  title: string;
  previewText: string;
  className: string;
}
