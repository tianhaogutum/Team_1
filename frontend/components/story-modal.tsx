'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Scroll, ArrowRight } from 'lucide-react';

interface StoryModalProps {
  title: string;
  content: string;
  narrativeStyle: string;
  onContinue: () => void;
}

export function StoryModal({ title, content, narrativeStyle, onContinue }: StoryModalProps) {
  return (
    <Card className="p-8 border-4 border-border bg-card/95 shadow-2xl quest-card-appear">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <div className="w-16 h-16 rounded-full bg-secondary/20 flex items-center justify-center">
              <Scroll className="w-8 h-8 text-secondary" />
            </div>
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-foreground">{title}</h2>
          <div className="inline-block px-4 py-1 bg-secondary/20 rounded-full">
            <p className="text-sm font-semibold text-secondary capitalize">{narrativeStyle} Tale</p>
          </div>
        </div>

        {/* Story Content */}
        <div className="p-6 bg-muted/30 rounded-lg border-2 border-border">
          <p className="text-foreground leading-relaxed text-lg text-center italic">
            "{content}"
          </p>
        </div>

        {/* Continue Button */}
        <div className="flex justify-center pt-2">
          <Button
            size="lg"
            className="px-8 py-6 text-lg bg-secondary hover:bg-secondary/90 text-secondary-foreground font-semibold"
            onClick={onContinue}
          >
            Continue Your Journey
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
