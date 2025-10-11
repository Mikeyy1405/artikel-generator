
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { unlink } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

// DELETE video
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Get video to find file path
    const video = await prisma.videos.findUnique({
      where: {
        id: params.id,
      },
    });

    if (!video) {
      return NextResponse.json(
        { error: 'Video not found' },
        { status: 404 }
      );
    }

    // Delete video file from disk
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

    // Delete from database
    await prisma.videos.delete({
      where: {
        id: params.id,
      },
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting video:', error);
    return NextResponse.json(
      { error: 'Failed to delete video' },
      { status: 500 }
    );
  }
}
