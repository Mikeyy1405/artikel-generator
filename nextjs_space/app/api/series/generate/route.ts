
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { generateVideo } from '@/lib/videoGenerator';
import { updateProgress, clearProgress } from '@/lib/progressTracker';
import path from 'path';
import fs from 'fs';

const prisma = new PrismaClient();

export async function POST(request: NextRequest) {
  try {
    const { seriesId } = await request.json();
    
    if (!seriesId) {
      return NextResponse.json({ error: 'Series ID is required' }, { status: 400 });
    }
    
    // Get series configuration
    const series = await prisma.series.findUnique({
      where: { id: seriesId },
    });
    
    if (!series) {
      return NextResponse.json({ error: 'Series not found' }, { status: 404 });
    }
    
    // Create output directory
    const outputDir = path.join(process.cwd(), 'public', 'generated', seriesId);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Delete existing videos for this series
    await prisma.videos.deleteMany({
      where: { seriesId },
    });
    
    // Generate videos
    const videos = [];
    for (let i = 0; i < series.videoCount; i++) {
      try {
        // Update initial progress
        updateProgress(
          seriesId,
          i + 1,
          series.videoCount,
          `Video ${i + 1} van ${series.videoCount} wordt voorbereid...`
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
          i,
          outputDir,
          (step: string, percentage: number) => {
            updateProgress(
              seriesId,
              i + 1,
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
            thumbnailUrl: `/generated/${seriesId}/thumbnail_${i}.jpg`,
            videoUrl: `/generated/${seriesId}/video_${i}.mp4`,
            duration: result.duration,
            status: 'generated',
          },
        });
        
        videos.push(video);
      } catch (error) {
        console.error(`Error generating video ${i}:`, error);
        // Continue with next video
      }
    }
    
    // Clear progress when done
    clearProgress(seriesId);
    
    return NextResponse.json({ 
      success: true, 
      message: `Generated ${videos.length} videos`,
      videos 
    });
    
  } catch (error) {
    console.error('Error in video generation:', error);
    return NextResponse.json(
      { error: 'Failed to generate videos' },
      { status: 500 }
    );
  }
}
