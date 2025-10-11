
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET single WordPress site
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const site = await prisma.wordpress_sites.findUnique({
      where: { id: params.id },
      include: {
        blog_posts: {
          orderBy: { createdAt: 'desc' },
          take: 10
        }
      }
    });

    if (!site) {
      return NextResponse.json(
        { success: false, error: 'Site not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true, site });
  } catch (error: any) {
    console.error('Error fetching WordPress site:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// PUT update WordPress site
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await req.json();
    const { name, url, username, appPassword, language, country, isActive } = body;

    const updateData: any = {};
    if (name) updateData.name = name;
    if (url) updateData.url = url;
    if (username) updateData.username = username;
    if (appPassword) updateData.appPassword = appPassword;
    if (language) updateData.language = language;
    if (country !== undefined) updateData.country = country;
    if (isActive !== undefined) updateData.isActive = isActive;

    const site = await prisma.wordpress_sites.update({
      where: { id: params.id },
      data: updateData
    });

    return NextResponse.json({ success: true, site });
  } catch (error: any) {
    console.error('Error updating WordPress site:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// DELETE WordPress site
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await prisma.wordpress_sites.delete({
      where: { id: params.id }
    });

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Error deleting WordPress site:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
