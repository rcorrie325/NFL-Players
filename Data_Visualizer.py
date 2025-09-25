import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, f_oneway
import sqlite3
import matplotlib.cm as cm
import seaborn as sns


class PlayerVisualizer:
    def __init__(self, player_data):
        """
        Constructor for the PlayerVisualizer class.

        Parameters:
        - player_data: Instance of PlayerData containing the final_data DataFrame.
        """
        self.data = player_data.final_data
        self.connection = sqlite3.connect(":memory:")
        self.data.to_sql("players", self.connection, index=False, if_exists="replace")
        self.clean_numeric_columns()

    def clean_numeric_columns(self):
        """
        Clean numeric columns in the dataset to remove formatting issues
        (e.g., commas) and convert to proper numeric types.
        """
        for col in self.data.columns:
            if self.data[col].dtype == "object":  # Only process object columns
                try:
                    # Remove commas and strip spaces
                    self.data[col] = self.data[col].apply(
                        lambda x: x.replace(",", "").strip() if isinstance(x, str) else x
                    )
                    # Convert to numeric
                    self.data[col] = pd.to_numeric(self.data[col], errors="coerce")
                except Exception as e:
                    print(f"Error cleaning column '{col}': {e}")

    def plot_stat_distribution(self, stat_column, title="Stat Distribution", bins=20):
        """
        Visualize the distribution of a specific stat across all players with a normality test
        and calculate basic statistics (mean, median, range).
        """
        query = f"SELECT `{stat_column}` FROM players WHERE `{stat_column}` IS NOT NULL"
        stat_data = pd.read_sql_query(query, self.connection)

        if stat_data.empty:
            print(f"No valid data found for column '{stat_column}'.")
            return

        # Ensure the data is numeric
        stat_data = pd.to_numeric(stat_data[stat_column], errors="coerce").dropna()

        print(f"Number of entries for '{stat_column}': {len(stat_data)}")

        # Calculate basic statistics
        mean_value = stat_data.mean()
        median_value = stat_data.median()
        range_value = stat_data.max() - stat_data.min()

        print(f"Basic Statistics for '{stat_column}':")
        print(f"Mean = {mean_value:.2f}")
        print(f"Median = {median_value:.2f}")
        print(f"Range = {range_value:.2f}")

        # Perform Shapiro-Wilk test for normality
        stat, p_value = shapiro(stat_data)
        print(f"Shapiro-Wilk Test for Normality:\n"
              f"Statistic = {stat:.4f}, p-value = {p_value:.4f}")
        if p_value > 0.05:
            print(f"The data in '{stat_column}' appears to follow a normal distribution (p > 0.05).")
        else:
            print(f"The data in '{stat_column}' does not follow a normal distribution (p <= 0.05).")

        # Plot the distribution
        plt.figure(figsize=(10, 6))
        plt.hist(stat_data, bins=bins, edgecolor="black")
        plt.title(title)
        plt.xlabel(stat_column)
        plt.ylabel("Frequency")
        plt.grid(alpha=0.5)
        plt.show()

    def compare_players_stat(self, stat_column, *players):
        """
        Compare a specific stat across multiple players using a bar chart, a legend, unique colors, and ANOVA test.

        Parameters:
        - stat_column: Column name of the stat to compare.
        - *players: Variable number of player names to compare.
        """
        placeholders = ", ".join(["?"] * len(players))
        query = f"""
        SELECT Player, `{stat_column}`
        FROM players
        WHERE Player IN ({placeholders})
        """
        player_stats = pd.read_sql_query(query, self.connection, params=players)

        if player_stats.empty:
            print(f"No data found for players: {', '.join(players)}.")
            return

        # Ensure the stat_column is numeric
        player_stats[stat_column] = pd.to_numeric(player_stats[stat_column], errors="coerce")

        # Drop rows with NaN or non-numeric values
        player_stats = player_stats.dropna(subset=[stat_column])

        if player_stats.empty:
            print(f"No valid numeric data found for column '{stat_column}' for the specified players.")
            return

        player_stats.set_index("Player", inplace=True)

        # Generate unique colors for each player
        cmap = cm.get_cmap("tab10", len(player_stats))
        colors = [cmap(i) for i in range(len(player_stats))]

        # Create bar chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(player_stats.index, player_stats[stat_column], color=colors, edgecolor="black")
        plt.title(f"{stat_column} Comparison for Selected Players")
        plt.ylabel(stat_column)
        plt.xlabel("Player")
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)

        # Add legend for player names
        plt.legend(bars, player_stats.index, title="Players", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        plt.show()

    def top_players_by_stat(self, stat_column, top_n=10):
        """
        Visualize the top N players by a specific stat with basic statistics, a legend, and unique colors.

        Parameters:
        - stat_column: Column name of the stat to visualize.
        - top_n: Number of top players to display (default is 10).
        """
        query = f"""
        SELECT Player, `{stat_column}`
        FROM players
        WHERE `{stat_column}` IS NOT NULL
        """
        top_players = pd.read_sql_query(query, self.connection)

        if top_players.empty:
            print(f"No valid data found for column '{stat_column}'.")
            return

        # Clean and convert the stat column to numeric
        top_players[stat_column] = (
            top_players[stat_column]
            .replace({',': ''}, regex=True)  # Remove commas for large numbers
            .astype(str)
            .str.strip()  # Strip spaces
        )
        top_players[stat_column] = pd.to_numeric(top_players[stat_column], errors='coerce')

        # Filter valid data and sort by the stat column
        top_players = top_players.dropna(subset=[stat_column])
        top_players = top_players[top_players[stat_column] > 0]
        top_players = top_players.sort_values(by=stat_column, ascending=False).head(top_n)

        if top_players.empty:
            print(f"No numeric data available for column '{stat_column}'.")
            return

        top_players.set_index("Player", inplace=True)

        # Generate unique colors for each bar
        cmap = cm.get_cmap("tab10", len(top_players))
        colors = [cmap(i) for i in range(len(top_players))]

        # Plot the bar chart
        plt.figure(figsize=(12, 8))
        bars = plt.bar(top_players.index, top_players[stat_column], color=colors, edgecolor="black")
        plt.title(f"Top {top_n} Players by {stat_column}")
        plt.ylabel(stat_column)
        plt.xlabel("Player")
        plt.xticks(rotation=45, ha="right")
        plt.grid(alpha=0.3)

        # Calculate basic statistics
        mean_stat = top_players[stat_column].mean()
        median_stat = top_players[stat_column].median()
        print(f"Basic Statistics for Top {top_n} Players in '{stat_column}':\n"
              f"Mean = {mean_stat:.4f}, Median = {median_stat:.4f}")

        # Add legend for player names
        plt.legend(bars, top_players.index, title="Players", bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()
        plt.show()

    def plot_stat_heatmap(self, stat_column, group_column, title="Stat Heatmap"):
        query = f"""
        SELECT `{group_column}`, `{stat_column}`
        FROM players
        WHERE `{stat_column}` IS NOT NULL AND `{group_column}` IS NOT NULL
        """
        data = pd.read_sql_query(query, self.connection)

        if data.empty:
            print(f"No valid data found for column '{stat_column}' grouped by '{group_column}'.")
            return

        # Ensure the stat column is numeric
        data[stat_column] = pd.to_numeric(data[stat_column], errors="coerce")
        data = data.dropna(subset=[stat_column])

        if data.empty:
            print(f"No valid numeric data available for '{stat_column}'.")
            return
        heatmap_data = data.groupby(group_column)[stat_column].mean().reset_index()
        heatmap_data = heatmap_data.pivot_table(index=group_column, values=stat_column)
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="coolwarm", linewidths=0.5)
        plt.title(title)
        plt.ylabel(group_column)
        plt.show()






