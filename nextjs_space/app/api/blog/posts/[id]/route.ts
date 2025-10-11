
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET single blog post
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const post = await prisma.blog_posts.findUnique({
      where: { id: params.id },
      include: {
        wordpress_sites: {
          select: {
            id: true,
            name: true,
            url: true,
            username: true,
            appPassword: true
          }
        }
      }
    });

    if (!post) {
      return NextResponse.json(
        { success: false, error: 'Post not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true, post });
  } catch (error: any) {
    console.error('Error fetching blog post:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// PUT update blog post
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await req.json();
    const {
      title,
      content,
      seoTitle,
      metaDescription,
      keywords,
      wordCount,
      htmlContent,
      youtubeUrl,
      status,
      scheduledAt,
      wordpressPostId,
      publishedUrl
    } = body;

    const updateData: any = {};
    if (title) updateData.title = title;
    if (content) updateData.content = content;
    if (seoTitle !== undefined) updateData.seoTitle = seoTitle;
    if (metaDescription !== undefined) updateData.metaDescription = metaDescription;
    if (keywords !== undefined) updateData.keywords = keywords;
    if (wordCount !== undefined) updateData.wordCount = wordCount;
    if (htmlContent !== undefined) updateData.htmlContent = htmlContent;
    if (youtubeUrl !== undefined) updateData.youtubeUrl = youtubeUrl;
    if (status) updateData.status = status;
    if (scheduledAt !== undefined) updateData.scheduledAt = scheduledAt ? new Date(scheduledAt) : null;
    if (wordpressPostId !== undefined) updateData.wordpressPostId = wordpressPostId;
    if (publishedUrl !== undefined) updateData.publishedUrl = publishedUrl;

    const post = await prisma.blog_posts.update({
      where: { id: params.id },
      data: updateData,
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
    console.error('Error updating blog post:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// DELETE blog post
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await prisma.blog_posts.delete({
      where: { id: params.id }
    });

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Error deleting blog post:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
