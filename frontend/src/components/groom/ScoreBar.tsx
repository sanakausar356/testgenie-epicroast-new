import React from "react";

interface ScoreBarProps {
  score: number;
  maxScore?: number;
  label?: string;
  showValue?: boolean;
}

export default function ScoreBar({ score, maxScore = 100, label, showValue = true }: ScoreBarProps) {
  const percentage = Math.min((score / maxScore) * 100, 100);
  
  const getColorClass = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    return "bg-red-500";
  };
  
  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>{label}</span>
          {showValue && <span>{score}/{maxScore}</span>}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${getColorClass(score)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
