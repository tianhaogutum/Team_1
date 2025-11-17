'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DigitalSouvenir } from '@/lib/mock-data';
import { Trophy, MapPin, Sparkles, ArrowRight } from 'lucide-react';

interface SouvenirSpotlightProps {
  souvenirs: DigitalSouvenir[];
  onViewAll: () => void;
}

export function SouvenirSpotlight({ souvenirs, onViewAll }: SouvenirSpotlightProps) {
  if (souvenirs.length === 0) {
    return null;
  }

  const mostRecent = souvenirs[0];
  const totalSouvenirs = souvenirs.length;

  return (
    <Card className="p-5 border-4 border-accent/50 bg-gradient-to-br from-accent/10 to-accent/5">
      <div className="flex items-start justify-between gap-4">
        {/* Left: Collection Info */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Trophy className="w-6 h-6 text-accent" />
            <h2 className="text-xl font-bold text-foreground">Souvenir Collection</h2>
          </div>
          
          <p className="text-sm text-muted-foreground mb-4">
            <span className="font-bold text-accent">{totalSouvenirs} {totalSouvenirs === 1 ? 'Souvenir' : 'Souvenirs'}</span> collected
          </p>

          {/* Most Recent Preview */}
          <div className="flex items-center gap-3 p-3 border-2 border-border bg-card/50 mb-3">
            {/* Small thumbnail */}
            <div className="w-12 h-12 flex-shrink-0 border-2 border-border overflow-hidden">
              <img
                src={mostRecent.imageUrl || "/placeholder.svg"}
                alt={mostRecent.routeName}
                className="w-full h-full object-cover"
              />
            </div>
            
            {/* Info */}
            <div className="flex-1 min-w-0">
              <p className="text-xs text-muted-foreground font-semibold mb-0.5">
                Latest adventure:
              </p>
              <p className="font-bold text-foreground text-sm truncate">
                {mostRecent.routeName}
              </p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {mostRecent.location}
                </span>
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-accent" />
                  +{mostRecent.xpGained} XP
                </span>
              </div>
            </div>
          </div>

          {/* CTA Button */}
          <Button 
            onClick={onViewAll}
            className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-semibold"
          >
            Open Gallery
            <ArrowRight className="ml-2 w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
