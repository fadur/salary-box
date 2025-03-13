# CLAUDE.md - Guidelines for this codebase

## Build & Test Commands
- Install dependencies: `pip install -r requirements.txt`
- Run Streamlit app: `streamlit run src/main.py`
- Development mode: `streamlit run src/main.py --server.runOnSave=true`
- Deploy: `streamlit share src/main.py` (requires Streamlit account)

## Code Style Guidelines
- **Formatting**: Use Black for auto-formatting (`pip install black`, then `black src/*.py`)
- **Imports**: Group imports (standard library, third-party, local) with a blank line between groups
- **Line Length**: Max 88 characters per line
- **Naming**: 
  - snake_case for variables and functions
  - CamelCase for classes
- **Comments**: Add meaningful comments for complex code sections
- **Type Hints**: Use Python type hints where appropriate
- **Error Handling**: Use explicit try/except blocks with specific exceptions
- **Data Visualization**: Use matplotlib for visualization within Streamlit
- **Streamlit UI**: Keep UI elements organized with clear section headers

## Project Purpose
This is a salary visualization tool using Streamlit that compares actual vs. adjusted salaries across years (2024-2025), 
calculating penetration rates based on job levels from CSV data files. It helps users understand their salary positioning
within standard ranges for their job level.