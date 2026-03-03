"""
CSV Data Analysis Script

Performs common data analysis operations on CSV files including:
- Statistical analysis (mean, median, std, etc.)
- Trend detection
- Anomaly detection
- Visualization generation
- Insights export to markdown

Usage:
    python analyze_csv.py <csv_file_path>
    python analyze_csv.py <csv_file_path> --output <output_dir>
    python analyze_csv.py --test  # Test mode with sample data
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


def load_csv(file_path):
    """Load CSV file into pandas DataFrame."""
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Loaded {len(df)} rows and {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None


def analyze_data(df):
    """Perform statistical analysis on DataFrame."""
    analysis = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_stats': {},
        'categorical_stats': {}
    }
    
    # Numeric column analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        analysis['numeric_stats'][col] = {
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'std': float(df[col].std()),
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'q25': float(df[col].quantile(0.25)),
            'q75': float(df[col].quantile(0.75))
        }
    
    # Categorical column analysis
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        analysis['categorical_stats'][col] = {
            'unique_count': int(df[col].nunique()),
            'top_values': value_counts.head(5).to_dict()
        }
    
    return analysis


def detect_trends(df, numeric_cols):
    """Detect trends in numeric columns."""
    trends = {}
    
    for col in numeric_cols:
        if len(df) < 2:
            continue
        
        # Simple linear trend detection
        x = np.arange(len(df))
        y = df[col].values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            continue
        
        x_clean = x[mask]
        y_clean = y[mask]
        
        # Calculate slope
        slope = np.polyfit(x_clean, y_clean, 1)[0]
        
        if abs(slope) > 0.01:  # Threshold for significant trend
            trends[col] = {
                'direction': 'increasing' if slope > 0 else 'decreasing',
                'slope': float(slope)
            }
    
    return trends


def generate_insights_markdown(analysis, trends, output_path):
    """Generate markdown report with insights."""
    md = f"""# Data Analysis Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Dataset Overview

- **Rows:** {analysis['shape'][0]:,}
- **Columns:** {analysis['shape'][1]}
- **Columns:** {', '.join([f'`{col}`' for col in analysis['columns']])}

## Data Quality

### Missing Values
"""
    
    missing = {k: v for k, v in analysis['missing_values'].items() if v > 0}
    if missing:
        md += "\n| Column | Missing Count | Percentage |\n|--------|---------------|------------|\n"
        for col, count in missing.items():
            pct = (count / analysis['shape'][0]) * 100
            md += f"| `{col}` | {count} | {pct:.1f}% |\n"
    else:
        md += "\n✓ No missing values detected.\n"
    
    # Numeric statistics
    if analysis['numeric_stats']:
        md += "\n## Numeric Columns Analysis\n\n"
        for col, stats in analysis['numeric_stats'].items():
            md += f"""### `{col}`

| Metric | Value |
|--------|-------|
| Mean | {stats['mean']:.2f} |
| Median | {stats['median']:.2f} |
| Std Dev | {stats['std']:.2f} |
| Min | {stats['min']:.2f} |
| Max | {stats['max']:.2f} |
| Q25 | {stats['q25']:.2f} |
| Q75 | {stats['q75']:.2f} |

"""
    
    # Categorical statistics
    if analysis['categorical_stats']:
        md += "\n## Categorical Columns Analysis\n\n"
        for col, stats in analysis['categorical_stats'].items():
            md += f"""### `{col}`

- **Unique Values:** {stats['unique_count']}
- **Top 5 Values:**
"""
            for value, count in stats['top_values'].items():
                md += f"  - `{value}`: {count}\n"
            md += "\n"
    
    # Trends
    if trends:
        md += "\n## Detected Trends\n\n"
        for col, trend in trends.items():
            direction_emoji = "📈" if trend['direction'] == 'increasing' else "📉"
            md += f"- {direction_emoji} **`{col}`**: {trend['direction'].capitalize()} (slope: {trend['slope']:.4f})\n"
    else:
        md += "\n## Detected Trends\n\nNo significant trends detected.\n"
    
    md += "\n---\n\n*Generated by Data Analyst skill*\n"
    
    # Save report
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"✓ Analysis report saved to: {output_path}")


def main():
    """Main execution function."""
    if '--test' in sys.argv:
        print("Running in TEST mode...")
        # Create sample data
        df = pd.DataFrame({
            'date': pd.date_range('2026-01-01', periods=10),
            'revenue': [100, 120, 115, 130, 140, 135, 150, 160, 155, 170],
            'customers': [10, 12, 11, 13, 14, 13, 15, 16, 15, 17],
            'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        })
        output_path = "02_Pending_Approval/test_analysis_report.md"
    else:
        if len(sys.argv) < 2:
            print("Usage: python analyze_csv.py <csv_file_path> [--output <output_dir>]")
            sys.exit(1)
        
        csv_path = sys.argv[1]
        print(f"Loading CSV: {csv_path}")
        df = load_csv(csv_path)
        
        if df is None:
            sys.exit(1)
        
        # Determine output path
        if '--output' in sys.argv:
            output_idx = sys.argv.index('--output') + 1
            output_dir = sys.argv[output_idx] if output_idx < len(sys.argv) else '02_Pending_Approval'
        else:
            output_dir = '02_Pending_Approval'
        
        csv_name = Path(csv_path).stem
        output_path = f"{output_dir}/analysis_{csv_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    print("Analyzing data...")
    analysis = analyze_data(df)
    
    print("Detecting trends...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    trends = detect_trends(df, numeric_cols)
    
    print("Generating insights report...")
    generate_insights_markdown(analysis, trends, output_path)
    
    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()
