
'use client';

import { CheckCircle } from 'lucide-react';
import { WizardStep } from '@/lib/types';

interface WizardProgressProps {
  steps: WizardStep[];
  currentStep: number;
}

export default function WizardProgress({ steps, currentStep }: WizardProgressProps) {
  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`wizard-step-indicator ${
                  index + 1 === currentStep
                    ? 'wizard-step-active'
                    : step.completed
                    ? 'wizard-step-completed'
                    : 'wizard-step-inactive'
                }`}
              >
                {step.completed ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              <span
                className={`mt-2 text-sm font-medium ${
                  index + 1 === currentStep
                    ? 'text-purple-600'
                    : step.completed
                    ? 'text-purple-700'
                    : 'text-gray-400'
                }`}
              >
                {step.title}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-12 h-1 mx-2 mt-[-24px] rounded-full ${
                  step.completed ? 'bg-purple-200' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
