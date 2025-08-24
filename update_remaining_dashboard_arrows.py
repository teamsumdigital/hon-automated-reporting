#!/usr/bin/env python3
"""
Update remaining dashboards with new arrow pattern
"""

import os
import re

# Files to update
files_to_update = [
    '/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/frontend/src/pages/GoogleDashboard.tsx',
    '/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/frontend/src/pages/TikTokDashboard.tsx',
    '/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/frontend/src/pages/TikTokAdLevelDashboard.tsx'
]

def update_dashboard_file(file_path):
    """Update a dashboard file with the new arrow pattern"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    filename = os.path.basename(file_path)
    print(f"Updating {filename}...")
    
    # 1. Add ChevronUpIcon import if not present
    if 'ChevronUpIcon' not in content:
        content = content.replace(
            'ArrowDownIcon\n} from \'@heroicons/react/24/outline\';',
            'ArrowDownIcon,\n  ChevronUpIcon\n} from \'@heroicons/react/24/outline\';'
        )
    
    # 2. Update the toggle section pattern
    # Look for the current pattern and replace it
    old_pattern = r'(\s+){/\* Toggle Button \*/}\s*<div className="flex justify-end mb-4">\s*<button[^>]+onClick=\{[^}]+\}[^>]+>\s*\{kpiCollapsed \? \(\s*<ChevronRightIcon className="w-5 h-5" />\s*\) : \(\s*<ChevronDownIcon className="w-5 h-5" />\s*\)\}\s*</button>\s*</div>'
    
    # For TikTok Ad Level (different structure)
    if 'TikTokAdLevel' in filename:
        # Different replacement for TikTok Ad Level
        old_pattern_tiktok = r'(\s+){/\* Toggle Button \*/}\s*<div className="flex justify-end mb-4">\s*<button[^>]+onClick=\{[^}]+\}[^>]+>\s*\{kpiCollapsed \? \(\s*<ChevronRightIcon className="w-5 h-5" />\s*\) : \(\s*<ChevronDownIcon className="w-5 h-5" />\s*\)\}\s*</button>\s*</div>'
        
        new_pattern_tiktok = r'''\1{/* Toggle Button - Below KPI Cards */}
\1<div className="flex justify-center">
\1  <button
\1    onClick={() => setKpiCollapsed(!kpiCollapsed)}
\1    className="p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200"
\1  >
\1    {kpiCollapsed ? (
\1      <ChevronDownIcon className="w-5 h-5" />
\1    ) : (
\1      <ChevronUpIcon className="w-5 h-5" />
\1    )}
\1  </button>
\1</div>'''
        
        content = re.sub(old_pattern_tiktok, new_pattern_tiktok, content, flags=re.DOTALL)
        
        # Also need to move this section after the KPI cards for TikTok Ad Level
        # This is more complex, so let's handle it manually for this file
        
    else:
        # For Google and TikTok dashboards
        new_pattern = r'''\1{/* Toggle Button - Below KPI Cards */}
\1<div className="flex justify-center">
\1  <button
\1    onClick={() => setKpiCollapsed(!kpiCollapsed)}
\1    className="p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200"
\1  >
\1    {kpiCollapsed ? (
\1      <ChevronDownIcon className="w-5 h-5" />
\1    ) : (
\1      <ChevronUpIcon className="w-5 h-5" />
\1    )}
\1  </button>
\1</div>'''
        
        content = re.sub(old_pattern, new_pattern, content, flags=re.DOTALL)
    
    # 3. Reduce margin from mb-8 to mb-6
    content = content.replace('mb-8">', 'mb-6">')
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {filename}")

# Run updates
for file_path in files_to_update:
    if os.path.exists(file_path):
        update_dashboard_file(file_path)
    else:
        print(f"⚠️ File not found: {file_path}")

print("\n✅ All dashboard files updated!")