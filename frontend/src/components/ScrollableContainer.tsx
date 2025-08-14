import React from 'react';

interface ScrollableContainerProps {
  children: React.ReactNode;
  className?: string;
  maxHeight?: string;
}

const ScrollableContainer: React.FC<ScrollableContainerProps> = ({ 
  children, 
  className = '', 
  maxHeight = 'max-h-96' 
}) => {
  return (
    <div className={`
      ${maxHeight} 
      overflow-y-auto 
      scrollbar-thin 
      scrollbar-thumb-gray-300 
      scrollbar-track-gray-100 
      hover:scrollbar-thumb-gray-400 
      pr-2
      ${className}
    `}>
      {children}
    </div>
  );
};

export default ScrollableContainer;