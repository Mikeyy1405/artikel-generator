

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Save, Send, Copy, Download, ExternalLink, Globe, FileText, Link as LinkIcon } from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';

interface BlogPost {
  id: string;
  title: string;
  content: string;
  htmlContent?: string;
  contentType: string;
  keywords?: string;
  seoTitle?: string;
  metaDescription?: string;
  wordCount?: number;
  status: string;
  publishedUrl?: string;
  createdAt: string;
  siteId?: string;
  wordpress_sites?: {
    id: string;
    name: string;
    url: string;
  };
}

interface WordPressSite {
  id: string;
  name: string;
  url: string;
}

interface InternalLink {
  postId: string;
  title: string;
}

export default function BlogPostDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [post, setPost] = useState<BlogPost | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [seoTitle, setSeoTitle] = useState('');
  const [metaDescription, setMetaDescription] = useState('');
  const [keywords, setKeywords] = useState('');
  const [selectedSiteId, setSelectedSiteId] = useState('');
  const [sites, setSites] = useState<WordPressSite[]>([]);
  const [allPosts, setAllPosts] = useState<InternalLink[]>([]);
  const [showLinkSelector, setShowLinkSelector] = useState(false);

  useEffect(() => {
    fetchPost();
    fetchWordPressSites();
    fetchAllPosts();
  }, [params.id]);

  const fetchPost = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/blog/posts/${params.id}`);
      const data = await response.json();
      if (data.success) {
        setPost(data.post);
        setTitle(data.post.title);
        setContent(data.post.htmlContent || data.post.content);
        setSeoTitle(data.post.seoTitle || '');
        setMetaDescription(data.post.metaDescription || '');
        setKeywords(data.post.keywords || '');
        setSelectedSiteId(data.post.siteId || '');
      } else {
        toast.error('Failed to load blog post');
        router.push('/blog/posts');
      }
    } catch (error) {
      console.error('Error fetching post:', error);
      toast.error('Failed to load blog post');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchWordPressSites = async () => {
    try {
      const response = await fetch('/api/wordpress/sites');
      const data = await response.json();
      if (data.success) {
        setSites(data.sites);
      }
    } catch (error) {
      console.error('Error fetching sites:', error);
    }
  };

  const fetchAllPosts = async () => {
    try {
      const response = await fetch('/api/blog/posts');
      const data = await response.json();
      if (data.success) {
        setAllPosts(
          data.posts
            .filter((p: BlogPost) => p.id !== params.id && p.status === 'published')
            .map((p: BlogPost) => ({ postId: p.id, title: p.title }))
        );
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const savePost = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(`/api/blog/posts/${params.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          content,
          htmlContent: content,
          seoTitle,
          metaDescription,
          keywords,
          siteId: selectedSiteId || null,
          wordCount: content.replace(/<[^>]*>/g, '').split(/\s+/).filter(w => w.length > 0).length
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Post saved successfully!');
        setPost(data.post);
      } else {
        toast.error(data.error || 'Failed to save post');
      }
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Failed to save post');
    } finally {
      setIsSaving(false);
    }
  };

  const publishToWordPress = async () => {
    if (!selectedSiteId) {
      toast.error('Please select a WordPress site');
      return;
    }

    try {
      const response = await fetch('/api/blog/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ postId: params.id })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Published to WordPress successfully!');
        if (data.wordpressUrl) {
          window.open(data.wordpressUrl, '_blank');
        }
        fetchPost(); // Refresh post data
      } else {
        toast.error(data.error || 'Failed to publish');
      }
    } catch (error) {
      console.error('Publish error:', error);
      toast.error('Failed to publish to WordPress');
    }
  };

  const insertInternalLink = (linkPostId: string) => {
    const linkedPost = allPosts.find(p => p.postId === linkPostId);
    if (!linkedPost) return;

    const linkHtml = `<a href="/blog/${linkPostId}" class="internal-link">${linkedPost.title}</a>`;
    setContent(content + ` ${linkHtml} `);
    setShowLinkSelector(false);
    toast.success('Internal link added!');
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(content);
    toast.success('Content copied to clipboard!');
  };

  const downloadHTML = () => {
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title || 'article'}.html`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('HTML file downloaded!');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading blog post...</p>
        </div>
      </div>
    );
  }

  if (!post) {
    return null;
  }

  const wordCount = content.replace(/<[^>]*>/g, '').split(/\s+/).filter(w => w.length > 0).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/blog/posts">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Posts
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold">Edit Blog Post</h1>
              <div className="flex items-center gap-2 mt-2">
                <Badge>{post.contentType}</Badge>
                <Badge variant="outline">{wordCount} words</Badge>
                <Badge className={post.status === 'published' ? 'bg-green-500' : 'bg-yellow-500'}>
                  {post.status}
                </Badge>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={copyToClipboard}>
              <Copy className="h-4 w-4 mr-2" />
              Copy
            </Button>
            <Button variant="outline" onClick={downloadHTML}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button onClick={savePost} disabled={isSaving}>
              <Save className="h-4 w-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save'}
            </Button>
            <Button 
              onClick={publishToWordPress} 
              disabled={!selectedSiteId}
              className="bg-gradient-to-r from-purple-600 to-blue-600"
            >
              <Send className="h-4 w-4 mr-2" />
              Publish
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* SEO Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">SEO Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Title</Label>
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Post title"
                  />
                </div>

                <div>
                  <Label>SEO Title (max 55 chars)</Label>
                  <Input
                    value={seoTitle}
                    onChange={(e) => setSeoTitle(e.target.value)}
                    placeholder="SEO optimized title"
                    maxLength={55}
                  />
                  <p className="text-xs text-gray-500 mt-1">{seoTitle.length}/55</p>
                </div>

                <div>
                  <Label>Meta Description (max 130 chars)</Label>
                  <Textarea
                    value={metaDescription}
                    onChange={(e) => setMetaDescription(e.target.value)}
                    placeholder="SEO meta description"
                    maxLength={130}
                    rows={3}
                  />
                  <p className="text-xs text-gray-500 mt-1">{metaDescription.length}/130</p>
                </div>

                <div>
                  <Label>Keywords (comma separated)</Label>
                  <Input
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="keyword1, keyword2, keyword3"
                  />
                </div>

                <div>
                  <Label>WordPress Site</Label>
                  <Select value={selectedSiteId || "no-site"} onValueChange={(val) => setSelectedSiteId(val === "no-site" ? "" : val)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a site..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="no-site">No site</SelectItem>
                      {sites.map((site) => (
                        <SelectItem key={site.id} value={site.id}>
                          {site.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Internal Links */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <LinkIcon className="h-5 w-5" />
                  Internal Links (Sitemap)
                </CardTitle>
                <CardDescription>
                  Add links to other published posts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {allPosts.length === 0 ? (
                  <p className="text-sm text-gray-500">No published posts available for linking</p>
                ) : (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => setShowLinkSelector(!showLinkSelector)}
                    >
                      <LinkIcon className="h-4 w-4 mr-2" />
                      Add Internal Link
                    </Button>

                    {showLinkSelector && (
                      <div className="border rounded-lg p-2 mt-2 max-h-60 overflow-y-auto">
                        {allPosts.map((linkPost) => (
                          <button
                            key={linkPost.postId}
                            onClick={() => insertInternalLink(linkPost.postId)}
                            className="w-full text-left text-sm p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                          >
                            {linkPost.title}
                          </button>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>

            {/* Post Info */}
            {post.publishedUrl && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Published</CardTitle>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => window.open(post.publishedUrl, '_blank')}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View on WordPress
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Main Editor */}
          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Content Editor</CardTitle>
                <CardDescription>
                  Edit your content in HTML or preview mode
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="preview" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="preview">Preview</TabsTrigger>
                    <TabsTrigger value="html">HTML Code</TabsTrigger>
                  </TabsList>

                  <TabsContent value="preview" className="min-h-[600px]">
                    <div
                      className="prose prose-sm dark:prose-invert max-w-none p-6 bg-white dark:bg-gray-900 rounded-lg border min-h-[600px]"
                      dangerouslySetInnerHTML={{ __html: content }}
                    />
                  </TabsContent>

                  <TabsContent value="html" className="min-h-[600px]">
                    <Textarea
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      className="min-h-[600px] font-mono text-sm"
                      placeholder="HTML content..."
                    />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

