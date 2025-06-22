
import type { PatientStudy } from '../../types/dicom.types';

interface StatusIndicatorProps {
  status: PatientStudy['dicomPdfStatus'];
  className?: string;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function StatusIndicator({ 
  status, 
  className = '', 
  showText = true,
  size = 'md'
}: StatusIndicatorProps) {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  const getStatusConfig = (status: PatientStudy['dicomPdfStatus']) => {
    switch (status) {
      case 'pending':
        return {
          color: 'bg-yellow-400',
          text: 'Pending',
          textColor: 'text-yellow-400',
          containerClass: 'status-pending',
          icon: (
            <svg className={sizeClasses[size]} fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          ),
        };
      case 'processing':
        return {
          color: 'bg-blue-400 animate-pulse',
          text: 'Processing',
          textColor: 'text-blue-400',
          containerClass: 'status-processing',
          icon: (
            <div className={`loading-spinner ${sizeClasses[size]}`} />
          ),
        };
      case 'completed':
        return {
          color: 'bg-green-400',
          text: 'Completed',
          textColor: 'text-green-400',
          containerClass: 'status-completed',
          icon: (
            <svg className={sizeClasses[size]} fill="currentColor" viewBox="0 0 24 24">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          ),
        };
      case 'error':
        return {
          color: 'bg-red-400',
          text: 'Error',
          textColor: 'text-red-400',
          containerClass: 'status-error',
          icon: (
            <svg className={sizeClasses[size]} fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          ),
        };
      default:
        return {
          color: 'bg-gray-400',
          text: 'Unknown',
          textColor: 'text-gray-400',
          containerClass: 'status-indicator',
          icon: (
            <div className={`rounded-full ${sizeClasses[size]} bg-gray-400`} />
          ),
        };
    }
  };

  const config = getStatusConfig(status);

  if (showText) {
    return (
      <div className={`status-indicator ${config.containerClass} ${className}`}>
        {config.icon}
        <span className={textSizeClasses[size]}>
          {config.text}
        </span>
      </div>
    );
  }

  return (
    <div 
      className={`${className}`}
      title={config.text}
    >
      {config.icon}
    </div>
  );
}