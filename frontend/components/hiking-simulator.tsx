'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Route, UserProfile, Breakpoint, MiniQuest } from '@/lib/mock-data';
import { ArrowRight, X, MapPin, Sparkles, Camera, CheckCircle2, Trophy, Target, Scroll, Compass } from 'lucide-react';
import { StoryModal } from '@/components/story-modal';
import { QuestCard } from '@/components/quest-card';
import { CompletionSummary } from '@/components/completion-summary';
import { RouteSimulationMap } from '@/components/route-simulation-map';
import { StoryOverlayModal } from '@/components/story-overlay-modal';

interface HikingSimulatorProps {
  route: Route;
  userProfile: UserProfile;
  onComplete: (route: Route, xpGained: number) => void;
  onExit: () => void;
  onViewSouvenirs?: () => void;
}

export function HikingSimulator({ 
  route, 
  userProfile,
  onComplete, 
  onExit,
  onViewSouvenirs
}: HikingSimulatorProps) {
  const [currentBreakpointIndex, setCurrentBreakpointIndex] = useState(0);
  const [showStory, setShowStory] = useState(true);
  const [activeQuest, setActiveQuest] = useState<MiniQuest | null>(null);
  const [completedQuests, setCompletedQuests] = useState<string[]>([]);
  const [totalXpGained, setTotalXpGained] = useState(0);
  const [showCompletion, setShowCompletion] = useState(false);
  const [xpAnimations, setXpAnimations] = useState<Array<{ id: string; amount: number }>>([]);
  
  const [showPrologueModal, setShowPrologueModal] = useState(false);
  const [showChapterModal, setShowChapterModal] = useState(false);
  const [showEpilogueModal, setShowEpilogueModal] = useState(false);
  const [isMovingToBreakpoint, setIsMovingToBreakpoint] = useState(false);

  // Guard against empty breakpoints array
  if (!route.breakpoints || route.breakpoints.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-primary/10 via-background to-secondary/10 flex items-center justify-center">
        <Card className="p-8 border-4 border-destructive">
          <h2 className="text-2xl font-bold text-destructive mb-4">Invalid Route</h2>
          <p className="text-muted-foreground mb-4">
            This route has no breakpoints. Please select a different route.
          </p>
          <Button onClick={onExit}>Go Back</Button>
        </Card>
      </div>
    );
  }

  // Ensure index is within bounds
  const safeIndex = Math.min(currentBreakpointIndex, route.breakpoints.length - 1);
  const currentBreakpoint = route.breakpoints[safeIndex];
  const progress = route.breakpoints.length > 1 
    ? (safeIndex / (route.breakpoints.length - 1)) * 100 
    : 0;
  const isLastBreakpoint = safeIndex === route.breakpoints.length - 1;

  useEffect(() => {
    if (route.prologue) {
      setShowPrologueModal(true);
    }
  }, [route.prologue]);

  useEffect(() => {
    if (isLastBreakpoint && !showEpilogueModal && !showCompletion && !showPrologueModal) {
      const hasQuestAtFinal = currentBreakpoint?.quest && !completedQuests.includes(currentBreakpoint.quest.id);
      
      if (!hasQuestAtFinal) {
        if (route.epilogue) {
          setShowEpilogueModal(true);
        } else {
          handleRouteCompletion();
        }
      }
    }
  }, [isLastBreakpoint, completedQuests, showPrologueModal, currentBreakpoint, showEpilogueModal, showCompletion, route.epilogue]);

  const handleNextBreakpoint = () => {
    if (!isLastBreakpoint) {
      setIsMovingToBreakpoint(true);
      
      setTimeout(() => {
        const nextIndex = safeIndex + 1;
        setCurrentBreakpointIndex(nextIndex);
        setIsMovingToBreakpoint(false);
        
        const nextBreakpoint = route.breakpoints[nextIndex];
        if (nextBreakpoint?.content) {
          setShowChapterModal(true);
        }
      }, 800);
    }
  };

  const handlePrologueContinue = () => {
    setShowPrologueModal(false);
  };

  const handleChapterContinue = () => {
    setShowChapterModal(false);
  };

  const handleAcceptQuestFromModal = () => {
    setShowChapterModal(false);
    if (currentBreakpoint?.quest && !completedQuests.includes(currentBreakpoint.quest.id)) {
      setActiveQuest(currentBreakpoint.quest);
    }
  };

  const handleEpilogueContinue = () => {
    setShowEpilogueModal(false);
    handleRouteCompletion();
  };

  const handleQuestComplete = (quest: MiniQuest) => {
    setCompletedQuests([...completedQuests, quest.id]);
    setTotalXpGained(totalXpGained + quest.xpReward);
    
    const animId = `xp-${Date.now()}`;
    setXpAnimations([...xpAnimations, { id: animId, amount: quest.xpReward }]);
    setTimeout(() => {
      setXpAnimations(prev => prev.filter(a => a.id !== animId));
    }, 1500);

    setActiveQuest(null);

    if (isLastBreakpoint) {
      setTimeout(() => {
        if (route.epilogue) {
          setShowEpilogueModal(true);
        } else {
          handleRouteCompletion();
        }
      }, 1600);
    }
  };

  const handleRouteCompletion = () => {
    const baseXp = route.xpReward;
    const questBonus = totalXpGained;
    const difficultyMultiplier = {
      'easy': 1,
      'medium': 1.2,
      'hard': 1.5,
      'expert': 2
    }[route.difficulty];
    
    const totalXp = Math.round((baseXp + questBonus) * difficultyMultiplier);
    
    setTotalXpGained(totalXp);
    setShowCompletion(true);
  };

  const handleCompletionClose = () => {
    onComplete(route, totalXpGained);
  };

  const handleViewSouvenirs = () => {
    console.log('[v0] handleViewSouvenirs called');
    if (onViewSouvenirs) {
      onViewSouvenirs();
    }
  };

  const totalQuests = route.breakpoints.filter(bp => bp.quest).length;
  const currentQuestAtBreakpoint = currentBreakpoint?.quest && !completedQuests.includes(currentBreakpoint.quest.id);

  if (showCompletion) {
    return (
      <CompletionSummary
        route={route}
        userProfile={userProfile}
        xpGained={totalXpGained}
        questsCompleted={completedQuests.length}
        onClose={handleCompletionClose}
        onViewSouvenirs={handleViewSouvenirs}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/10 via-background to-secondary/10 pb-32">
      {showPrologueModal && route.prologue && (
        <StoryOverlayModal
          type="prologue"
          title={route.name}
          routeName={route.name}
          content={route.prologue}
          ctaText="Begin Journey"
          onContinue={handlePrologueContinue}
        />
      )}

      {showChapterModal && currentBreakpoint?.content && (
        <StoryOverlayModal
          type="chapter"
          title={currentBreakpoint.name}
          routeName={route.name}
                  chapterNumber={safeIndex + 1}
          content={currentBreakpoint.content}
          ctaText="Continue"
          onContinue={handleChapterContinue}
          questTitle={currentBreakpoint?.quest && !completedQuests.includes(currentBreakpoint.quest.id) ? currentBreakpoint.quest.title : undefined}
          questDescription={currentBreakpoint?.quest && !completedQuests.includes(currentBreakpoint.quest.id) ? currentBreakpoint.quest.description : undefined}
          onAcceptQuest={handleAcceptQuestFromModal}
        />
      )}

      {showEpilogueModal && route.epilogue && (
        <StoryOverlayModal
          type="epilogue"
          title={route.name}
          routeName={route.name}
          content={route.epilogue}
          ctaText="View Summary & Souvenir"
          onContinue={handleEpilogueContinue}
        />
      )}

      <header className="border-b-4 border-border bg-card/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <h1 className="text-xl md:text-2xl font-bold text-foreground">{route.name}</h1>
                <Badge variant="secondary" className="text-xs font-bold border-2 border-accent">
                  SIMULATION MODE
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Click 'Next Breakpoint' to move along the route and trigger story events & quests.
              </p>
            </div>
            <Button variant="outline" size="icon" onClick={onExit} className="border-2">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <div className="fixed top-20 right-8 z-50 pointer-events-none">
        {xpAnimations.map((anim) => (
          <div
            key={anim.id}
            className="xp-animation text-2xl font-bold text-accent"
          >
            +{anim.amount} XP
          </div>
        ))}
      </div>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <div>
            <RouteSimulationMap
              route={route}
              currentBreakpointIndex={safeIndex}
              completedBreakpoints={completedQuests}
            />
          </div>

          <Card className="p-6 border-4 border-primary bg-card/95 shadow-lg">
            {currentQuestAtBreakpoint ? (
              <>
                <div className="flex items-start gap-3 mb-4">
                  <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
                    <Target className="w-6 h-6 text-accent" />
                  </div>
                  <div className="flex-1">
                    <Badge variant="outline" className="text-xs mb-2 border-accent bg-accent/10 text-accent">
                      MINI QUEST
                    </Badge>
                    <h2 className="text-2xl font-bold text-foreground mb-2">
                      {currentBreakpoint?.name || 'Unknown Location'}
                    </h2>
                  </div>
                </div>
                
                <div className="bg-accent/10 p-4 rounded-lg mb-4 border-2 border-accent">
                  <p className="text-sm text-foreground leading-relaxed mb-3">
                    {currentBreakpoint?.quest?.description || 'No description available'}
                  </p>
                  <div className="flex items-center gap-2 text-sm">
                    <Sparkles className="w-4 h-4 text-accent" />
                    <span className="font-semibold text-accent">+{currentBreakpoint?.quest?.xpReward || 0} XP</span>
                    <span className="text-muted-foreground">· +1 Memory</span>
                  </div>
                </div>

                <Button
                  onClick={() => currentBreakpoint?.quest && setActiveQuest(currentBreakpoint.quest)}
                  className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-bold border-4 border-border"
                  size="lg"
                >
                  Accept Quest
                </Button>
              </>
            ) : (
              <>
                <div className="flex items-start gap-3 mb-4">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <Compass className="w-6 h-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-foreground mb-2">
                      Chapter {safeIndex + 1} • {currentBreakpoint?.name || 'Unknown'}
                    </h2>
                  </div>
                </div>

                <div className="bg-muted/30 p-4 rounded-lg mb-4 border-2 border-muted">
                  <p className="text-sm text-foreground/80 italic leading-relaxed">
                    "A quiet moment where the journey reveals its character."
                  </p>
                </div>

                <div className="space-y-4 bg-muted/20 p-4 rounded-lg border-2 border-border">
                  <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wide mb-3">
                    Route Progress
                  </h3>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Breakpoints</span>
                      <span className="font-semibold text-foreground">
                        {safeIndex + 1} / {route.breakpoints.length}
                      </span>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Distance walked</span>
                      <span className="font-semibold text-foreground">
                        {currentBreakpoint?.distance || 0} / {route.distance} km
                      </span>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Mini Quests completed</span>
                      <span className="font-semibold text-foreground">
                        {completedQuests.length} / {totalQuests}
                      </span>
                    </div>

                    <div className="pt-2 border-t-2 border-border">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-muted-foreground">XP</span>
                        <span className="font-semibold text-foreground">
                          {totalXpGained} / {route.xpReward}
                        </span>
                      </div>
                      <Progress 
                        value={(totalXpGained / route.xpReward) * 100} 
                        className="h-2" 
                      />
                    </div>
                  </div>
                </div>
              </>
            )}
          </Card>
        </div>

        {activeQuest && (
          <div className="mb-8">
            <QuestCard
              quest={activeQuest}
              onComplete={() => handleQuestComplete(activeQuest)}
              onSkip={isLastBreakpoint ? () => {
                setActiveQuest(null);
                setTimeout(() => {
                  if (route.epilogue) {
                    setShowEpilogueModal(true);
                  } else {
                    handleRouteCompletion();
                  }
                }, 100);
              } : undefined}
            />
          </div>
        )}

        <Card className="mt-6 p-4 border-2 border-secondary bg-secondary/10">
          <div className="flex items-center gap-3">
            <Trophy className="w-6 h-6 text-secondary flex-shrink-0" />
            <p className="text-sm text-foreground">
              <span className="font-bold">Reward awaits!</span> Finish this route to unlock a Digital Souvenir in your gallery.
            </p>
          </div>
        </Card>
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-card/95 backdrop-blur-sm border-t-4 border-border shadow-2xl z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <Button
              size="lg"
              className="px-8 py-6 text-base bg-primary hover:bg-primary/90 text-primary-foreground font-bold shadow-lg border-4 border-border"
              onClick={handleNextBreakpoint}
              disabled={isMovingToBreakpoint || showPrologueModal || showChapterModal || showEpilogueModal || !!activeQuest || isLastBreakpoint}
            >
              Next Breakpoint
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
