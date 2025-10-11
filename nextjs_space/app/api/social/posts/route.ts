
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const posts = await prisma.social_media_posts.findMany({
      orderBy: { createdAt: 'desc' },
    });

    return NextResponse.json({ success: true, posts });
  } catch (error) {
    console.error('Error fetching social media posts:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch social media posts' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      title,
      content,
      platform,
      postType,
      imagePrompt,
      hashtags,
      scheduledFor,
    } = body;

    const post = await prisma.social_media_posts.create({
      data: {
        title,
        content,
        platform: platform || 'all',
        postType: postType || 'motivational',
        imagePrompt,
        hashtags: hashtags || [],
        scheduledFor: scheduledFor ? new Date(scheduledFor) : undefined,
        status: 'draft',
      },
    });

    return NextResponse.json({ success: true, post });
  } catch (error) {
    console.error('Error creating social media post:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create social media post' },
      { status: 500 }
    );
  }
}
