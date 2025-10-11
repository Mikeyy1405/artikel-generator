
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import WizardLayout from '@/components/wizard-layout';
import Step1FormatNiche from '@/components/wizard-steps/step1-format-niche';
import Step2LanguageVoice from '@/components/wizard-steps/step2-language-voice';
import Step3BackgroundMusic from '@/components/wizard-steps/step3-background-music';
import Step4ArtStyle from '@/components/wizard-steps/step4-art-style';
import Step5CaptionStyle from '@/components/wizard-steps/step5-caption-style';
import Step6Duration from '@/components/wizard-steps/step6-duration';
import Step7SeriesDetails from '@/components/wizard-steps/step7-series-details';
import { SeriesFormData } from '@/lib/types';

export default function WizardPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<SeriesFormData>>({
    format: 'preset',
    language: 'Nederlands',
    duration: 'short',
    videoCount: 5,
  });

  const updateFormData = (data: Partial<SeriesFormData>) => {
    setFormData(prev => ({ ...prev, ...data }));
  };

  const canGoNext = (): boolean => {
    switch (currentStep) {
      case 1:
        return !!(formData.niche && 
               ((formData.format === 'preset' && formData.presetType) || 
                (formData.format === 'custom' && formData.customFormat)));
      case 2:
        return !!(formData.language && formData.voice && formData.voiceStyle);
      case 3:
        return true; // Background music is optional
      case 4:
        return !!formData.artStyle;
      case 5:
        return !!formData.captionStyle;
      case 6:
        return !!formData.duration;
      case 7:
        return !!(formData.seriesName && formData.videoCount);
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep < 7) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/series', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.seriesName,
          format: formData.format,
          presetType: formData.presetType,
          customFormat: formData.customFormat,
          niche: formData.niche,
          language: formData.language,
          voice: formData.voice,
          voiceStyle: formData.voiceStyle,
          backgroundMusic: formData.backgroundMusic,
          musicDescription: formData.musicDescription,
          artStyle: formData.artStyle,
          captionStyle: formData.captionStyle,
          duration: formData.duration,
          videoCount: formData.videoCount,
          publishSchedule: formData.publishSchedule,
          publishTime: formData.publishTime,
        }),
      });

      if (response.ok) {
        const series = await response.json();
        toast.success('Serie succesvol aangemaakt!');
        router.push(`/dashboard/series/${series.id}`);
      } else {
        throw new Error('Fout bij het aanmaken van de serie');
      }
    } catch (error) {
      console.error('Error creating series:', error);
      toast.error('Er is een fout opgetreden bij het aanmaken van de serie');
    } finally {
      setLoading(false);
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return <Step1FormatNiche formData={formData} updateFormData={updateFormData} />;
      case 2:
        return <Step2LanguageVoice formData={formData} updateFormData={updateFormData} />;
      case 3:
        return <Step3BackgroundMusic formData={formData} updateFormData={updateFormData} />;
      case 4:
        return <Step4ArtStyle formData={formData} updateFormData={updateFormData} />;
      case 5:
        return <Step5CaptionStyle formData={formData} updateFormData={updateFormData} />;
      case 6:
        return <Step6Duration formData={formData} updateFormData={updateFormData} />;
      case 7:
        return <Step7SeriesDetails formData={formData} updateFormData={updateFormData} />;
      default:
        return null;
    }
  };

  return (
    <WizardLayout
      currentStep={currentStep}
      onNext={handleNext}
      onPrev={handlePrev}
      canGoNext={canGoNext()}
      canGoPrev={currentStep > 1}
      isLastStep={currentStep === 7}
      onComplete={handleComplete}
      loading={loading}
    >
      {renderCurrentStep()}
    </WizardLayout>
  );
}
