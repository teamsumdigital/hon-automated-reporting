#!/usr/bin/env python3
"""
Add KPI collapse functionality to remaining dashboards
"""

import os
import re

# Dashboard files to update (excluding AdLevelDashboard.tsx and ModernDashboard.tsx as they're already done)
dashboard_files = [
    'GoogleDashboard.tsx',
    'TikTokDashboard.tsx', 
    'TikTokAdLevelDashboard.tsx'
]

frontend_path = '/Users/joeymuller/Documents/coding-projects/active-projects/hon-automated-reporting/frontend/src/pages'

def add_kpi_collapse_to_dashboard(file_path):
    """Add KPI collapse functionality to a dashboard file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if already has kpiCollapsed state
    if 'kpiCollapsed' in content:
        print(f"  ✅ {os.path.basename(file_path)} already has KPI collapse functionality")
        return
    
    print(f"  🔧 Adding KPI collapse to {os.path.basename(file_path)}")
    
    # 1. Add kpiCollapsed state after filterPanelOpen
    filter_panel_pattern = r'(\s+const \[filterPanelOpen, setFilterPanelOpen\] = useState\(true\);)'
    replacement = r'\1\n  const [kpiCollapsed, setKpiCollapsed] = useState(false);'
    content = re.sub(filter_panel_pattern, replacement, content)
    
    # 2. Find KPI Cards section and wrap with collapse functionality
    # Look for the KPI cards grid pattern
    kpi_pattern = r'(\s+)(.*KPI Cards.*\n\s+<div className=.*grid.*grid-cols.*gap.*mb.*)(.*?)(</div>)'
    
    def replace_kpi_section(match):
        indent = match.group(1)
        comment = match.group(2)
        content_between = match.group(3)
        closing_div = match.group(4)
        
        new_section = f"""{indent}/* Collapsible KPI Dashboard */
{indent}<div className="mb-8">
{indent}  {{/* Toggle Header */}}
{indent}  <div className="flex items-center justify-between mb-4">
{indent}    <h2 className="text-lg font-semibold text-gray-900">Performance Overview</h2>
{indent}    <button
{indent}      onClick={{() => setKpiCollapsed(!kpiCollapsed)}}
{indent}      className="flex items-center space-x-1 px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200"
{indent}    >
{indent}      <span>{{kpiCollapsed ? 'Show' : 'Hide'}}</span>
{indent}      {{kpiCollapsed ? (
{indent}        <ChevronRightIcon className="w-4 h-4" />
{indent}      ) : (
{indent}        <ChevronDownIcon className="w-4 h-4" />
{indent}      )}}
{indent}    </button>
{indent}  </div>
{indent}  
{indent}  {{/* KPI Cards */}}
{indent}  <div className={{`transition-all duration-300 ease-in-out ${{
{indent}    kpiCollapsed 
{indent}      ? 'opacity-0 max-h-0 overflow-hidden transform -translate-y-2 pointer-events-none' 
{indent}      : 'opacity-100 max-h-full transform translate-y-0'
{indent}  }}`}}>
{indent}    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">{content_between}    </div>
{indent}  </div>
{indent}</div>"""
        return new_section
    
    # Apply the replacement
    content = re.sub(kpi_pattern, replace_kpi_section, content, flags=re.DOTALL)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"  ✅ Successfully updated {os.path.basename(file_path)}")

def main():
    print("🚀 Adding KPI collapse functionality to remaining dashboards...\n")
    
    for dashboard_file in dashboard_files:
        file_path = os.path.join(frontend_path, dashboard_file)
        
        if os.path.exists(file_path):
            add_kpi_collapse_to_dashboard(file_path)
        else:
            print(f"  ⚠️ File not found: {dashboard_file}")
    
    print("\n✅ KPI collapse functionality added to all remaining dashboards!")

if __name__ == "__main__":
    main()