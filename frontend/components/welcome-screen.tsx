'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface WelcomeScreenProps {
  onStartAdventure: () => void;
  onGuestExplore: () => void;
}

export function WelcomeScreen({ onStartAdventure, onGuestExplore }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 opacity-5" style={{
        backgroundImage: `
          repeating-linear-gradient(0deg, transparent, transparent 8px, currentColor 8px, currentColor 9px),
          repeating-linear-gradient(90deg, transparent, transparent 8px, currentColor 8px, currentColor 9px)
        `
      }} />
      
      <Card className="max-w-3xl w-full p-8 md:p-12 bg-card pixel-border relative z-10">
        <div className="text-center space-y-8">
          <div className="flex justify-center mb-4">
            <div className="text-primary text-6xl md:text-7xl leading-none select-none">
              ⛰️
            </div>
          </div>

          <div className="space-y-4">
            <h1 className="text-2xl md:text-4xl font-pixel text-foreground text-pixel-shadow leading-relaxed">
              TRAIL<span className="text-primary">SAGA</span>
            </h1>
            <p className="text-xs md:text-sm text-muted-foreground max-w-md mx-auto leading-relaxed">
              YOUR OUTDOOR ADVENTURE AWAITS
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-4 py-6">
            <div className="p-4 bg-muted pixel-border-sm space-y-2">
              <div className="text-3xl">⚔️</div>
              <h3 className="text-xs font-pixel text-foreground">QUESTS</h3>
              <p className="text-[10px] leading-relaxed text-muted-foreground">Complete challenges</p>
            </div>
            <div className="p-4 bg-muted pixel-border-sm space-y-2">
              <div className="text-3xl">📈</div>
              <h3 className="text-xs font-pixel text-foreground">LEVEL UP</h3>
              <p className="text-[10px] leading-relaxed text-muted-foreground">Gain XP & unlock</p>
            </div>
            <div className="p-4 bg-muted pixel-border-sm space-y-2">
              <div className="text-3xl">🎭</div>
              <h3 className="text-xs font-pixel text-foreground">STORIES</h3>
              <p className="text-[10px] leading-relaxed text-muted-foreground">AI narratives</p>
            </div>
          </div>

          <div className="flex flex-col gap-4 justify-center pt-4">
            <button
              className="px-6 py-4 bg-primary text-primary-foreground font-pixel text-xs pixel-button hover:bg-primary/90 transition-colors"
              onClick={onStartAdventure}
            >
              ▶ BEGIN YOUR SAGA
            </button>
            <button
              className="text-xs text-muted-foreground hover:text-foreground transition-colors underline"
              onClick={onGuestExplore}
            >
              Browse all routes (no personalization)
            </button>
          </div>
          {/* </CHANGE> */}

          {/* </CHANGE> */}
        </div>
      </Card>
    </div>
  );
}
