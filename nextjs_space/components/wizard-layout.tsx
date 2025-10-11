
'use client';

import { ArrowLeft, ArrowRight, Video } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import WizardProgress from './wizard-progress';
import { WizardStep } from '@/lib/types';

interface WizardLayoutProps {
  children: React.ReactNode;
  currentStep: number;
  onNext?: () => void;
  onPrev?: () => void;
  canGoNext?: boolean;
  canGoPrev?: boolean;
  isLastStep?: boolean;
  onComplete?: () => void;
  loading?: boolean;
}

const wizardSteps: WizardStep[] = [
  { id: 1, title: 'Format & Niche', completed: false },
  { id: 2, title: 'Taal & Stem', completed: false },
  { id: 3, title: 'Muziek', completed: false },
  { id: 4, title: 'Art Style', completed: false },
  { id: 5, title: 'Ondertiteling', completed: false },
  { id: 6, title: 'Duur', completed: false },
  { id: 7, title: 'Serie Details', completed: false },
];

export default function WizardLayout({
  children,
  currentStep,
  onNext,
  onPrev,
  canGoNext = false,
  canGoPrev = true,
  isLastStep = false,
  onComplete,
  loading = false,
}: WizardLayoutProps) {
  const stepsWithCompletion = wizardSteps.map((step, index) => ({
    ...step,
    completed: index + 1 < currentStep,
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-violet-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-purple-100">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-violet-600 rounded-lg flex items-center justify-center">
                <Video className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent">
                FacelessVideo
              </h1>
            </Link>
            <div className="text-sm text-gray-600">
              Stap {currentStep} van {wizardSteps.length}
            </div>
          </div>
        </div>
      </header>

      {/* Progress Indicator */}
      <WizardProgress steps={stepsWithCompletion} currentStep={currentStep} />

      {/* Content */}
      <main className="flex-1 px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg border border-purple-100 overflow-hidden">
            <div className="p-8">
              {children}
            </div>
          </div>
        </div>
      </main>

      {/* Navigation */}
      <div className="sticky bottom-0 bg-white/80 backdrop-blur-md border-t border-purple-100 px-4 py-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Button
            variant="outline"
            onClick={onPrev}
            disabled={!canGoPrev || loading}
            className="flex items-center space-x-2 border-purple-200 text-purple-600 hover:bg-purple-50"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Terug</span>
          </Button>

          {isLastStep ? (
            <Button
              onClick={onComplete}
              disabled={!canGoNext || loading}
              className="gradient-button flex items-center space-x-2"
            >
              <span>{loading ? 'Serie aanmaken...' : 'Serie aanmaken'}</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          ) : (
            <Button
              onClick={onNext}
              disabled={!canGoNext || loading}
              className="gradient-button flex items-center space-x-2"
            >
              <span>Verder</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
