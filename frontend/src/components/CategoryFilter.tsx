import React, { useState, useEffect } from 'react';
import { ChevronDown, X } from 'lucide-react';

interface CategoryFilterProps {
  categories: string[];
  selectedCategories: string[];
  onCategoryChange: (categories: string[]) => void;
  loading?: boolean;
}

const CategoryFilter: React.FC<CategoryFilterProps> = ({
  categories,
  selectedCategories,
  onCategoryChange,
  loading = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.category-filter')) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleCategoryToggle = (category: string) => {
    const updatedCategories = selectedCategories.includes(category)
      ? selectedCategories.filter((c) => c !== category)
      : [...selectedCategories, category];
    
    onCategoryChange(updatedCategories);
  };

  const handleSelectAll = () => {
    onCategoryChange(categories);
  };

  const handleClearAll = () => {
    onCategoryChange([]);
  };

  const getDisplayText = () => {
    if (selectedCategories.length === 0) {
      return 'All Categories';
    }
    if (selectedCategories.length === 1) {
      return selectedCategories[0];
    }
    if (selectedCategories.length === categories.length) {
      return 'All Categories';
    }
    return `${selectedCategories.length} categories selected`;
  };

  if (loading) {
    return (
      <div className="category-filter relative w-64">
        <div className="w-full px-3 py-2 border border-border rounded-md bg-muted">
          <div className="animate-pulse h-5 bg-muted-foreground/20 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="category-filter relative w-64">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 text-left border border-border rounded-md bg-background hover:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors"
      >
        <div className="flex items-center justify-between">
          <span className="truncate">{getDisplayText()}</span>
          <ChevronDown
            className={`w-4 h-4 transition-transform ${
              isOpen ? 'transform rotate-180' : ''
            }`}
          />
        </div>
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-background border border-border rounded-md shadow-lg max-h-64 overflow-y-auto">
          {/* Header with controls */}
          <div className="px-3 py-2 border-b border-border bg-muted/50">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Categories</span>
              <div className="flex gap-2">
                <button
                  onClick={handleSelectAll}
                  className="text-xs text-primary hover:text-primary/80"
                >
                  All
                </button>
                <button
                  onClick={handleClearAll}
                  className="text-xs text-muted-foreground hover:text-foreground"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>

          {/* Category list */}
          <div className="py-1">
            {categories.map((category) => (
              <label
                key={category}
                className="flex items-center px-3 py-2 hover:bg-muted/50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedCategories.includes(category)}
                  onChange={() => handleCategoryToggle(category)}
                  className="w-4 h-4 text-primary border-border rounded focus:ring-primary focus:ring-2"
                />
                <span className="ml-3 text-sm">{category}</span>
              </label>
            ))}
          </div>

          {/* Selected categories chips */}
          {selectedCategories.length > 0 && selectedCategories.length < categories.length && (
            <div className="px-3 py-2 border-t border-border bg-muted/30">
              <div className="flex flex-wrap gap-1">
                {selectedCategories.map((category) => (
                  <span
                    key={category}
                    className="inline-flex items-center px-2 py-1 text-xs bg-primary/10 text-primary rounded-md"
                  >
                    {category}
                    <button
                      onClick={() => handleCategoryToggle(category)}
                      className="ml-1 hover:bg-primary/20 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CategoryFilter;