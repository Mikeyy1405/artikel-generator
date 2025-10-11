

'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, Globe, Trash2, ExternalLink, Edit } from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface BlogPost {
  id: string;
  title: string;
  contentType: string;
  status: string;
  wordCount?: number;
  createdAt: string;
  publishedUrl?: string;
  wordpress_sites?: {
    id: string;
    name: string;
    url: string;
  };
}

export default function BlogPostsPage() {
  const router = useRouter();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/blog/posts');
      const data = await response.json();
      if (data.success) {
        setPosts(data.posts);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      toast.error('Failed to load blog posts');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/blog/posts/${id}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Post deleted successfully');
        fetchPosts();
      } else {
        toast.error(data.error || 'Failed to delete post');
      }
    } catch (error) {
      console.error('Error deleting post:', error);
      toast.error('Failed to delete post');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'bg-green-500';
      case 'draft':
        return 'bg-yellow-500';
      case 'scheduled':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getContentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      seo: '🎯 SEO Article',
      perplexity: '🔍 Research',
      youtube: '🎥 YouTube',
      list: '📝 List',
      listicle: '📝 List',
      howto: '📖 How-to',
      review: '⭐ Review'
    };
    return labels[type] || type;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              📝 Blog Posts
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              View and manage your blog content
            </p>
          </div>

          <Link href="/blog">
            <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
              <FileText className="h-4 w-4 mr-2" />
              Create New Post
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading blog posts...</p>
          </div>
        ) : posts.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">No Blog Posts</h3>
              <p className="text-gray-600 mb-4 text-center">
                Create your first blog post to get started
              </p>
              <Link href="/blog">
                <Button className="bg-gradient-to-r from-purple-600 to-blue-600">
                  <FileText className="h-4 w-4 mr-2" />
                  Create First Post
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <Card 
                key={post.id} 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/blog/${post.id}`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className={getStatusColor(post.status)}>
                          {post.status}
                        </Badge>
                        <Badge variant="outline">
                          {getContentTypeLabel(post.contentType)}
                        </Badge>
                        {post.wordCount && (
                          <Badge variant="outline">
                            {post.wordCount} words
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-xl">{post.title}</CardTitle>
                      <CardDescription className="flex items-center gap-4 mt-2">
                        {post.wordpress_sites && (
                          <span className="flex items-center gap-1">
                            <Globe className="h-3 w-3" />
                            {post.wordpress_sites.name}
                          </span>
                        )}
                        <span>
                          Created {new Date(post.createdAt).toLocaleDateString()}
                        </span>
                      </CardDescription>
                    </div>

                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push(`/blog/${post.id}`)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      {post.publishedUrl && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.open(post.publishedUrl, '_blank')}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleDelete(post.id, post.title)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

