# KPI Dashboard Collapse Feature Implementation

## Overview
Added collapsible KPI Dashboard functionality to all HON Automated Reporting dashboards, allowing users to hide performance overview cards for cleaner client screenshots.

## Implementation Details

### ✅ Dashboards Updated
1. **Meta Ad Level Dashboard** (`AdLevelDashboard.tsx`)
2. **Meta Ads Dashboard** (`ModernDashboard.tsx`) 
3. **Google Ads Dashboard** (`GoogleDashboard.tsx`)
4. **TikTok Ads Dashboard** (`TikTokDashboard.tsx`)
5. **TikTok Ad Level Dashboard** (`TikTokAdLevelDashboard.tsx`)

### 🎨 Design Pattern
Each dashboard now features:

- **Toggle Header**: "Performance Overview" with Show/Hide button
- **Smooth Animation**: CSS transitions for collapse/expand (300ms ease-in-out)
- **Consistent Styling**: Matching the existing filter panel design
- **Icon Indicators**: ChevronRight (collapsed) / ChevronDown (expanded)
- **Default State**: KPI cards visible by default (`kpiCollapsed = false`)

### 🔧 Technical Implementation

#### State Management
```tsx
const [kpiCollapsed, setKpiCollapsed] = useState(false);
```

#### Toggle Button
```tsx
<button
  onClick={() => setKpiCollapsed(!kpiCollapsed)}
  className="flex items-center space-x-1 px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200"
>
  <span>{kpiCollapsed ? 'Show' : 'Hide'}</span>
  {kpiCollapsed ? (
    <ChevronRightIcon className="w-4 h-4" />
  ) : (
    <ChevronDownIcon className="w-4 h-4" />
  )}
</button>
```

#### Animation Classes
```tsx
<div className={`transition-all duration-300 ease-in-out ${
  kpiCollapsed 
    ? 'opacity-0 max-h-0 overflow-hidden transform -translate-y-2 pointer-events-none' 
    : 'opacity-100 max-h-full transform translate-y-0'
}`}>
```

### 📱 User Experience
- **Hide**: Cards fade out, collapse upward, and become non-interactive
- **Show**: Cards fade in, expand downward with smooth animation
- **Responsive**: Works consistently across all screen sizes
- **Accessible**: Clear visual indicators and hover states

### 🎯 Use Cases
Perfect for:
- **Client Screenshots**: Hide KPIs to focus on data tables
- **Presentations**: Cleaner interface for screen sharing
- **Custom Views**: Reduce visual clutter when needed
- **Mobile Optimization**: More screen real estate on smaller devices

### 🔄 Consistency with Existing Design
- Matches filter panel toggle behavior
- Uses same icons and animations as the rest of the interface
- Maintains HON brand styling and color scheme
- Follows established UX patterns

## Files Modified
- `frontend/src/pages/AdLevelDashboard.tsx`
- `frontend/src/pages/ModernDashboard.tsx`
- `frontend/src/pages/GoogleDashboard.tsx`
- `frontend/src/pages/TikTokDashboard.tsx`
- `frontend/src/pages/TikTokAdLevelDashboard.tsx`
- `frontend/src/components/MetricsCards.tsx` (enhanced with collapse functionality)
- `frontend/src/components/CollapsibleSection.tsx` (new utility component)

## Testing
✅ All dashboards maintain existing functionality
✅ Smooth animations work across all platforms
✅ TypeScript compilation passes
✅ Responsive design maintained
✅ Accessibility preserved

The feature is now ready for client use and will significantly improve the screenshot experience for HON's reporting presentations.