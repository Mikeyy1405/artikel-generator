
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Download, Play, Video, Calendar, Users, Clock, Music, Type, Palette, Settings, Sparkles, Loader2, Pencil, Trash2, X, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { toast } from 'sonner';

interface SeriesDetail {
  id: string;
  name: string;
  format: string;
  presetType?: string;
  customFormat?: string;
  niche: string;
  language: string;
  voice: string;
  voiceStyle: string;
  backgroundMusic?: string;
  musicDescription?: string;
  artStyle: string;
  captionStyle: string;
  duration: string;
  videoCount: number;
  publishSchedule?: string;
  publishTime?: string;
  createdAt: string;
  videos: {
    id: string;
    title: string;
    thumbnailUrl: string;
    duration: string;
    status: string;
    createdAt: string;
    videoUrl?: string;
  }[];
}

interface ProgressInfo {
  generating: boolean;
  currentStep?: string;
  currentVideo?: number;
  totalVideos?: number;
  percentage?: number;
  message?: string;
}

export default function SeriesDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [series, setSeries] = useState<SeriesDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState<ProgressInfo>({ generating: false });
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState<Partial<SeriesDetail>>({});
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteVideoId, setDeleteVideoId] = useState<string | null>(null);
  const [deleteSeriesDialogOpen, setDeleteSeriesDialogOpen] = useState(false);

  useEffect(() => {
    const fetchSeries = async () => {
      try {
        const response = await fetch(`/api/series/${params.id}`);
        if (response.ok) {
          const data = await response.json();
          setSeries(data);
          setEditData(data);
        } else if (response.status === 404) {
          router.push('/dashboard');
        }
      } catch (error) {
        console.error('Error fetching series:', error);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchSeries();
    }
  }, [params.id, router]);

  // Poll for progress updates when generating
  useEffect(() => {
    if (!generating || !params.id) return;

    const pollProgress = async () => {
      try {
        const response = await fetch(`/api/series/${params.id}/progress`);
        if (response.ok) {
          const data = await response.json();
          setProgress(data);
        }
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    };

    // Poll every 2 seconds
    const interval = setInterval(pollProgress, 2000);
    
    // Initial poll
    pollProgress();

    return () => clearInterval(interval);
  }, [generating, params.id]);

  const handleDownload = async (videoId: string, title: string) => {
    try {
      toast.info('Video downloaden...', {
        description: 'De download start zo meteen.',
      });

      const response = await fetch(`/api/videos/${videoId}/download`);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      // Get the blob from response
      const blob = await response.blob();
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('Video gedownload!', {
        description: 'De video is opgeslagen op je apparaat.',
      });
    } catch (error) {
      console.error('Error downloading video:', error);
      toast.error('Download mislukt', {
        description: 'Er ging iets mis bij het downloaden van de video.',
      });
    }
  };

  const handleDeleteVideo = async (videoId: string) => {
    try {
      const response = await fetch(`/api/videos/${videoId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('Video verwijderd!', {
          description: 'De video is succesvol verwijderd.',
        });
        
        // Refresh the series data
        const refreshResponse = await fetch(`/api/series/${params.id}`);
        if (refreshResponse.ok) {
          const refreshedData = await refreshResponse.json();
          setSeries(refreshedData);
        }
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Error deleting video:', error);
      toast.error('Verwijderen mislukt', {
        description: 'Er ging iets mis bij het verwijderen van de video.',
      });
    } finally {
      setDeleteVideoId(null);
      setDeleteDialogOpen(false);
    }
  };

  const handleDeleteSeries = async () => {
    try {
      const response = await fetch(`/api/series/${params.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('Serie verwijderd!', {
          description: 'De serie is succesvol verwijderd.',
        });
        router.push('/dashboard');
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Error deleting series:', error);
      toast.error('Verwijderen mislukt', {
        description: 'Er ging iets mis bij het verwijderen van de serie.',
      });
    } finally {
      setDeleteSeriesDialogOpen(false);
    }
  };

  const handleSaveEdit = async () => {
    try {
      const response = await fetch(`/api/series/${params.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editData),
      });

      if (response.ok) {
        const updatedSeries = await response.json();
        setSeries(updatedSeries);
        setEditMode(false);
        toast.success('Serie bijgewerkt!', {
          description: 'De wijzigingen zijn succesvol opgeslagen.',
        });
      } else {
        throw new Error('Update failed');
      }
    } catch (error) {
      console.error('Error updating series:', error);
      toast.error('Bijwerken mislukt', {
        description: 'Er ging iets mis bij het opslaan van de wijzigingen.',
      });
    }
  };

  const handleGenerateAllVideos = async () => {
    setGenerating(true);
    toast.info('Video generatie gestart...', {
      description: 'Dit kan enkele minuten duren. Je krijgt een melding wanneer het klaar is.',
    });

    try {
      const response = await fetch('/api/series/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ seriesId: params.id }),
      });

      if (response.ok) {
        const data = await response.json();
        toast.success('Video\'s succesvol gegenereerd!', {
          description: `${data.videos.length} video's zijn klaar om te downloaden.`,
        });
        
        // Refresh the series data
        const refreshResponse = await fetch(`/api/series/${params.id}`);
        if (refreshResponse.ok) {
          const refreshedData = await refreshResponse.json();
          setSeries(refreshedData);
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Video generation failed');
      }
    } catch (error) {
      console.error('Error generating videos:', error);
      toast.error('Fout bij video generatie', {
        description: error instanceof Error ? error.message : 'Er is iets misgegaan. Probeer het opnieuw.',
      });
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateNextVideo = async () => {
    setGenerating(true);
    toast.info('Video wordt gegenereerd...', {
      description: 'Dit kan enkele minuten duren. Houd deze pagina open.',
    });

    try {
      const response = await fetch(`/api/series/${params.id}/generate-next-video`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        toast.success('Video succesvol gegenereerd!', {
          description: `Video ${data.progress.current} van ${data.progress.total} is klaar.`,
        });
        
        // Refresh the series data
        const refreshResponse = await fetch(`/api/series/${params.id}`);
        if (refreshResponse.ok) {
          const refreshedData = await refreshResponse.json();
          setSeries(refreshedData);
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Video generation failed');
      }
    } catch (error) {
      console.error('Error generating video:', error);
      toast.error('Fout bij video generatie', {
        description: error instanceof Error ? error.message : 'Er is iets misgegaan. Probeer het opnieuw.',
      });
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto"></div>
          <p className="text-gray-600 mt-4">Serie laden...</p>
        </div>
      </div>
    );
  }

  if (!series) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50 flex items-center justify-center">
        <div className="text-center">
          <Video className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Serie niet gevonden</h3>
          <Link href="/dashboard">
            <Button variant="outline">Terug naar Dashboard</Button>
          </Link>
        </div>
      </div>
    );
  }

  const formatType = () => {
    if (series.format === 'preset') {
      return series.presetType?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
    }
    return series.customFormat?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-purple-100">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center space-x-3">
              <ArrowLeft className="w-5 h-5 text-gray-600" />
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-violet-600 rounded-lg flex items-center justify-center">
                <Video className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent">
                FacelessVideo
              </h1>
            </Link>
          </div>
        </div>
      </header>

      <main className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Progress Indicator */}
          {generating && progress.generating && (
            <div className="mb-6">
              <Card className="bg-gradient-to-r from-purple-50 to-violet-50 border-purple-200">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-4">
                    <Loader2 className="w-8 h-8 text-purple-600 animate-spin" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        Video wordt gegenereerd...
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {progress.message || 'Bezig met genereren...'}
                      </p>
                      {progress.percentage !== undefined && (
                        <div className="w-full bg-white rounded-full h-2.5">
                          <div 
                            className="bg-gradient-to-r from-purple-600 to-violet-600 h-2.5 rounded-full transition-all duration-500"
                            style={{ width: `${progress.percentage}%` }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Series Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {editMode ? (
                  <Input
                    value={editData.name || ''}
                    onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                    className="text-3xl font-bold border-2 border-purple-300 focus:border-purple-500"
                  />
                ) : (
                  <>
                    <h2 className="text-3xl font-bold text-gray-900">{series.name}</h2>
                    <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                      {formatType()}
                    </Badge>
                  </>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {editMode ? (
                  <>
                    <Button
                      onClick={() => {
                        setEditMode(false);
                        setEditData(series);
                      }}
                      variant="outline"
                    >
                      <X className="w-4 h-4 mr-2" />
                      Annuleren
                    </Button>
                    <Button
                      onClick={handleSaveEdit}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Opslaan
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      onClick={() => setEditMode(true)}
                      variant="outline"
                      className="border-purple-600 text-purple-600 hover:bg-purple-50"
                    >
                      <Pencil className="w-4 h-4 mr-2" />
                      Bewerken
                    </Button>
                    <Button
                      onClick={() => setDeleteSeriesDialogOpen(true)}
                      variant="outline"
                      className="border-red-600 text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Verwijderen
                    </Button>
                    {series.videos.length < series.videoCount && (
                      <Button
                        onClick={handleGenerateNextVideo}
                        disabled={generating}
                        variant="outline"
                        className="border-purple-600 text-purple-600 hover:bg-purple-50"
                      >
                        {generating ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Bezig...
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            Volgende Video
                          </>
                        )}
                      </Button>
                    )}
                    <Button
                      onClick={handleGenerateAllVideos}
                      disabled={generating || series.videos.length >= series.videoCount}
                      className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700"
                    >
                      {generating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Bezig met genereren...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          {series.videos.length > 0 ? 'Genereer Resterende' : 'Genereer Alle Video\'s'}
                        </>
                      )}
                    </Button>
                  </>
                )}
              </div>
            </div>
            {editMode ? (
              <Input
                value={editData.niche || ''}
                onChange={(e) => setEditData({ ...editData, niche: e.target.value })}
                className="border-2 border-purple-300 focus:border-purple-500"
                placeholder="Niche"
              />
            ) : (
              <p className="text-gray-600">{series.niche}</p>
            )}
          </div>

          <div className="grid gap-8 lg:grid-cols-3">
            {/* Configuration Panel */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="w-5 h-5" />
                    <span>Configuratie</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {editMode ? (
                    <div className="space-y-4">
                      <div>
                        <Label>Taal</Label>
                        <Select
                          value={editData.language || ''}
                          onValueChange={(value) => setEditData({ ...editData, language: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Dutch">Dutch</SelectItem>
                            <SelectItem value="English">English</SelectItem>
                            <SelectItem value="Spanish">Spanish</SelectItem>
                            <SelectItem value="French">French</SelectItem>
                            <SelectItem value="German">German</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Stem Stijl</Label>
                        <Select
                          value={editData.voiceStyle || ''}
                          onValueChange={(value) => setEditData({ ...editData, voiceStyle: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Male 1">Male 1</SelectItem>
                            <SelectItem value="Male 2">Male 2</SelectItem>
                            <SelectItem value="Female 1">Female 1</SelectItem>
                            <SelectItem value="Female 2">Female 2</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Art Style</Label>
                        <Select
                          value={editData.artStyle || ''}
                          onValueChange={(value) => setEditData({ ...editData, artStyle: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Realistic">Realistic</SelectItem>
                            <SelectItem value="Cinematic">Cinematic</SelectItem>
                            <SelectItem value="Animated">Animated</SelectItem>
                            <SelectItem value="Minimalist">Minimalist</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Ondertitels</Label>
                        <Select
                          value={editData.captionStyle || ''}
                          onValueChange={(value) => setEditData({ ...editData, captionStyle: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Bold">Bold</SelectItem>
                            <SelectItem value="Subtle">Subtle</SelectItem>
                            <SelectItem value="Animated">Animated</SelectItem>
                            <SelectItem value="None">None</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  ) : (
                    <div className="grid gap-3 text-sm">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Users className="w-4 h-4 text-purple-600" />
                          <span className="text-gray-600">Taal:</span>
                        </div>
                        <span className="font-medium">{series.language}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Play className="w-4 h-4 text-purple-600" />
                          <span className="text-gray-600">Stem:</span>
                        </div>
                        <span className="font-medium">{series.voiceStyle}</span>
                      </div>
                      {series.backgroundMusic && (
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Music className="w-4 h-4 text-purple-600" />
                            <span className="text-gray-600">Muziek:</span>
                          </div>
                          <span className="font-medium">Ja</span>
                        </div>
                      )}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Palette className="w-4 h-4 text-purple-600" />
                          <span className="text-gray-600">Art Style:</span>
                        </div>
                        <span className="font-medium">{series.artStyle}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Type className="w-4 h-4 text-purple-600" />
                          <span className="text-gray-600">Ondertitels:</span>
                        </div>
                        <span className="font-medium">{series.captionStyle}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-purple-600" />
                          <span className="text-gray-600">Duur:</span>
                        </div>
                        <span className="font-medium">
                          {series.duration === 'short' ? '30-60s' : '3-5min'}
                        </span>
                      </div>
                      {series.publishSchedule && (
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Calendar className="w-4 h-4 text-purple-600" />
                            <span className="text-gray-600">Schema:</span>
                          </div>
                          <span className="font-medium">
                            {series.publishSchedule === 'daily' ? 'Dagelijks' : 
                             series.publishSchedule === 'weekly' ? 'Wekelijks' :
                             series.publishSchedule === 'every-2-days' ? 'Om de 2 dagen' : 'Handmatig'}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Videos Grid */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Video className="w-5 h-5" />
                      <span>Gegenereerde Video's ({series.videos.length}/{series.videoCount})</span>
                    </div>
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-purple-600 to-violet-600 h-2 rounded-full transition-all duration-500"
                        style={{ 
                          width: `${(series.videos.length / series.videoCount) * 100}%` 
                        }}
                      />
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {series.videos.length === 0 ? (
                    <div className="text-center py-12">
                      <Video className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Geen video's gegenereerd</h3>
                      <p className="text-gray-600 mb-4">Klik op "Volgende Video" of "Genereer Alle Video's" om te beginnen met het genereren van video's</p>
                      <Button
                        onClick={handleGenerateNextVideo}
                        disabled={generating}
                        className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700"
                      >
                        {generating ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Bezig met genereren...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4 mr-2" />
                            Start Video Generatie
                          </>
                        )}
                      </Button>
                    </div>
                  ) : (
                    <div className="grid gap-4 md:grid-cols-2">
                      {series.videos.map((video) => (
                        <div key={video.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                          <div className="aspect-video relative bg-gray-100">
                            <img
                              src={video.thumbnailUrl}
                              alt={video.title}
                              className="w-full h-full object-cover"
                            />
                            <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                              {video.duration}
                            </div>
                          </div>
                          <div className="p-4">
                            <h4 className="font-medium text-gray-900 mb-2 truncate">{video.title}</h4>
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="outline" className="text-green-600 border-green-200">
                                {video.status === 'generated' ? 'Gereed' : 'Genereren...'}
                              </Badge>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button
                                size="sm"
                                onClick={() => handleDownload(video.id, video.title)}
                                className="flex-1 bg-purple-600 hover:bg-purple-700"
                                disabled={!video.videoUrl}
                              >
                                <Download className="w-4 h-4 mr-2" />
                                Download
                              </Button>
                              <Button
                                size="sm"
                                onClick={() => {
                                  setDeleteVideoId(video.id);
                                  setDeleteDialogOpen(true);
                                }}
                                variant="outline"
                                className="border-red-600 text-red-600 hover:bg-red-50"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                            <p className="text-xs text-gray-500 mt-2">
                              Aangemaakt: {new Date(video.createdAt).toLocaleDateString('nl-NL')}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>

      {/* Delete Video Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Video verwijderen?</AlertDialogTitle>
            <AlertDialogDescription>
              Weet je zeker dat je deze video wilt verwijderen? Deze actie kan niet ongedaan worden gemaakt.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuleren</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteVideoId && handleDeleteVideo(deleteVideoId)}
              className="bg-red-600 hover:bg-red-700"
            >
              Verwijderen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Series Confirmation Dialog */}
      <AlertDialog open={deleteSeriesDialogOpen} onOpenChange={setDeleteSeriesDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Serie verwijderen?</AlertDialogTitle>
            <AlertDialogDescription>
              Weet je zeker dat je deze serie en alle bijbehorende video's wilt verwijderen? Deze actie kan niet ongedaan worden gemaakt.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuleren</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteSeries}
              className="bg-red-600 hover:bg-red-700"
            >
              Verwijderen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
