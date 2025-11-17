'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { questionnaireQuestions, UserProfile, defaultUserProfile } from '@/lib/mock-data';
import { ArrowRight, ArrowLeft, Sparkles } from 'lucide-react';

interface OnboardingQuestionnaireProps {
  onComplete: (profile: UserProfile) => void;
}

export function OnboardingQuestionnaire({ onComplete }: OnboardingQuestionnaireProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [showSummary, setShowSummary] = useState(false);
  const [explorerType, setExplorerType] = useState('');

  const progress = ((currentQuestion + 1) / questionnaireQuestions.length) * 100;

  const handleAnswer = (questionId: string, value: any, isMultiple: boolean) => {
    if (isMultiple) {
      const current = answers[questionId] || [];
      const updated = current.includes(value)
        ? current.filter((v: any) => v !== value)
        : [...current, value];
      setAnswers({ ...answers, [questionId]: updated });
    } else {
      setAnswers({ ...answers, [questionId]: value });
    }
  };

  const handleNext = () => {
    if (currentQuestion < questionnaireQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      generateExplorerType();
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const generateExplorerType = () => {
    // Simple logic to generate explorer type based on answers
    const fitness = answers.fitness;
    const narrative = answers.narrative;
    
    let type = '';
    if (fitness === 'beginner') {
      type = narrative === 'history' ? 'Urban Historian' : 'Nature Novice';
    } else if (fitness === 'intermediate') {
      type = narrative === 'adventure' ? 'Trail Adventurer' : 'City Explorer';
    } else if (fitness === 'advanced') {
      type = narrative === 'adventure' ? 'Mountain Challenger' : 'Peak Seeker';
    } else {
      type = 'Summit Conqueror';
    }
    
    setExplorerType(type);
    setShowSummary(true);
  };

  const handleComplete = () => {
    const profile: UserProfile = {
      ...defaultUserProfile,
      explorerType,
      fitnessLevel: answers.fitness,
      preferredTypes: answers.type || [],
      narrativeStyle: answers.narrative,
    };
    onComplete(profile);
  };

  const question = questionnaireQuestions[currentQuestion];
  const isAnswered = question.type === 'multiple' 
    ? (answers[question.id]?.length > 0)
    : answers[question.id];

  if (showSummary) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
        <div className="absolute inset-0 opacity-5" style={{
          backgroundImage: `
            repeating-linear-gradient(0deg, transparent, transparent 8px, currentColor 8px, currentColor 9px),
            repeating-linear-gradient(90deg, transparent, transparent 8px, currentColor 8px, currentColor 9px)
          `
        }} />
        
        <Card className="max-w-2xl w-full bg-card pixel-border relative z-10">
          <div className="bg-accent text-accent-foreground p-4 border-b-4 border-border">
            <h2 className="text-sm font-pixel text-pixel-shadow-sm text-center">CLASS ASSIGNED!</h2>
          </div>
          
          <div className="p-8 md:p-12 space-y-6 text-center">
            <div className="text-6xl mb-4 animate-bounce">
              🎖️
            </div>
            
            <div className="bg-primary text-primary-foreground p-4 pixel-border-sm">
              <h2 className="text-sm md:text-base font-pixel text-pixel-shadow-sm">
                {explorerType.toUpperCase()}
              </h2>
            </div>

            <div className="bg-muted p-6 pixel-border-sm">
              <p className="text-[10px] md:text-xs leading-relaxed text-foreground">
                YOUR ADVENTURE PROFILE HAS BEEN CREATED. ROUTES HAVE BEEN PERSONALIZED TO MATCH YOUR EXPLORER SPIRIT.
              </p>
            </div>

            <div className="bg-card border-4 border-border p-4 space-y-3 text-left">
              <h3 className="font-pixel text-xs text-center mb-4">STATS</h3>
              <div className="grid grid-cols-2 gap-4 text-[10px]">
                <div className="space-y-1">
                  <p className="text-muted-foreground">FITNESS</p>
                  <p className="font-pixel text-foreground uppercase">{answers.fitness}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground">STYLE</p>
                  <p className="font-pixel text-foreground uppercase">{answers.narrative}</p>
                </div>
              </div>
              <div className="pt-2 border-t-2 border-dashed border-border space-y-1">
                <p className="text-muted-foreground text-[10px]">ACTIVITIES</p>
                <div className="flex flex-wrap gap-2">
                  {(answers.type || ['ALL']).map((t: string) => (
                    <span key={t} className="px-2 py-1 bg-primary text-primary-foreground text-[8px] font-pixel">
                      {t.toUpperCase().replace('-', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={handleComplete}
              className="w-full px-6 py-4 bg-accent text-accent-foreground font-pixel text-xs pixel-button hover:bg-accent/90 pixel-blink"
            >
              ▶ START EXPLORING
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 opacity-5" style={{
        backgroundImage: `
          repeating-linear-gradient(0deg, transparent, transparent 8px, currentColor 8px, currentColor 9px),
          repeating-linear-gradient(90deg, transparent, transparent 8px, currentColor 8px, currentColor 9px)
        `
      }} />

      <Card className="max-w-2xl w-full bg-card pixel-border relative z-10">
        <div className="bg-primary text-primary-foreground p-4 border-b-4 border-border">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs md:text-sm font-pixel text-pixel-shadow-sm">CHARACTER CREATION</h2>
            <span className="text-xs font-pixel">Q {currentQuestion + 1}/{questionnaireQuestions.length}</span>
          </div>
          <div className="health-bar-container">
            <div 
              className="health-bar-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="p-6 md:p-8 space-y-6">
          <div className="space-y-4">
            <div className="bg-muted p-4 pixel-border-sm">
              <p className="text-[10px] md:text-xs leading-relaxed text-foreground font-pixel">
                {question.question}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {question.options.map((option) => {
              const isSelected = question.type === 'multiple'
                ? (answers[question.id] || []).includes(option.value)
                : answers[question.id] === option.value;

              return (
                <button
                  key={option.value}
                  onClick={() => handleAnswer(question.id, option.value, question.type === 'multiple')}
                  className={`w-full p-4 text-left pixel-border-sm text-[10px] md:text-xs transition-all flex items-center gap-3 ${
                    isSelected
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card hover:bg-muted'
                  }`}
                >
                  <span className="text-2xl">{option.icon}</span>
                  <span className="flex-1 font-pixel">
                    {isSelected && <span className="mr-2">▶</span>}
                    {option.label.toUpperCase()}
                  </span>
                  {isSelected && (
                    <span className="text-lg">✓</span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="flex gap-3 pt-4">
            {currentQuestion > 0 && (
              <button
                onClick={handlePrevious}
                className="px-6 py-3 bg-muted text-foreground font-pixel text-[10px] md:text-xs pixel-button"
              >
                ← BACK
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={!isAnswered}
              className={`flex-1 px-6 py-3 font-pixel text-[10px] md:text-xs pixel-button ${
                !isAnswered
                  ? 'bg-muted text-muted-foreground opacity-50 cursor-not-allowed'
                  : 'bg-primary text-primary-foreground hover:bg-primary/90'
              }`}
            >
              {currentQuestion === questionnaireQuestions.length - 1 ? '✓ FINISH' : 'NEXT →'}
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
