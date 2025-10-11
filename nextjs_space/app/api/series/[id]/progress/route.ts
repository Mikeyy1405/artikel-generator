
import { NextRequest, NextResponse } from 'next/server';
import { getProgress } from '@/lib/progressTracker';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const seriesId = params.id;
    
    if (!seriesId) {
      return NextResponse.json({ error: 'Series ID is required' }, { status: 400 });
    }
    
    const progress = getProgress(seriesId);
    
    if (!progress) {
      return NextResponse.json({ 
        generating: false,
        message: 'Geen actieve generatie',
      });
    }
    
    // Check if progress is stale (older than 5 minutes)
    const isStale = Date.now() - progress.timestamp > 5 * 60 * 1000;
    
    if (isStale) {
      return NextResponse.json({ 
        generating: false,
        message: 'Generatie time-out',
      });
    }
    
    return NextResponse.json({ 
      generating: true,
      currentStep: progress.currentStep,
      currentVideo: progress.currentVideo,
      totalVideos: progress.totalVideos,
      percentage: progress.percentage,
      message: progress.message,
    });
    
  } catch (error) {
    console.error('Error fetching progress:', error);
    return NextResponse.json(
      { error: 'Failed to fetch progress' },
      { status: 500 }
    );
  }
}
