# Salary Projection Tool

A Streamlit application for visualizing and projecting salary data based on job levels and penetration rates.

## Overview

This tool helps users understand their compensation in the context of standard salary ranges and project future earnings. It allows users to:

- Select their job level
- Input their actual salary for different years
- Visualize how their salary compares to standard ranges
- Project expected future earnings based on historical trends

## Features

- **Salary Range Visualization**: Compare your actual salary against minimum, maximum, and median values for your job level
- **Penetration Rate Analysis**: Understand your position within the salary range
- **Future Projections**: See expected salary growth for upcoming years based on current trends
- **Detailed Data Tables**: View comprehensive data on historical and projected salaries

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run src/main.py
```

2. In the sidebar:
   - Select your job level
   - Enter your actual salary for each year

3. View the visualizations and data tables to understand your salary positioning and projections

## Data Sources

The application uses the following CSV files for salary range data:
- `src/salary_2023.csv`: Salary range data for 2023
- `src/salary_2024.csv`: Salary range data for 2024
- `src/salary_2025.csv`: Salary range data for 2025

## Calculation Methodology

- **Penetration Rate**: Your position within the salary range, calculated as:
  ```
  (actual_salary - minimum) / (maximum - minimum)
  ```
- **Future Projections**: Based on historical growth rates of salary ranges and your consistent penetration rate

## Development

- Built with Streamlit, Pandas, Matplotlib, and NumPy
- Add additional years by creating new CSV files with the appropriate format

## License

[Specify your license information here]