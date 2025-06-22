

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  message?: string;
}

export default function LoadingSpinner({ 
  size = 'md', 
  className = '', 
  message 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div className={`loading-spinner ${sizeClasses[size]}`} />
      {message && (
        <p className="mt-2 text-sm text-blue-300 animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
}