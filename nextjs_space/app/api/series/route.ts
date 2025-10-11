
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const {
      name,
      format,
      presetType,
      customFormat,
      niche,
      language,
      voice,
      voiceStyle,
      backgroundMusic,
      musicDescription,
      artStyle,
      captionStyle,
      duration,
      videoCount,
      publishSchedule,
      publishTime,
    } = body;

    // Create the series without any videos
    const { randomUUID } = await import('crypto');
    const seriesId = randomUUID();
    
    const series = await prisma.series.create({
      data: {
        id: seriesId,
        name,
        format,
        presetType,
        customFormat,
        niche,
        language,
        voice,
        voiceStyle,
        backgroundMusic,
        musicDescription,
        artStyle,
        captionStyle,
        duration,
        videoCount,
        publishSchedule,
        publishTime,
        updatedAt: new Date(),
      },
    });

    return NextResponse.json(series);
  } catch (error) {
    console.error('Error creating series:', error);
    return NextResponse.json(
      { error: 'Failed to create series' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const series = await prisma.series.findMany({
      include: {
        videos: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });

    return NextResponse.json(series);
  } catch (error) {
    console.error('Error fetching series:', error);
    return NextResponse.json(
      { error: 'Failed to fetch series' },
      { status: 500 }
    );
  }
}
