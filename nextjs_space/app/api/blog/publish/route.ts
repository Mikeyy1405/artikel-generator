
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { postId } = body;

    if (!postId) {
      return NextResponse.json(
        { success: false, error: 'Missing postId' },
        { status: 400 }
      );
    }

    // Get the post with site credentials
    const post = await prisma.blog_posts.findUnique({
      where: { id: postId },
      include: {
        wordpress_sites: true
      }
    });

    if (!post) {
      return NextResponse.json(
        { success: false, error: 'Post not found' },
        { status: 404 }
      );
    }

    if (!post.wordpress_sites) {
      return NextResponse.json(
        { success: false, error: 'No WordPress site connected to this post' },
        { status: 400 }
      );
    }

    // Prepare WordPress API request
    const wpApiUrl = `${post.wordpress_sites.url}/wp-json/wp/v2/posts`;
    const auth = Buffer.from(`${post.wordpress_sites.username}:${post.wordpress_sites.appPassword}`).toString('base64');

    const wpPostData = {
      title: post.seoTitle || post.title,
      content: post.htmlContent || post.content,
      status: 'publish',
      meta: {
        description: post.metaDescription || ''
      }
    };

    // Publish to WordPress
    const response = await fetch(wpApiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${auth}`
      },
      body: JSON.stringify(wpPostData)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('WordPress API error:', errorText);
      return NextResponse.json(
        { success: false, error: `WordPress API error: ${response.status} - ${errorText}` },
        { status: 500 }
      );
    }

    const wpResponse = await response.json();

    // Update post in database
    const updatedPost = await prisma.blog_posts.update({
      where: { id: postId },
      data: {
        status: 'published',
        wordpressPostId: wpResponse.id,
        publishedUrl: wpResponse.link
      }
    });

    return NextResponse.json({
      success: true,
      post: updatedPost,
      wordpressUrl: wpResponse.link
    });

  } catch (error: any) {
    console.error('Error publishing to WordPress:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
