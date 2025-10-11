
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Globe, Plus, Trash2, Edit, Check, X } from 'lucide-react';
import { toast } from 'sonner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface WordPressSite {
  id: string;
  name: string;
  url: string;
  username: string;
  language: string;
  country?: string;
  isActive: boolean;
  createdAt: string;
  _count?: {
    blogPosts: number;
  };
}

export default function WordPressPage() {
  const [sites, setSites] = useState<WordPressSite[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [username, setUsername] = useState('');
  const [appPassword, setAppPassword] = useState('');
  const [language, setLanguage] = useState('en');
  const [country, setCountry] = useState('');

  useEffect(() => {
    fetchSites();
  }, []);

  const fetchSites = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/wordpress/sites');
      const data = await response.json();
      if (data.success) {
        setSites(data.sites);
      }
    } catch (error) {
      console.error('Error fetching sites:', error);
      toast.error('Failed to load WordPress sites');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddSite = async () => {
    if (!name || !url || !username || !appPassword) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/wordpress/sites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          url,
          username,
          appPassword,
          language,
          country: country || null
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('WordPress site added successfully!');
        setIsDialogOpen(false);
        resetForm();
        fetchSites();
      } else {
        toast.error(data.error || 'Failed to add site');
      }
    } catch (error) {
      console.error('Error adding site:', error);
      toast.error('Failed to add WordPress site');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteSite = async (id: string, siteName: string) => {
    if (!confirm(`Are you sure you want to delete "${siteName}"?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/wordpress/sites/${id}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Site deleted successfully');
        fetchSites();
      } else {
        toast.error(data.error || 'Failed to delete site');
      }
    } catch (error) {
      console.error('Error deleting site:', error);
      toast.error('Failed to delete site');
    }
  };

  const resetForm = () => {
    setName('');
    setUrl('');
    setUsername('');
    setAppPassword('');
    setLanguage('en');
    setCountry('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              🌐 WordPress Sites
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Manage your WordPress sites and publish content
            </p>
          </div>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                Add WordPress Site
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Add WordPress Site</DialogTitle>
                <DialogDescription>
                  Connect a new WordPress site to publish content
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label>Site Name *</Label>
                  <Input
                    placeholder="My Blog"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>

                <div>
                  <Label>Site URL *</Label>
                  <Input
                    placeholder="https://yourblog.com"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                </div>

                <div>
                  <Label>Username *</Label>
                  <Input
                    placeholder="admin"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>

                <div>
                  <Label>Application Password *</Label>
                  <Input
                    type="password"
                    placeholder="xxxx xxxx xxxx xxxx xxxx xxxx"
                    value={appPassword}
                    onChange={(e) => setAppPassword(e.target.value)}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Create an Application Password in WordPress (Users → Profile → Application Passwords)
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Language</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="nl">Nederlands</SelectItem>
                        <SelectItem value="de">Deutsch</SelectItem>
                        <SelectItem value="fr">Français</SelectItem>
                        <SelectItem value="es">Español</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Country (Optional)</Label>
                    <Input
                      placeholder="US"
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      maxLength={2}
                    />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleAddSite}
                  disabled={isSubmitting}
                  className="bg-gradient-to-r from-purple-600 to-blue-600"
                >
                  {isSubmitting ? 'Adding...' : 'Add Site'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading WordPress sites...</p>
          </div>
        ) : sites.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Globe className="h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">No WordPress Sites</h3>
              <p className="text-gray-600 mb-4 text-center">
                Add your first WordPress site to start publishing content
              </p>
              <Button
                onClick={() => setIsDialogOpen(true)}
                className="bg-gradient-to-r from-purple-600 to-blue-600"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Your First Site
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sites.map((site) => (
              <Card key={site.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Globe className="h-5 w-5 text-purple-600" />
                      <CardTitle className="text-lg">{site.name}</CardTitle>
                    </div>
                    {site.isActive ? (
                      <Check className="h-5 w-5 text-green-500" />
                    ) : (
                      <X className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                  <CardDescription className="truncate">{site.url}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Language:</span>
                      <span className="font-medium">{site.language.toUpperCase()}</span>
                    </div>
                    {site.country && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Country:</span>
                        <span className="font-medium">{site.country.toUpperCase()}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-gray-600">Posts:</span>
                      <span className="font-medium">{site._count?.blogPosts || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Added:</span>
                      <span className="font-medium">
                        {new Date(site.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => window.open(site.url, '_blank')}
                    >
                      <Globe className="h-4 w-4 mr-1" />
                      Visit
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => handleDeleteSite(site.id, site.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
