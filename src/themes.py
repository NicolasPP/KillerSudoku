from typing import NamedTuple

import pygame

from puzzle_store import PuzzleDifficulty


class GameTheme(NamedTuple):
    foreground_primary: pygame.color.Color
    foreground_secondary: pygame.color.Color
    background_primary: pygame.color.Color
    background_secondary: pygame.color.Color


class DifficultyThemes:
    themes: dict[PuzzleDifficulty, GameTheme] = {
        PuzzleDifficulty.EASY: GameTheme(
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(255, 255, 255),
            pygame.color.Color(255, 255, 255),
        ),
        PuzzleDifficulty.NORMAL: GameTheme(
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(255, 255, 255),
            pygame.color.Color(255, 255, 255),
        ),
        PuzzleDifficulty.HARD: GameTheme(
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(255, 255, 255),
            pygame.color.Color(255, 255, 255),
        ),
        PuzzleDifficulty.EXPERT: GameTheme(
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(255, 255, 255),
            pygame.color.Color(255, 255, 255),
        ),
        PuzzleDifficulty.MASTER: GameTheme(
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(0, 0, 0),
            pygame.color.Color(255, 255, 255),
            pygame.color.Color(255, 255, 255),
        )
    }
