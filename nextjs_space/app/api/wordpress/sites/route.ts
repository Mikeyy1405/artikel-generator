
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET all WordPress sites
export async function GET() {
  try {
    const sites = await prisma.wordpress_sites.findMany({
      orderBy: { createdAt: 'desc' },
      include: {
        _count: {
          select: { blog_posts: true }
        }
      }
    });

    return NextResponse.json({ success: true, sites });
  } catch (error: any) {
    console.error('Error fetching WordPress sites:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// POST new WordPress site
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, url, username, appPassword, language, country } = body;

    if (!name || !url || !username || !appPassword) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const { randomUUID } = await import('crypto');
    const siteId = randomUUID();
    
    const site = await prisma.wordpress_sites.create({
      data: {
        id: siteId,
        name,
        url,
        username,
        appPassword,
        language: language || 'en',
        country,
        isActive: true,
        updatedAt: new Date()
      }
    });

    return NextResponse.json({ success: true, site });
  } catch (error: any) {
    console.error('Error creating WordPress site:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
