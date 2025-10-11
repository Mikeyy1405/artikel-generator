
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Sparkles, Youtube, List, Download, Copy, Trash2, Send, Globe } from 'lucide-react';
import { toast } from 'sonner';

interface WordPressSite {
  id: string;
  name: string;
  url: string;
}

export default function BlogPage() {
  const [contentType, setContentType] = useState<string>('seo');
  const [subject, setSubject] = useState('');
  const [wordCount, setWordCount] = useState('1000');
  const [keyword, setKeyword] = useState('');
  const [seoTitle, setSeoTitle] = useState('');
  const [metaDescription, setMetaDescription] = useState('');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [listItems, setListItems] = useState('10');
  const [wordsPerItem, setWordsPerItem] = useState('100');
  const [htmlContent, setHtmlContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [sites, setSites] = useState<WordPressSite[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>('');
  const [savedPostId, setSavedPostId] = useState<string>('');

  useEffect(() => {
    fetchWordPressSites();
  }, []);

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

  const generateContent = async () => {
    if (!subject.trim()) {
      toast.error('Please enter a subject');
      return;
    }

    if (contentType === 'seo' && (!keyword.trim() || !wordCount)) {
      toast.error('SEO articles require keyword and word count');
      return;
    }

    if (contentType === 'youtube' && !youtubeUrl.trim()) {
      toast.error('YouTube posts require a video URL');
      return;
    }

    if (contentType === 'list' && !listItems) {
      toast.error('List articles require number of items');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await fetch('/api/blog/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contentType,
          subject,
          wordCount: parseInt(wordCount),
          keyword,
          seoTitle,
          metaDescription,
          youtubeUrl,
          listItems: parseInt(listItems),
          wordsPerItem: parseInt(wordsPerItem)
        })
      });

      const data = await response.json();
      if (data.success) {
        setHtmlContent(data.content);
        toast.success('Content generated successfully!');
        
        // Auto-save as draft
        await saveDraft(data.content, data.wordCount);
      } else {
        toast.error(data.error || 'Failed to generate content');
      }
    } catch (error: any) {
      console.error('Generation error:', error);
      toast.error('Failed to generate content');
    } finally {
      setIsGenerating(false);
    }
  };

  const saveDraft = async (content?: string, calculatedWordCount?: number) => {
    const contentToSave = content || htmlContent;
    if (!contentToSave || !subject) {
      toast.error('Cannot save empty post');
      return;
    }

    try {
      const postData = {
        title: subject,
        content: contentToSave,
        contentType,
        seoTitle: seoTitle || subject,
        metaDescription,
        keywords: keyword,
        wordCount: calculatedWordCount || parseInt(wordCount),
        htmlContent: contentToSave,
        youtubeUrl: contentType === 'youtube' ? youtubeUrl : null,
        status: 'draft',
        siteId: selectedSiteId || null
      };

      const url = savedPostId ? `/api/blog/posts/${savedPostId}` : '/api/blog/posts';
      const method = savedPostId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
      });

      const data = await response.json();
      if (data.success) {
        setSavedPostId(data.post.id);
        toast.success('Draft saved successfully!');
      } else {
        toast.error(data.error || 'Failed to save draft');
      }
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Failed to save draft');
    }
  };

  const publishToWordPress = async () => {
    if (!savedPostId) {
      toast.error('Please save the post first');
      return;
    }

    if (!selectedSiteId) {
      toast.error('Please select a WordPress site');
      return;
    }

    try {
      const response = await fetch('/api/blog/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ postId: savedPostId })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Published to WordPress successfully!');
        if (data.wordpressUrl) {
          window.open(data.wordpressUrl, '_blank');
        }
      } else {
        toast.error(data.error || 'Failed to publish');
      }
    } catch (error) {
      console.error('Publish error:', error);
      toast.error('Failed to publish to WordPress');
    }
  };

  const copyToClipboard = () => {
    if (!htmlContent) {
      toast.error('No content to copy');
      return;
    }
    navigator.clipboard.writeText(htmlContent);
    toast.success('Content copied to clipboard!');
  };

  const downloadHTML = () => {
    if (!htmlContent) {
      toast.error('No content to download');
      return;
    }
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${subject || 'article'}.html`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('HTML file downloaded!');
  };

  const clearEditor = () => {
    setHtmlContent('');
    setSubject('');
    setKeyword('');
    setSeoTitle('');
    setMetaDescription('');
    setYoutubeUrl('');
    setSavedPostId('');
    toast.success('Editor cleared');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            ✍️ Blog Content Generator
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Create SEO-optimized articles, YouTube posts, and list articles with AI
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Settings */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Content Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Content Type</Label>
                  <Select value={contentType} onValueChange={setContentType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="seo">🎯 SEO Article</SelectItem>
                      <SelectItem value="perplexity">🔍 Research Article</SelectItem>
                      <SelectItem value="youtube">🎥 YouTube Post</SelectItem>
                      <SelectItem value="list">📝 List Article</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Subject / Topic</Label>
                  <Input
                    placeholder="Enter article topic..."
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                  />
                </div>

                {(contentType === 'seo' || contentType === 'perplexity') && (
                  <div>
                    <Label>Word Count</Label>
                    <Input
                      type="number"
                      placeholder="1000"
                      value={wordCount}
                      onChange={(e) => setWordCount(e.target.value)}
                    />
                  </div>
                )}

                {contentType === 'seo' && (
                  <>
                    <div>
                      <Label>Target Keyword</Label>
                      <Input
                        placeholder="main keyword"
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                      />
                    </div>

                    <div>
                      <Label>SEO Title (max 55 chars)</Label>
                      <Input
                        placeholder="SEO optimized title"
                        value={seoTitle}
                        onChange={(e) => setSeoTitle(e.target.value)}
                        maxLength={55}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        {seoTitle.length}/55 characters
                      </p>
                    </div>

                    <div>
                      <Label>Meta Description (max 130 chars)</Label>
                      <Textarea
                        placeholder="SEO meta description"
                        value={metaDescription}
                        onChange={(e) => setMetaDescription(e.target.value)}
                        maxLength={130}
                        rows={3}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        {metaDescription.length}/130 characters
                      </p>
                    </div>
                  </>
                )}

                {contentType === 'youtube' && (
                  <div>
                    <Label>YouTube URL</Label>
                    <Input
                      placeholder="https://youtube.com/watch?v=..."
                      value={youtubeUrl}
                      onChange={(e) => setYoutubeUrl(e.target.value)}
                    />
                  </div>
                )}

                {contentType === 'list' && (
                  <>
                    <div>
                      <Label>Number of Items</Label>
                      <Input
                        type="number"
                        placeholder="10"
                        value={listItems}
                        onChange={(e) => setListItems(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label>Words per Item</Label>
                      <Input
                        type="number"
                        placeholder="100"
                        value={wordsPerItem}
                        onChange={(e) => setWordsPerItem(e.target.value)}
                      />
                    </div>
                  </>
                )}

                <div>
                  <Label>WordPress Site (Optional)</Label>
                  <Select value={selectedSiteId} onValueChange={setSelectedSiteId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a site..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No site (save as draft)</SelectItem>
                      {sites.map((site) => (
                        <SelectItem key={site.id} value={site.id}>
                          {site.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  onClick={generateContent}
                  disabled={isGenerating}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                >
                  {isGenerating ? (
                    <>
                      <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Content
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Main Content - Editor */}
          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Generated Content</CardTitle>
                <CardDescription>
                  Your AI-generated content will appear here. You can edit it directly.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Editor Toolbar */}
                  <div className="flex flex-wrap gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg border">
                    <Button size="sm" variant="outline" onClick={() => saveDraft()} disabled={!htmlContent}>
                      <FileText className="h-4 w-4 mr-1" />
                      Save Draft
                    </Button>
                    <Button size="sm" variant="outline" onClick={publishToWordPress} disabled={!savedPostId || !selectedSiteId}>
                      <Send className="h-4 w-4 mr-1" />
                      Publish
                    </Button>
                    <Button size="sm" variant="outline" onClick={copyToClipboard} disabled={!htmlContent}>
                      <Copy className="h-4 w-4 mr-1" />
                      Copy HTML
                    </Button>
                    <Button size="sm" variant="outline" onClick={downloadHTML} disabled={!htmlContent}>
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                    <Button size="sm" variant="outline" onClick={clearEditor} disabled={!htmlContent}>
                      <Trash2 className="h-4 w-4 mr-1" />
                      Clear
                    </Button>
                  </div>

                  {/* Content Display */}
                  <Tabs defaultValue="preview" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="preview">Preview</TabsTrigger>
                      <TabsTrigger value="html">HTML Code</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="preview" className="min-h-[500px]">
                      {htmlContent ? (
                        <div
                          className="prose prose-sm dark:prose-invert max-w-none p-6 bg-white dark:bg-gray-900 rounded-lg border min-h-[500px]"
                          dangerouslySetInnerHTML={{ __html: htmlContent }}
                        />
                      ) : (
                        <div className="flex items-center justify-center h-[500px] bg-gray-50 dark:bg-gray-800 rounded-lg border border-dashed">
                          <div className="text-center text-gray-400">
                            <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                            <p>No content generated yet</p>
                            <p className="text-sm">Fill in the settings and click Generate</p>
                          </div>
                        </div>
                      )}
                    </TabsContent>
                    
                    <TabsContent value="html" className="min-h-[500px]">
                      {htmlContent ? (
                        <Textarea
                          value={htmlContent}
                          onChange={(e) => setHtmlContent(e.target.value)}
                          className="min-h-[500px] font-mono text-sm"
                          placeholder="HTML content will appear here..."
                        />
                      ) : (
                        <div className="flex items-center justify-center h-[500px] bg-gray-50 dark:bg-gray-800 rounded-lg border border-dashed">
                          <div className="text-center text-gray-400">
                            <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                            <p>No HTML code yet</p>
                          </div>
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
