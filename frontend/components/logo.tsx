import React from 'react';

export const Logo = ({ className = "w-10 h-10" }: { className?: string }) => (
  <svg 
    viewBox="0 0 512 512" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg" 
    className={className}
  >
    <defs>
      <linearGradient id="prism-grad-1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#22d3ee" /> {/* Cyan */}
        <stop offset="100%" stopColor="#6366f1" /> {/* Indigo */}
      </linearGradient>
      
      <linearGradient id="prism-grad-2" x1="100%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#818cf8" /> {/* Indigo Light */}
        <stop offset="100%" stopColor="#a855f7" /> {/* Purple */}
      </linearGradient>

      <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="10" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>

    <g filter="url(#neon-glow)">
      {/* Left Facet */}
      <path 
        d="M256 96 L160 256 L256 416 L256 256 Z" 
        fill="url(#prism-grad-1)" 
        fillOpacity="0.9" 
        stroke="#67e8f9" 
        strokeWidth="4" 
      />
      
      {/* Right Facet */}
      <path 
        d="M256 96 L352 256 L256 416 L256 256 Z" 
        fill="url(#prism-grad-2)" 
        fillOpacity="0.8" 
        stroke="#d8b4fe" 
        strokeWidth="4" 
      />
      
      {/* Horizontal Spark Line */}
      <path 
        d="M140 256 L372 256" 
        stroke="white" 
        strokeWidth="2" 
        strokeOpacity="0.4" 
      />
    </g>
  </svg>
);