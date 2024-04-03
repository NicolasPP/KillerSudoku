from __future__ import annotations

from typing import NamedTuple

from pygame.color import Color

from puzzle_store import PuzzleDifficulty


class GameTheme(NamedTuple):
    @staticmethod
    def default() -> GameTheme:
        return GameTheme(
            Color(0, 0, 0),
            Color(0, 0, 0),
            Color(255, 255, 255),
            Color(255, 255, 255),
        )

    foreground_primary: Color
    foreground_secondary: Color
    background_primary: Color
    background_secondary: Color


class DifficultyThemes:

    themes: dict[PuzzleDifficulty, GameTheme] = {
        PuzzleDifficulty.EASY: GameTheme(
            Color(255, 255, 255),
            Color(255, 255, 255),
            Color(0, 0, 0),
            Color(0, 0, 0),
        ),
        PuzzleDifficulty.NORMAL: GameTheme(
            Color(0, 0, 0),
            Color(0, 0, 0),
            Color(255, 255, 255),
            Color(255, 255, 255),
        ),
        PuzzleDifficulty.HARD: GameTheme(
            Color(0, 0, 0),
            Color(0, 0, 0),
            Color(255, 255, 255),
            Color(255, 255, 255),
        ),
        PuzzleDifficulty.EXPERT: GameTheme(
            Color(0, 0, 0),
            Color(0, 0, 0),
            Color(255, 255, 255),
            Color(255, 255, 255),
        ),
        PuzzleDifficulty.MASTER: GameTheme(
            Color(0, 0, 0),
            Color(0, 0, 0),
            Color(255, 255, 255),
            Color(255, 255, 255),
        )
    }
