
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Plus, Video, Calendar, Play, Users, Clock, MoreVertical, Trash2, Pencil, FileText, Globe, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
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

interface Series {
  id: string;
  name: string;
  format: string;
  presetType?: string;
  customFormat?: string;
  niche: string;
  language: string;
  duration: string;
  videoCount: number;
  publishSchedule?: string;
  publishTime?: string;
  createdAt: string;
  videos: any[];
}

interface BlogPost {
  id: string;
  title: string;
  contentType: string;
  status: string;
  wordCount?: number;
  createdAt: string;
}

interface WordPressSite {
  id: string;
  name: string;
  url: string;
  _count?: {
    blogPosts: number;
  };
}

export default function DashboardPage() {
  const router = useRouter();
  const [series, setSeries] = useState<Series[]>([]);
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([]);
  const [wordPressSites, setWordPressSites] = useState<WordPressSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [seriesIdToDelete, setSeriesIdToDelete] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('videos');

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    await Promise.all([
      fetchSeries(),
      fetchBlogPosts(),
      fetchWordPressSites()
    ]);
    setLoading(false);
  };

  const fetchSeries = async () => {
    try {
      const response = await fetch('/api/series');
      if (response.ok) {
        const data = await response.json();
        setSeries(data);
      }
    } catch (error) {
      console.error('Error fetching series:', error);
    }
  };

  const fetchBlogPosts = async () => {
    try {
      const response = await fetch('/api/blog/posts');
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setBlogPosts(data.posts);
        }
      }
    } catch (error) {
      console.error('Error fetching blog posts:', error);
    }
  };

  const fetchWordPressSites = async () => {
    try {
      const response = await fetch('/api/wordpress/sites');
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setWordPressSites(data.sites);
        }
      }
    } catch (error) {
      console.error('Error fetching WordPress sites:', error);
    }
  };

  const handleDeleteSeries = async (seriesId: string) => {
    try {
      const response = await fetch(`/api/series/${seriesId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('Serie verwijderd!', {
          description: 'De serie is succesvol verwijderd.',
        });
        
        // Refresh the series list
        fetchSeries();
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Error deleting series:', error);
      toast.error('Verwijderen mislukt', {
        description: 'Er ging iets mis bij het verwijderen van de serie.',
      });
    } finally {
      setDeleteDialogOpen(false);
      setSeriesIdToDelete(null);
    }
  };

  const formatType = (s: Series) => {
    if (s.format === 'preset') {
      return s.presetType?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
    }
    return s.customFormat?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
  };

  const getNextPublishTime = (schedule?: string, time?: string) => {
    if (!schedule || schedule === 'manual') return null;
    
    const now = new Date();
    let nextDate = new Date(now);
    
    switch (schedule) {
      case 'daily':
        nextDate.setDate(now.getDate() + 1);
        break;
      case 'every-2-days':
        nextDate.setDate(now.getDate() + 2);
        break;
      case 'weekly':
        nextDate.setDate(now.getDate() + 7);
        break;
    }
    
    if (time) {
      const [hours, minutes] = time.split(':').map(Number);
      nextDate.setHours(hours, minutes, 0, 0);
    }
    
    return nextDate.toLocaleDateString('nl-NL', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-purple-100">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-violet-600 rounded-lg flex items-center justify-center">
                <Video className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent">
                FacelessVideo
              </h1>
            </Link>
            <Link href="/wizard">
              <Button className="gradient-button">
                <Plus className="w-4 h-4 mr-2" />
                Nieuwe Serie
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">📊 Multi-Channel Content Dashboard</h2>
            <p className="text-gray-600">Beheer video's, blogs en WordPress sites vanaf één plek</p>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="border-purple-100">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Video Series</p>
                    <p className="text-3xl font-bold text-purple-600">{series.length}</p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Video className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {series.reduce((sum, s) => sum + (s.videos?.length || 0), 0)} totale video's
                </p>
              </CardContent>
            </Card>

            <Card className="border-blue-100">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Blog Posts</p>
                    <p className="text-3xl font-bold text-blue-600">{blogPosts.length}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {blogPosts.filter(p => p.status === 'published').length} gepubliceerd
                </p>
              </CardContent>
            </Card>

            <Card className="border-green-100">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">WordPress Sites</p>
                    <p className="text-3xl font-bold text-green-600">{wordPressSites.length}</p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Globe className="w-6 h-6 text-green-600" />
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {wordPressSites.filter(s => s._count && s._count.blogPosts > 0).length} actief
                </p>
              </CardContent>
            </Card>

            <Card className="border-orange-100">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Totale Content</p>
                    <p className="text-3xl font-bold text-orange-600">
                      {series.reduce((sum, s) => sum + (s.videos?.length || 0), 0) + blogPosts.length}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Video's + Artikelen
                </p>
              </CardContent>
            </Card>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto"></div>
              <p className="text-gray-600 mt-4">Content laden...</p>
            </div>
          ) : (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full max-w-md grid-cols-2 mb-6">
                <TabsTrigger 
                  value="videos" 
                  className="flex items-center gap-2"
                  onClick={() => setActiveTab('videos')}
                >
                  <Video className="h-4 w-4" />
                  Video's ({series.length})
                </TabsTrigger>
                <TabsTrigger 
                  value="blog" 
                  className="flex items-center gap-2"
                  onClick={() => setActiveTab('blog')}
                >
                  <FileText className="h-4 w-4" />
                  Blog ({blogPosts.length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="videos" className="mt-6">
                {series.length === 0 ? (
                  <Card className="text-center py-12">
                    <CardContent>
                      <Video className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">Geen video series</h3>
                      <p className="text-gray-600 mb-6">Maak je eerste video serie om te beginnen</p>
                      <Link href="/wizard">
                        <Button className="gradient-button">
                          <Plus className="w-4 h-4 mr-2" />
                          Eerste Serie Maken
                        </Button>
                      </Link>
                    </CardContent>
                  </Card>
                ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {series.map((s) => (
                <Card key={s.id} className="hover:shadow-lg transition-shadow duration-200 border-purple-100 relative">
                  <div className="absolute top-3 right-3 z-10">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 hover:bg-purple-100"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/dashboard/series/${s.id}`);
                          }}
                        >
                          <Pencil className="mr-2 h-4 w-4" />
                          <span>Bewerken</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            setSeriesIdToDelete(s.id);
                            setDeleteDialogOpen(true);
                          }}
                          className="text-red-600"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          <span>Verwijderen</span>
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                  <Link href={`/dashboard/series/${s.id}`}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between pr-8">
                        <CardTitle className="text-lg text-gray-900 truncate">{s.name}</CardTitle>
                        <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                          {formatType(s)}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{s.niche}</p>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center space-x-2">
                          <Users className="w-4 h-4 text-purple-600" />
                          <span className="text-gray-600">{s.language}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Play className="w-4 h-4 text-purple-600" />
                          <span className="text-gray-600">
                            {s.duration === 'short' ? '30-60s' : '3-5min'}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Video's: {s.videos?.length || 0}/{s.videoCount}</span>
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-purple-600 to-violet-600 h-2 rounded-full"
                            style={{ 
                              width: `${((s.videos?.length || 0) / s.videoCount) * 100}%` 
                            }}
                          />
                        </div>
                      </div>

                      {getNextPublishTime(s.publishSchedule, s.publishTime) && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Calendar className="w-4 h-4" />
                          <span>Volgende: {getNextPublishTime(s.publishSchedule, s.publishTime)}</span>
                        </div>
                      )}

                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Aangemaakt: {new Date(s.createdAt).toLocaleDateString('nl-NL')}</span>
                        <Badge variant="outline" className="text-green-600 border-green-200">
                          Actief
                        </Badge>
                      </div>
                    </CardContent>
                  </Link>
                </Card>
              ))}
            </div>
                )}
              </TabsContent>

              <TabsContent value="blog" className="mt-6">
                {blogPosts.length === 0 ? (
                  <Card className="text-center py-12">
                    <CardContent>
                      <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">Geen blog posts</h3>
                      <p className="text-gray-600 mb-6">Maak je eerste blog artikel om te beginnen</p>
                      <Link href="/blog">
                        <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                          <Plus className="w-4 h-4 mr-2" />
                          Eerste Artikel Maken
                        </Button>
                      </Link>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {blogPosts.slice(0, 10).map((post) => (
                      <Card key={post.id} className="hover:shadow-lg transition-shadow">
                        <CardContent className="py-4">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge className={
                                  post.status === 'published' ? 'bg-green-500' :
                                  post.status === 'draft' ? 'bg-yellow-500' :
                                  'bg-blue-500'
                                }>
                                  {post.status}
                                </Badge>
                                <Badge variant="outline">
                                  {post.contentType === 'seo' ? '🎯 SEO' :
                                   post.contentType === 'perplexity' ? '🔍 Research' :
                                   post.contentType === 'youtube' ? '🎥 YouTube' :
                                   '📝 List'}
                                </Badge>
                                {post.wordCount && (
                                  <Badge variant="outline">{post.wordCount} words</Badge>
                                )}
                              </div>
                              <h4 className="text-lg font-semibold text-gray-900">{post.title}</h4>
                              <p className="text-sm text-gray-500 mt-1">
                                {new Date(post.createdAt).toLocaleDateString('nl-NL')}
                              </p>
                            </div>
                            <Link href="/blog/posts">
                              <Button size="sm" variant="outline">
                                Bekijk →
                              </Button>
                            </Link>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    {blogPosts.length > 10 && (
                      <Link href="/blog/posts">
                        <Button variant="outline" className="w-full">
                          Bekijk alle {blogPosts.length} artikelen
                        </Button>
                      </Link>
                    )}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          )}
        </div>
      </main>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
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
              onClick={() => seriesIdToDelete && handleDeleteSeries(seriesIdToDelete)}
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
