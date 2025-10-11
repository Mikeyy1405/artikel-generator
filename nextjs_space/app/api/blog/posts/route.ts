
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET all blog posts
export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const siteId = searchParams.get('siteId');
    const status = searchParams.get('status');

    const where: any = {};
    if (siteId) where.siteId = siteId;
    if (status) where.status = status;

    const posts = await prisma.blog_posts.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      include: {
        wordpress_sites: {
          select: {
            id: true,
            name: true,
            url: true
          }
        }
      }
    });

    return NextResponse.json({ success: true, posts });
  } catch (error: any) {
    console.error('Error fetching blog posts:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// POST new blog post
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const {
      siteId,
      title,
      content,
      contentType,
      seoTitle,
      metaDescription,
      keywords,
      wordCount,
      htmlContent,
      youtubeUrl,
      status,
      scheduledAt
    } = body;

    if (!title || !content || !contentType) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const { randomUUID } = await import('crypto');
    const postId = randomUUID();
    
    const post = await prisma.blog_posts.create({
      data: {
        id: postId,
        siteId: siteId || null,
        title,
        content,
        contentType,
        seoTitle,
        metaDescription,
        keywords,
        wordCount,
        htmlContent,
        youtubeUrl,
        status: status || 'draft',
        scheduledAt: scheduledAt ? new Date(scheduledAt) : null,
        updatedAt: new Date()
      },
      include: {
        wordpress_sites: {
          select: {
            id: true,
            name: true,
            url: true
          }
        }
      }
    });

    return NextResponse.json({ success: true, post });
  } catch (error: any) {
    console.error('Error creating blog post:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
