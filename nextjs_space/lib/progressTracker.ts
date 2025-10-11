
// Simple in-memory progress tracker for video generation
interface ProgressStatus {
  seriesId: string;
  currentStep: string;
  currentVideo: number;
  totalVideos: number;
  percentage: number;
  message: string;
  timestamp: number;
}

const progressStore = new Map<string, ProgressStatus>();

export function updateProgress(
  seriesId: string,
  currentVideo: number,
  totalVideos: number,
  message: string
) {
  const percentage = Math.round((currentVideo / totalVideos) * 100);
  
  progressStore.set(seriesId, {
    seriesId,
    currentStep: message,
    currentVideo,
    totalVideos,
    percentage,
    message,
    timestamp: Date.now(),
  });
}

export function getProgress(seriesId: string): ProgressStatus | null {
  return progressStore.get(seriesId) || null;
}

export function clearProgress(seriesId: string) {
  progressStore.delete(seriesId);
}

export function getAllProgress(): ProgressStatus[] {
  return Array.from(progressStore.values());
}
