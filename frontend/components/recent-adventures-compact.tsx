'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Route, UserProfile } from '@/lib/mock-data';
import { MapPin, ArrowRight, Sparkles } from 'lucide-react';

interface RecentAdventuresCompactProps {
  userProfile: UserProfile;
  routes: Route[];
  onContinue: (route: Route) => void;
  onViewAll: () => void;
}

export function RecentAdventuresCompact({ 
  userProfile, 
  routes, 
  onContinue,
  onViewAll 
}: RecentAdventuresCompactProps) {
  // Find the most recent in-progress route (if any)
  // For now, we'll just show the first completed route as an example
  const recentRoute = routes[0];
  
  if (!recentRoute) {
    return null;
  }

  return (
    <Card className="p-4 border-2 border-border bg-card/50 hover:bg-card transition-colors">
      <div className="flex items-center justify-between gap-4">
        {/* Route Info */}
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* Small thumbnail */}
          <div className="w-16 h-16 flex-shrink-0 border-2 border-border overflow-hidden">
            <img
              src={recentRoute.imageUrl || "/placeholder.svg"}
              alt={recentRoute.name}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Details */}
          <div className="flex-1 min-w-0">
            <p className="text-xs text-muted-foreground font-semibold mb-1">
              Continue:
            </p>
            <h3 className="font-bold text-foreground truncate mb-1">
              {recentRoute.name}
            </h3>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {recentRoute.location}
              </span>
              <span className="flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                {recentRoute.xpReward} XP
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Button 
            size="sm"
            variant="outline"
            onClick={onViewAll}
            className="border-2 hidden sm:flex"
          >
            View all adventures
          </Button>
          <Button 
            size="sm"
            onClick={() => onContinue(recentRoute)}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
          >
            Continue
            <ArrowRight className="ml-1 w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
