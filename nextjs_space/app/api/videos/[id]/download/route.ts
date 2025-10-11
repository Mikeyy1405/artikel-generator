
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const video = await prisma.videos.findUnique({
      where: {
        id: params.id,
      },
      include: {
        series: true,
      },
    });

    if (!video) {
      return NextResponse.json(
        { error: 'Video not found' },
        { status: 404 }
      );
    }

    if (!video.videoUrl) {
      return NextResponse.json(
        { error: 'Video file not available' },
        { status: 404 }
      );
    }

    // The videoUrl contains the path to the video file
    const videoPath = path.join(process.cwd(), video.videoUrl);
    
    if (!existsSync(videoPath)) {
      return NextResponse.json(
        { error: 'Video file not found on disk' },
        { status: 404 }
      );
    }

    // Read the video file
    const videoBuffer = await readFile(videoPath);

    // Create a proper filename for download
    const fileName = `${video.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.mp4`;

    // Return the video file with proper headers
    return new NextResponse(videoBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'video/mp4',
        'Content-Disposition': `attachment; filename="${fileName}"`,
        'Content-Length': videoBuffer.length.toString(),
      },
    });
  } catch (error) {
    console.error('Error downloading video:', error);
    return NextResponse.json(
      { error: 'Failed to download video' },
      { status: 500 }
    );
  }
}
