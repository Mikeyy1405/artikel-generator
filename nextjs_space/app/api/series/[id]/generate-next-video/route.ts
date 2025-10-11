
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { generateVideo } from '@/lib/videoGenerator';
import { updateProgress, clearProgress } from '@/lib/progressTracker';
import path from 'path';
import fs from 'fs';

const prisma = new PrismaClient();

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const seriesId = params.id;
    
    if (!seriesId) {
      return NextResponse.json({ error: 'Series ID is required' }, { status: 400 });
    }
    
    // Get series configuration
    const series = await prisma.series.findUnique({
      where: { id: seriesId },
      include: {
        videos: true,
      },
    });
    
    if (!series) {
      return NextResponse.json({ error: 'Series not found' }, { status: 404 });
    }
    
    // Check if series already has all videos
    if (series.videos.length >= series.videoCount) {
      return NextResponse.json({ 
        error: 'Series already has all videos generated',
        videosGenerated: series.videos.length,
        videosTotal: series.videoCount,
      }, { status: 400 });
    }
    
    // Create output directory
    const outputDir = path.join(process.cwd(), 'public', 'generated', seriesId);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Generate next video
    const videoIndex = series.videos.length;
    
    console.log(`Generating video ${videoIndex + 1} for series: ${series.name}`);
    
    // Update progress
    updateProgress(
      seriesId,
      videoIndex + 1,
      series.videoCount,
      `Video ${videoIndex + 1} van ${series.videoCount} wordt gegenereerd...`
    );
    
    const result = await generateVideo(
      {
        format: series.format,
        presetType: series.presetType || undefined,
        customFormat: series.customFormat || undefined,
        niche: series.niche,
        language: series.language,
        voice: series.voice,
        voiceStyle: series.voiceStyle,
        backgroundMusic: series.backgroundMusic || undefined,
        artStyle: series.artStyle,
        captionStyle: series.captionStyle,
        duration: series.duration,
      },
      videoIndex,
      outputDir,
      (step: string, percentage: number) => {
        updateProgress(
          seriesId,
          videoIndex + 1,
          series.videoCount,
          step
        );
      }
    );
    
    // Create video record in database
    const { randomUUID } = await import('crypto');
    const videoId = randomUUID();
    
    const video = await prisma.videos.create({
      data: {
        id: videoId,
        seriesId,
        title: result.title,
        thumbnailUrl: `/generated/${seriesId}/thumbnail_${videoIndex}.jpg`,
        videoUrl: `/generated/${seriesId}/video_${videoIndex}.mp4`,
        duration: result.duration,
        status: 'generated',
      },
    });
    
    console.log(`Successfully generated video ${videoIndex + 1} for series: ${series.name}`);
    
    // Clear progress on success
    clearProgress(seriesId);
    
    return NextResponse.json({ 
      success: true, 
      message: `Generated video ${videoIndex + 1} of ${series.videoCount}`,
      video,
      progress: {
        current: videoIndex + 1,
        total: series.videoCount,
      }
    });
    
  } catch (error) {
    console.error('Error generating video:', error);
    // Clear progress on error
    clearProgress(params.id);
    return NextResponse.json(
      { error: 'Failed to generate video', details: String(error) },
      { status: 500 }
    );
  }
}
