'use client';

import { useState, useEffect } from 'react';
import { WelcomeScreen } from '@/components/welcome-screen';
import { OnboardingQuestionnaire } from '@/components/onboarding-questionnaire';
import { RouteRecommendations } from '@/components/route-recommendations';
import { UserProfile, defaultUserProfile } from '@/lib/mock-data';

export default function Home() {
  const [currentView, setCurrentView] = useState<'welcome' | 'onboarding' | 'home'>('welcome');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if user has completed onboarding
    const savedProfile = localStorage.getItem('trailsaga-profile');
    if (savedProfile) {
      setUserProfile(JSON.parse(savedProfile));
      setIsLoggedIn(true);
      setCurrentView('home');
    }
  }, []);

  const handleStartAdventure = () => {
    setCurrentView('onboarding');
  };

  const handleOnboardingComplete = (profile: UserProfile) => {
    setUserProfile(profile);
    setIsLoggedIn(true);
    localStorage.setItem('trailsaga-profile', JSON.stringify(profile));
    setCurrentView('home');
  };

  const handleGuestExplore = () => {
    setIsLoggedIn(false);
    setCurrentView('home');
  };

  if (currentView === 'welcome') {
    return (
      <WelcomeScreen 
        onStartAdventure={handleStartAdventure}
        onGuestExplore={handleGuestExplore}
      />
    );
  }

  if (currentView === 'onboarding') {
    return (
      <OnboardingQuestionnaire 
        onComplete={handleOnboardingComplete}
      />
    );
  }

  return (
    <RouteRecommendations 
      userProfile={userProfile || defaultUserProfile}
      isLoggedIn={isLoggedIn}
      onUpdateProfile={setUserProfile}
      onGoToQuestionnaire={() => setCurrentView('onboarding')}
      // </CHANGE>
    />
  );
}
