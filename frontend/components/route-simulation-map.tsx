'use client';

import { Route, Breakpoint } from '@/lib/mock-data';
import { MapPin, CheckCircle2, Sparkles, Target } from 'lucide-react';

interface RouteSimulationMapProps {
  route: Route;
  currentBreakpointIndex: number;
  completedBreakpoints: string[];
}

export function RouteSimulationMap({ 
  route, 
  currentBreakpointIndex,
  completedBreakpoints 
}: RouteSimulationMapProps) {
  const breakpoints = route.breakpoints;
  
  // Generate a curved path through breakpoints
  const generatePath = () => {
    const width = 400;
    const height = 300;
    const padding = 40;
    
    // Calculate positions for breakpoints
    const positions = breakpoints.map((_, index) => {
      const progress = index / (breakpoints.length - 1);
      const x = padding + progress * (width - 2 * padding);
      // Create a wavy path
      const y = height / 2 + Math.sin(progress * Math.PI * 2) * 60;
      return { x, y };
    });
    
    // Create SVG path
    let pathD = `M ${positions[0].x} ${positions[0].y}`;
    for (let i = 1; i < positions.length; i++) {
      const prev = positions[i - 1];
      const curr = positions[i];
      const midX = (prev.x + curr.x) / 2;
      pathD += ` Q ${midX} ${prev.y}, ${curr.x} ${curr.y}`;
    }
    
    return { pathD, positions, width, height };
  };
  
  const { pathD, positions, width, height } = generatePath();
  
  return (
    <div className="relative w-full bg-gradient-to-br from-primary/5 to-secondary/5 rounded-lg border-4 border-border p-4">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
          <MapPin className="w-5 h-5 text-primary" />
          Route Map
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Follow the path and complete each breakpoint
        </p>
      </div>
      
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        style={{ maxHeight: '300px' }}
      >
        {/* Background path */}
        <path
          d={pathD}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          className="text-muted/30"
        />
        
        {/* Completed path */}
        {currentBreakpointIndex > 0 && (
          <path
            d={pathD}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(currentBreakpointIndex / (breakpoints.length - 1)) * 100}% 100%`}
            className="text-primary transition-all duration-500"
          />
        )}
        
        {/* Breakpoint markers */}
        {positions.map((pos, index) => {
          const bp = breakpoints[index];
          const isPast = index < currentBreakpointIndex;
          const isCurrent = index === currentBreakpointIndex;
          const isCompleted = completedBreakpoints.includes(bp.id);
          
          return (
            <g key={bp.id}>
              {/* Marker circle */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={isCurrent ? 16 : 12}
                fill="currentColor"
                className={
                  isCurrent 
                    ? 'text-primary animate-pulse' 
                    : isPast 
                    ? 'text-primary' 
                    : 'text-muted'
                }
                stroke={isCurrent ? 'currentColor' : 'none'}
                strokeWidth={isCurrent ? 4 : 0}
                className={`${isCurrent ? 'text-accent' : ''} transition-all duration-300`}
              />
              
              {/* Icon inside marker */}
              {isPast && (
                <text
                  x={pos.x}
                  y={pos.y}
                  textAnchor="middle"
                  dominantBaseline="central"
                  className="text-xs fill-primary-foreground font-bold"
                >
                  ✓
                </text>
              )}
              
              {isCurrent && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={8}
                  fill="currentColor"
                  className="text-accent-foreground"
                />
              )}
              
              {/* Quest indicator */}
              {bp.type === 'quest' && !isCompleted && index <= currentBreakpointIndex && (
                <circle
                  cx={pos.x + 12}
                  cy={pos.y - 12}
                  r={6}
                  fill="currentColor"
                  className="text-accent animate-bounce"
                />
              )}
              
              {/* Label */}
              <text
                x={pos.x}
                y={pos.y + (index % 2 === 0 ? 30 : -20)}
                textAnchor="middle"
                className={`text-xs font-bold fill-current ${
                  isCurrent ? 'text-primary' : 'text-foreground'
                }`}
              >
                {bp.name}
              </text>
            </g>
          );
        })}
        
        {/* Character icon at current position */}
        {currentBreakpointIndex < positions.length && (
          <g className="transition-all duration-500">
            <circle
              cx={positions[currentBreakpointIndex].x}
              cy={positions[currentBreakpointIndex].y - 25}
              r="15"
              fill="currentColor"
              className="text-accent"
            />
            <text
              x={positions[currentBreakpointIndex].x}
              y={positions[currentBreakpointIndex].y - 25}
              textAnchor="middle"
              dominantBaseline="central"
              className="text-lg"
            >
              🎒
            </text>
          </g>
        )}
      </svg>
      
      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-primary" />
          <span className="text-muted-foreground">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-accent animate-pulse" />
          <span className="text-muted-foreground">Current</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-muted" />
          <span className="text-muted-foreground">Upcoming</span>
        </div>
      </div>
    </div>
  );
}
