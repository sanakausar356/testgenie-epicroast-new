import React from "react";

interface SectionCardProps {
  title: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export default function SectionCard({ title, children, icon, className = "" }: SectionCardProps) {
  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 shadow-sm ${className}`}>
      <div className="flex items-center space-x-2 mb-3">
        {icon && <span className="text-lg">{icon}</span>}
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      </div>
      <div className="text-gray-700">
        {children}
      </div>
    </div>
  );
}
