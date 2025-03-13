# Career Dashboard

A comprehensive Streamlit application with two main tools:

1. **Salary Projection Tool**: Visualize and project salary data based on job levels and penetration rates
2. **Professional Achievements Dashboard**: Track, visualize, and summarize your professional accomplishments

## Overview

This dashboard helps professionals understand their career progression in two key dimensions:

### Salary Projection Tool

- Understand your compensation in the context of standard salary ranges
- Project future earnings based on historical trends
- Analyze your salary penetration rate within your job level

### Achievements Dashboard

- Document and track professional achievements with rich metadata
- Visualize achievement trends and categories
- Generate summaries of your professional impact

## Features

### Salary Projection Tool

- **Salary Range Visualization**: Compare your actual salary against minimum, maximum, and median values
- **Penetration Rate Analysis**: Understand your position within the salary range
- **Future Projections**: See expected salary growth for upcoming years based on current trends
- **Detailed Data Tables**: View comprehensive data on historical and projected salaries

### Achievements Dashboard

- **Achievement Tracking**: Store achievements as markdown files with YAML metadata
- **Visual Analytics**: Trend charts, category breakdown, and impact leaderboard
- **Filtering**: Filter achievements by category, tags, and date range
- **Auto-Generated Summaries**: Get concise summaries of your professional impact

## Installation

1. **Prerequisites**:

   - Python 3.8 or higher
   - Git

2. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/salary-box.git
   cd salary-box
   ```

3. **Create a virtual environment** (optional but recommended):

   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:

   ```bash
   streamlit run src/main.py
   ```

2. **Switch between dashboards**:
   - Use the "Select Dashboard" radio buttons in the sidebar to switch between the Salary Comparison and Professional Achievements dashboards

### Salary Projection Tool

1. **Select your job level** from the dropdown in the sidebar
2. **Enter your actual salary** for each available year
3. **View the visualizations** to understand:
   - How your salary compares to the range for your level
   - Your penetration rate within the salary range
   - Projected future earnings based on historical trends

### Achievements Dashboard

1. **Add achievements** as markdown files in the `src/achievements/` directory:

   - Use the naming format: `YYYY-MM-DD-title.md`
   - Include YAML front matter with metadata (see example below)
   - Write your achievement details in markdown format

2. **Filter and analyze** your achievements:

   - Use sidebar filters to focus on specific categories, tags, or dates
   - View trend charts showing your achievement frequency
   - See category breakdown and impact leaderboards

3. **View auto-generated summaries** of your professional impact

## Data Sources and Formats

### Salary Data

The application uses CSV files for salary range data:

- `src/salary_2023.csv`: Salary range data for 2023
- `src/salary_2024.csv`: Salary range data for 2024
- `src/salary_2025.csv`: Salary range data for 2025

### Achievement Data

Achievements are stored as markdown files with YAML front matter:

```markdown
---
title: 'Optimized API Performance'
date: '2024-03-01'
category: 'Technical Impact'
tags: ['performance', 'latency', 'backend']
metrics:
  - key: 'Latency Reduction'
    value: '40%'
  - key: 'Throughput Increase'
    value: '2x'
impact:
  - 'Decreased latency from 500ms to 300ms'
  - 'Improved system throughput by 2x'
summary: 'By optimizing database queries, I significantly improved API performance, reducing response time by 40% and increasing throughput.'
---

# Optimizing API Performance

One of my biggest wins this quarter was improving the API response time,
which had been a major bottleneck. By optimizing database queries and
implementing caching, I achieved:

- 40% lower latency
- 2x increase in throughput

This improvement led to faster end-user interactions and a smoother
experience for our customers.
```

## Calculation Methodology

### Salary Penetration Rate

Your position within the salary range, calculated as:

```
RP = (Salary - Range Minimum) / (Range Maximum - Range Minimum)
```

This value indicates where you stand in your salary band:

- **0-33%**: Lower third of the range (new to role)
- **33-66%**: Middle of the range (fully competent)
- **66-100%**: Upper third of the range (highly experienced)
- **>100%**: Above the typical range (exceptional performance)

### Future Salary Projections

Based on historical growth rates of salary ranges and your consistent penetration rate.

## Customization

### Adding New Salary Data

The system automatically detects all available salary data files. To add data for a new year:

1. Create a new CSV file named `src/salary_YYYY.csv` (replace YYYY with the year)
2. Follow one of these formats:
   - **Format A (2023/2024 style)**: Include columns for Level, Minimum, Maximum, Lower_Mid_Zone, Upper_Mid_Zone
   - **Format B (2025+ style)**: Include columns for Level, Lower_Min, Middle_Min, Middle_Max, Upper_Max

The dashboard will automatically detect the new file and include it in the visualizations without requiring code changes. You can add data for multiple years - past, present, or future - and the system will handle them appropriately.

### Adding New Achievements

Create new markdown files in the `src/achievements/` directory following the format shown above.

## Development

Built with:

- Streamlit for the web interface
- Pandas for data manipulation
- Matplotlib for visualizations
- PyYAML for parsing YAML metadata

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
