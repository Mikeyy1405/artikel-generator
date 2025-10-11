
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { unlink } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

// GET single series
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const series = await prisma.series.findUnique({
      where: {
        id: params.id,
      },
      include: {
        videos: {
          orderBy: {
            createdAt: 'asc',
          },
        },
      },
    });

    if (!series) {
      return NextResponse.json(
        { error: 'Series not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(series);
  } catch (error) {
    console.error('Error fetching series:', error);
    return NextResponse.json(
      { error: 'Failed to fetch series' },
      { status: 500 }
    );
  }
}

// UPDATE series
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    
    const {
      name,
      niche,
      language,
      voice,
      voiceStyle,
      backgroundMusic,
      musicDescription,
      artStyle,
      captionStyle,
      publishSchedule,
      publishTime,
    } = body;

    const series = await prisma.series.update({
      where: {
        id: params.id,
      },
      data: {
        name,
        niche,
        language,
        voice,
        voiceStyle,
        backgroundMusic,
        musicDescription,
        artStyle,
        captionStyle,
        publishSchedule,
        publishTime,
      },
      include: {
        videos: {
          orderBy: {
            createdAt: 'asc',
          },
        },
      },
    });

    return NextResponse.json(series);
  } catch (error) {
    console.error('Error updating series:', error);
    return NextResponse.json(
      { error: 'Failed to update series' },
      { status: 500 }
    );
  }
}

// DELETE series
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Get all videos for this series to delete video files
    const videos = await prisma.videos.findMany({
      where: {
        seriesId: params.id,
      },
    });

    // Delete video files from disk
    for (const video of videos) {
      if (video.videoUrl) {
        const videoPath = path.join(process.cwd(), video.videoUrl);
        if (existsSync(videoPath)) {
          try {
            await unlink(videoPath);
          } catch (error) {
            console.error(`Failed to delete video file: ${videoPath}`, error);
          }
        }
      }
    }

    // Delete the series (cascade will delete videos from database)
    await prisma.series.delete({
      where: {
        id: params.id,
      },
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting series:', error);
    return NextResponse.json(
      { error: 'Failed to delete series' },
      { status: 500 }
    );
  }
}
