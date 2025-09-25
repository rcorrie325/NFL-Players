# NFL-Players Fantasy Comparison Tool

This project is an interactive toolkit I built for the 2024 NFL season to help fantasy football managers compare players, explore their statistics, and surface insights that can guide weekly lineup decisions. While the data files currently reflect the 2024 season, the workflow can be refreshed with new data each year to keep the analysis up to date.

## What the tool offers

- **Player comparison:** Quickly contrast multiple players across common fantasy metrics—such as rushing/receiving production, efficiency rates, and scoring totals—to identify potential starters, sleepers, or trade targets.
- **Statistical analysis:** Combine raw numbers with calculated metrics to spot trends over time, evaluate consistency, and understand how players perform in different situations (home/away splits, recent form, etc.).
- **Visualizations:** Generate charts that highlight performance trajectories and matchup-based projections so you can digest data at a glance.

## How it works

The project is organized into Python modules that load season data, compute summary statistics, and render visual dashboards. By running the scripts in sequence you can:

1. Import player data from the season data files.
2. Calculate fantasy-relevant statistics (e.g., weekly averages, totals, and efficiency metrics).
3. Display tables and visual comparisons that help you evaluate players head-to-head.

You can adapt the scripts to focus on specific positions, leagues, or scoring rules, and extend the analysis with additional metrics as needed.

## Updating for a new season

Refreshing the project for a new NFL season is straightforward:

1. Replace the existing data files with the latest season statistics.
2. Adjust any season-specific constants (such as week ranges or column names).
3. Re-run the analysis scripts to produce updated comparisons and visualizations.

Because the data pipeline and visualization templates are already in place, only a few tweaks are required each year to keep the tool current.

## Getting started

1. Clone this repository and install the required Python libraries listed in your environment or requirements file.
2. Run the data processing and visualization scripts (e.g., `Player_data.py`, `Player_Stats.py`, and `Data_Visualizer.py`).
3. Review the generated tables and charts to inform your fantasy roster decisions.

Whether you are preparing for drafts, managing waiver wire targets, or setting weekly lineups, this tool provides a solid foundation for data-driven fantasy football strategy.
