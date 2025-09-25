from pandas import to_numeric

class PlayerStats:
    def __init__(self, player_name, player_data_instance):
        self.player_name = player_name
        self.player_data_instance = player_data_instance

    def get_player_stats(self):
        """
        Retrieve stats for the given player.

        Returns:
        - A DataFrame with the player's stats if found.
        - None if the player is not found in the dataset.
        """
        player_data = self.player_data_instance.final_data[
            self.player_data_instance.final_data['Player'] == self.player_name
        ]
        if not player_data.empty:
            return player_data
        else:
            print(f"No data found for player: {self.player_name}.")
            return None

    def count_stat(self, column_name, multiplier):
        """
        Generalized method to calculate points for a given stat column.

        Parameters:
        - column_name: The column name for the stat.
        - multiplier: The multiplier for the stat.

        Returns:
        - Total points for the stat.
        """
        player_stats = self.get_player_stats()
        if player_stats is None:
            return 0

        try:
            stat_values = to_numeric(player_stats[column_name], errors='coerce')
            return stat_values.sum() * multiplier
        except KeyError:
            print(f"Column '{column_name}' not found in player data.")
            return 0

    def count_receptions(self, receptions_score):
        return self.count_stat('Rec', receptions_score)

    def count_sacks(self, sack_score):
        return self.count_stat('Sk', sack_score)

    def count_fumbles(self, fumble_score):
        return self.count_stat('Fmb', fumble_score)

    def count_interceptions(self, interception_score):
        return self.count_stat('Int', interception_score)

    def count_rushing_yards(self, rushing_yards_score):
        return self.count_stat('Rush Yards', rushing_yards_score)

    def count_passing_yards(self, passing_yards_score):
        return self.count_stat('Passing Yards', passing_yards_score)

    def count_receiving_yards(self, receiving_yards_score):
        return self.count_stat('Receiving Yards', receiving_yards_score)

    def count_td_passing(self, td_score_passing):
        return self.count_stat('Passing TD', td_score_passing)

    def count_receiving_td(self, receiving_score):
        return self.count_stat('Receiving TD', receiving_score)

    def count_rushing_td(self, rushing_score):
        return self.count_stat('TD', rushing_score)

    def count_2pt_conversions(self, pt_score):
        return self.count_stat('2pt Conversion', pt_score)

    def get_games_played(self):
        """
        Retrieve the number of games played by the player.

        Returns:
        - Number of games played if available, else 1 to avoid division by zero.
        """
        player_stats = self.get_player_stats()
        if player_stats is None:
            return 1

        for column in ['Games', 'Games_y', 'Games_x']:
            if column in player_stats.columns:
                games = to_numeric(player_stats[column], errors='coerce')
                if games.notna().any():
                    return games.iloc[0]
        return 1

    def calculate_Points(self, sack_score, receptions_score, fumble_score, interception_score,
                         rushing_yards_score, passing_yards_score, receiving_yards_score,
                         td_score_passing, td_receiving, td_rushing, conversion_score):
        """
        Calculate the total average points for the player based on multiple stats.
        """
        total_score = (
            self.count_sacks(sack_score) +
            self.count_receptions(receptions_score) +
            self.count_fumbles(fumble_score) +
            self.count_interceptions(interception_score) +
            self.count_rushing_yards(rushing_yards_score) +
            self.count_passing_yards(passing_yards_score) +
            self.count_receiving_yards(receiving_yards_score) +
            self.count_td_passing(td_score_passing) +
            self.count_receiving_td(td_receiving) +
            self.count_rushing_td(td_rushing) +
            self.count_2pt_conversions(conversion_score)
        )
        games_played = self.get_games_played()
        if games_played > 0:
            return total_score / games_played
        return 0

    @staticmethod
    def compare_players(*players, scoring_params=None):
        """
        Compare multiple players and return a summary of their average points.

        Parameters:
        - *players: PlayerStats instances to compare.
        - scoring_params: Optional dictionary of scoring parameters.

        Returns:
        - A summary string of the comparison.
        """
        if len(players) < 2:
            return "At least two players are required for comparison."

        # Default scoring parameters if none are provided
        default_scoring = {
            'sack_score': 0,
            'receptions_score': 1,
            'fumble_score': -2,
            'interception_score': -2,
            'rushing_yards_score': 0.1,
            'passing_yards_score': 0.04,
            'receiving_yards_score': 0.1,
            'td_score_passing': 4,
            'td_receiving': 6,
            'td_rushing': 6,
            'conversion_score': 2
        }
        scoring_params = scoring_params or default_scoring

        # Calculate scores for all players
        scores = {}
        for player in players:
            try:
                points = player.calculate_Points(
                    scoring_params['sack_score'],
                    scoring_params['receptions_score'],
                    scoring_params['fumble_score'],
                    scoring_params['interception_score'],
                    scoring_params['rushing_yards_score'],
                    scoring_params['passing_yards_score'],
                    scoring_params['receiving_yards_score'],
                    scoring_params['td_score_passing'],
                    scoring_params['td_receiving'],
                    scoring_params['td_rushing'],
                    scoring_params['conversion_score']
                )
                scores[player.player_name] = points
            except Exception as e:
                print(f"Error calculating points for {player.player_name}: {e}")
                scores[player.player_name] = None

        # Sort players by their scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1] if x[1] is not None else -float('inf'), reverse=True)

        # Generate the comparison result
        result = []
        for i in range(len(sorted_scores) - 1):
            player1, score1 = sorted_scores[i]
            player2, score2 = sorted_scores[i + 1]
            if score1 is None or score2 is None:
                result.append(f"Could not compare {player1} and {player2} due to missing data.")
                continue

            if score1 > score2:
                result.append(f"{player1} has a higher average than {player2} (Score: {score1:.2f} > {score2:.2f})")
            elif score1 < score2:
                result.append(f"{player1} has a lower average than {player2} (Score: {score1:.2f} < {score2:.2f})")
            else:
                result.append(f"{player1} and {player2} have equal scores (Score: {score1:.2f})")

        return "\n".join(result)

    @staticmethod
    def compare_player_groups(group1, group2, scoring_params=None):
        """
        Compare two groups of players and return the difference in total points.

        Parameters:
        - group1: List of PlayerStats instances (Team 1).
        - group2: List of PlayerStats instances (Team 2).
        - scoring_params: Optional dictionary of scoring parameters.

        Returns:
        - A string describing the point difference between the two groups.
        """
        # Default scoring parameters
        default_scoring = {
            'sack_score': 0,
            'receptions_score': 1,
            'fumble_score': -2,
            'interception_score': -2,
            'rushing_yards_score': 0.1,
            'passing_yards_score': 0.04,
            'receiving_yards_score': 0.1,
            'td_score_passing': 4,
            'td_receiving': 6,
            'td_rushing': 6,
            'conversion_score': 2
        }
        scoring_params = scoring_params or default_scoring

        def calculate_group_points(group):
            total_points = 0
            for player in group:
                try:
                    points = player.calculate_Points(
                        scoring_params['sack_score'],
                        scoring_params['receptions_score'],
                        scoring_params['fumble_score'],
                        scoring_params['interception_score'],
                        scoring_params['rushing_yards_score'],
                        scoring_params['passing_yards_score'],
                        scoring_params['receiving_yards_score'],
                        scoring_params['td_score_passing'],
                        scoring_params['td_receiving'],
                        scoring_params['td_rushing'],
                        scoring_params['conversion_score']
                    )
                    total_points += points
                except Exception as e:
                    print(f"Error calculating points for {player.player_name}: {e}")
            return total_points

        group1_points = calculate_group_points(group1)
        group2_points = calculate_group_points(group2)

        point_difference = group1_points - group2_points

        if point_difference > 0:
            return f"Team 1 leads Team 2 by {point_difference:.2f} points."
        elif point_difference < 0:
            return f"Team 2 leads Team 1 by {-point_difference:.2f} points."
        else:
            return "Both groups have the same total points."

    @staticmethod
    def calculate_points_with_starters(group1, starters1, group2, starters2, scoring_params=None):
        default_scoring = {
            'sack_score': 0,
            'receptions_score': 1,
            'fumble_score': -2,
            'interception_score': -2,
            'rushing_yards_score': 0.1,
            'passing_yards_score': 0.04,
            'receiving_yards_score': 0.1,
            'td_score_passing': 4,
            'td_receiving': 6,
            'td_rushing': 6,
            'conversion_score': 2
        }
        scoring_params = scoring_params or default_scoring
        def calculate_group_points(group, starters):
            total_points = 0
            for player in group:
                try:
                    points = player.calculate_Points(
                        scoring_params['sack_score'],
                        scoring_params['receptions_score'],
                        scoring_params['fumble_score'],
                        scoring_params['interception_score'],
                        scoring_params['rushing_yards_score'],
                        scoring_params['passing_yards_score'],
                        scoring_params['receiving_yards_score'],
                        scoring_params['td_score_passing'],
                        scoring_params['td_receiving'],
                        scoring_params['td_rushing'],
                        scoring_params['conversion_score']
                    )
                    # Check if the player is a starter
                    if player.player_name not in starters:
                        points /= 2  # Halve the points if not a starter
                        if points < 9:  # If non-starter points are less than 9, count as 0
                            points = 0
                    total_points += points
                except Exception as e:
                    print(f"Error calculating points for {player.player_name}: {e}")
            return total_points

        # Calculate points for both groups
        group1_points = calculate_group_points(group1, starters1)
        group2_points = calculate_group_points(group2, starters2)

        point_difference = group1_points - group2_points

        # Return the comparison results
        if point_difference > 0:
            return f"Group 1 leads Group 2 by {point_difference:.2f} points."
        elif point_difference < 0:
            return f"Group 2 leads Group 1 by {-point_difference:.2f} points."
        else:
            return "Both groups have the same total points."



