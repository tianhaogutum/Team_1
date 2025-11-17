'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DigitalSouvenir } from '@/lib/mock-data';
import { Trophy, MapPin, Calendar, Sparkles, X, Mountain, Footprints, TrendingUp } from 'lucide-react';

interface SouvenirGalleryProps {
  souvenirs: DigitalSouvenir[];
  onClose: () => void;
}

export function SouvenirGallery({ souvenirs, onClose }: SouvenirGalleryProps) {
  const [filterType, setFilterType] = useState<'all' | 'hiking' | 'city-walk' | 'trail-running'>('all');

  const filteredSouvenirs = souvenirs
    .sort((a, b) => new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime());

  const stats = {
    total: souvenirs.length,
    totalXP: souvenirs.reduce((sum, s) => sum + s.xpGained, 0),
    totalDistance: souvenirs.reduce((sum, s) => sum + s.distance, 0)
  };

  return (
    <div className="fixed inset-0 bg-background z-50 overflow-y-auto">
      {/* Header */}
      <header className="border-b-4 border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Trophy className="w-8 h-8 text-accent" strokeWidth={2.5} />
              <h1 className="text-2xl font-bold text-foreground">
                My Souvenir Gallery
              </h1>
            </div>
            <Button variant="outline" size="icon" onClick={onClose} className="border-2">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-6 text-center">
          <p className="text-lg text-foreground">
            You've collected <span className="font-bold text-accent">{stats.total}</span> adventure {stats.total === 1 ? 'souvenir' : 'souvenirs'}. 
            <br />
            <span className="text-muted-foreground">Keep exploring to expand your collection.</span>
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <Card className="p-6 border-2 border-border bg-gradient-to-br from-primary/10 to-primary/5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <Trophy className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Adventures</p>
                <p className="text-2xl font-bold text-foreground">{stats.total}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6 border-2 border-border bg-gradient-to-br from-accent/10 to-accent/5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-accent" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total XP Earned</p>
                <p className="text-2xl font-bold text-foreground">{stats.totalXP}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6 border-2 border-border bg-gradient-to-br from-secondary/10 to-secondary/5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                <Footprints className="w-6 h-6 text-secondary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Distance</p>
                <p className="text-2xl font-bold text-foreground">{stats.totalDistance.toFixed(1)} km</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Souvenir Grid */}
        {filteredSouvenirs.length === 0 ? (
          <Card className="p-12 text-center border-2 border-border">
            <Trophy className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-bold text-foreground mb-2">No Souvenirs Yet</h2>
            <p className="text-muted-foreground">
              Complete your first route to earn your first digital souvenir!
            </p>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSouvenirs.map((souvenir) => (
              <Card 
                key={souvenir.id}
                className="overflow-hidden border-4 border-border hover:shadow-2xl transition-all"
              >
                {/* Image */}
                <div className="relative h-48 bg-muted">
                  <img
                    src={souvenir.imageUrl || "/placeholder.svg"}
                    alt={souvenir.routeName}
                    className="w-full h-full object-cover"
                  />
                  <Badge 
                    className="absolute top-2 left-2" 
                    variant={souvenir.difficulty === 'easy' ? 'secondary' : 'default'}
                  >
                    {souvenir.difficulty}
                  </Badge>
                  <div className="absolute top-2 right-2 bg-accent text-accent-foreground px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                    <Trophy className="w-4 h-4" />
                    Completed
                  </div>
                </div>

                {/* Content */}
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="text-xl font-bold text-foreground mb-1">
                      {souvenir.routeName}
                    </h3>
                    <p className="text-sm text-muted-foreground flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {souvenir.location}
                    </p>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-muted-foreground">Distance</p>
                      <p className="font-semibold text-foreground">{souvenir.distance} km</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">XP Earned</p>
                      <p className="font-semibold text-accent">{souvenir.xpGained} XP</p>
                    </div>
                  </div>

                  {/* Date */}
                  <div className="pt-3 border-t-2 border-border flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      {new Date(souvenir.completedAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>

                  {/* Badges */}
                  {souvenir.badgesEarned.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {souvenir.badgesEarned.map((badge, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {badge}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
