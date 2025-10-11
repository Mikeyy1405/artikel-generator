
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { generateVideo } from '@/lib/videoGenerator';
import path from 'path';
import fs from 'fs';

const prisma = new PrismaClient();

export async function POST(request: NextRequest) {
  try {
    // This endpoint should be called by a cron job every hour
    // For now, we'll generate videos for series that need them
    
    const allSeries = await prisma.series.findMany({
      include: {
        videos: true,
      },
    });
    
    const results = [];
    
    for (const series of allSeries) {
      // Check if series needs more videos
      if (series.videos.length < series.videoCount) {
        try {
          console.log(`Generating video for series: ${series.name}`);
          
          // Create output directory
          const outputDir = path.join(process.cwd(), 'public', 'generated', series.id);
          if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
          }
          
          // Generate next video
          const videoIndex = series.videos.length;
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
            outputDir
          );
          
          // Create video record in database
          const { randomUUID } = await import('crypto');
          const videoId = randomUUID();
          
          const video = await prisma.videos.create({
            data: {
              id: videoId,
              seriesId: series.id,
              title: result.title,
              thumbnailUrl: `/generated/${series.id}/thumbnail_${videoIndex}.jpg`,
              videoUrl: `/generated/${series.id}/video_${videoIndex}.mp4`,
              duration: result.duration,
              status: 'generated',
            },
          });
          
          results.push({
            seriesId: series.id,
            seriesName: series.name,
            videoId: video.id,
            success: true,
          });
          
          console.log(`Successfully generated video for series: ${series.name}`);
        } catch (error) {
          console.error(`Error generating video for series ${series.name}:`, error);
          results.push({
            seriesId: series.id,
            seriesName: series.name,
            success: false,
            error: String(error),
          });
        }
      }
    }
    
    return NextResponse.json({ 
      success: true,
      message: `Processed ${results.length} series`,
      results 
    });
    
  } catch (error) {
    console.error('Error in scheduled video generation:', error);
    return NextResponse.json(
      { error: 'Failed to generate scheduled videos', details: String(error) },
      { status: 500 }
    );
  }
}

// Allow GET for testing
export async function GET(request: NextRequest) {
  return POST(request);
}
