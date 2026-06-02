"""Ebbinghaus forgetting curve scheduler using SM-2 algorithm."""

import math
from datetime import datetime, timezone, timedelta
from typing import Any


class EbbinghausScheduler:
    """
    SM-2 based spaced repetition scheduler.

    Implements the SuperMemo SM-2 algorithm for scheduling reviews
    based on the Ebbinghaus forgetting curve theory.
    """

    def __init__(self, initial_ef: float = 2.5):
        """
        Initialize the scheduler.

        Args:
            initial_ef: Initial ease factor. Default is 2.5 (average difficulty).
        """
        self.initial_ef = initial_ef
        self.min_ef = 1.3
        self.max_ef = 3.0

    def calculate_next_review(
        self,
        repetitions: int,
        interval: int,
        quality: int,
        current_ef: float | None = None,
    ) -> dict[str, Any]:
        """
        Calculate the next review parameters using SM-2 algorithm.

        Args:
            repetitions: Number of consecutive successful reviews.
            interval: Current interval in days.
            quality: Review quality 0-5:
                0 - Complete blackout
                1 - Incorrect, but recognized answer
                2 - Incorrect, but answer seemed easy to recall
                3 - Correct with serious difficulty
                4 - Correct after hesitation
                5 - Perfect response
            current_ef: Current ease factor. Defaults to initial_ef.

        Returns:
            dict with new_interval, new_ef, new_repetitions, next_review_date,
            mastery_level
        """
        ef = current_ef or self.initial_ef
        quality = max(0, min(5, quality))  # clamp to 0-5

        # SM-2 EF formula:
        # EF = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(self.min_ef, min(self.max_ef, new_ef))

        if quality < 3:
            # Failed: reset repetitions and interval
            new_repetitions = 0
            new_interval = 1
            mastery_delta = -0.1  # slight decrease in mastery
        else:
            # Success
            new_repetitions = repetitions + 1
            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = round(interval * new_ef)

            # Mastery increases based on quality and consistency
            mastery_delta = 0.05 + (quality - 3) * 0.05

        # Calculate mastery level (0.0 - 1.0)
        mastery_level = min(1.0, max(0.0, self._calculate_mastery(new_repetitions, new_ef)))

        next_review_date = datetime.now(timezone.utc) + timedelta(days=new_interval)

        return {
            "new_interval": new_interval,
            "new_ef": round(new_ef, 2),
            "new_repetitions": new_repetitions,
            "next_review_date": next_review_date.isoformat(),
            "mastery_level": round(mastery_level, 3),
            "quality": quality,
            "previous_interval": interval,
        }

    def _calculate_mastery(self, repetitions: int, ef: float) -> float:
        """
        Calculate mastery level based on repetitions and ease factor.

        Uses a logistic growth model where mastery grows quickly with
        initial reviews and then asymptotes.
        """
        if repetitions == 0:
            return 0.0
        # S-curve: mastery = 1 - 1 / (1 + repetitions + EF)
        return 1.0 - 1.0 / (1.0 + repetitions + (ef - 1.3) * 0.5)

    def get_retention_strength(
        self,
        days_since_review: int,
        repetitions: int,
        interval: int,
        ef: float | None = None,
    ) -> float:
        """
        Calculate expected retention rate based on forgetting curve.

        Uses the Ebbinghaus forgetting curve model:
        R = e^(-t/S) where S = interval * ease_factor

        Args:
            days_since_review: Days elapsed since last review.
            repetitions: Number of successful reviews before this point.
            interval: The scheduled interval at last review.
            ef: Ease factor at last review.

        Returns:
            Retention rate between 0.0 and 1.0.
        """
        ef = ef or self.initial_ef
        stability = interval * ef  # stability parameter S

        if repetitions == 0 or stability == 0:
            # No learning yet - fast decay
            if days_since_review == 0:
                return 0.9  # just reviewed, still fresh
            return max(0.0, 0.9 * math.exp(-days_since_review / 1.0))

        # Ebbinghaus forgetting curve: R = e^(-t/S)
        retention = math.exp(-days_since_review / stability)
        return round(retention, 4)

    def get_forgetting_curve_points(
        self,
        current_interval: int,
        current_ef: float,
        repetitions: int,
        max_days: int = 60,
        num_points: int = 12,
    ) -> list[dict[str, Any]]:
        """
        Generate forgetting curve data points for visualization.

        Args:
            current_interval: Current review interval in days.
            current_ef: Current ease factor.
            repetitions: Number of successful reviews.
            max_days: Maximum days to project.
            num_points: Number of data points to generate.

        Returns:
            List of dicts with 'days', 'retention_rate', 'label'.
        """
        points = []
        step = max_days / num_points
        for i in range(num_points + 1):
            days = round(i * step, 1)
            retention = self.get_retention_strength(
                days, repetitions, current_interval, current_ef
            )
            label = self._retention_label(retention)
            points.append({"days": days, "retention_rate": retention, "label": label})
        return points

    def get_optimal_review_points(
        self,
        current_interval: int,
        current_ef: float,
        repetitions: int,
    ) -> list[dict[str, Any]]:
        """
        Generate optimal review timing points (before retention drops below threshold).

        Args:
            current_interval: Current review interval in days.
            current_ef: Current ease factor.
            repetitions: Number of successful reviews.

        Returns:
            List of dicts with 'days', 'retention_rate', 'label'.
        """
        stability = current_interval * current_ef
        # Review when retention would drop to ~85%
        optimal_days = [1, 6]
        if repetitions >= 3:
            optimal_days = [1, round(current_interval * 0.5), current_interval]
        if repetitions >= 5:
            optimal_days = [
                1,
                round(current_interval * 0.33),
                round(current_interval * 0.66),
                current_interval,
            ]

        return [
            {
                "days": days,
                "retention_rate": self.get_retention_strength(
                    days, repetitions, current_interval, current_ef
                ),
                "label": "Optimal review window",
            }
            for days in sorted(set(optimal_days))
            if days <= 90
        ]

    @staticmethod
    def _retention_label(retention: float) -> str:
        """Convert retention rate to human-readable label."""
        if retention >= 0.9:
            return "Fresh"
        elif retention >= 0.7:
            return "Good"
        elif retention >= 0.5:
            return "Fading"
        elif retention >= 0.3:
            return "Weak"
        else:
            return "Forgot"
