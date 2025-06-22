

interface A4ContainerProps {
  children: React.ReactNode;
  scale?: 'desktop' | 'tablet' | 'mobile' | 'print';
  className?: string;
}

export default function A4Container({ 
  children, 
  scale = 'desktop',
  className = '' 
}: A4ContainerProps) {
  const scaleClasses = {
    desktop: 'a4-preview-desktop',
    tablet: 'a4-preview-tablet', 
    mobile: 'a4-preview-mobile',
    print: '',
  };

  const containerStyle = scale === 'print' ? {} : {
    width: `${794 * getScaleFactor(scale)}px`,
    height: `${1123 * getScaleFactor(scale)}px`,
  };

  return (
    <div 
      className={`${className}`}
      style={containerStyle}
    >
      <div className={`a4-container ${scaleClasses[scale]}`}>
        <div className="a4-content">
          {children}
        </div>
      </div>
    </div>
  );
}

function getScaleFactor(scale: A4ContainerProps['scale']): number {
  switch (scale) {
    case 'desktop': return 0.4;
    case 'tablet': return 0.3;
    case 'mobile': return 0.2;
    case 'print': return 1.0;
    default: return 0.4;
  }
}