"""Rastreio da bola e detecao de quiques (bounce)."""

from __future__ import annotations

from typing import Optional, List, Tuple

import numpy as np


class BallTracker:
    """Rastreia a bola entre frames e detecta quiques com base na trajetoria."""

    def __init__(self, max_distance: float = 80.0, bounce_velocity_threshold: float = 3.0) -> None:
        self.max_distance = max_distance
        self.bounce_velocity_threshold = bounce_velocity_threshold
        self.positions: List[Tuple[int, int]] = []
        self.velocities: List[Tuple[float, float]] = []
        self.last_position: Optional[Tuple[int, int]] = None
        self.bounce_count = 0

    def update(self, position: Optional[Tuple[int, int]]) -> Optional[bool]:
        """Atualiza o rastreador com a nova posicao detectada.

        Returns:
            True se um quique foi detectado, False se nao, None se sem dados suficientes.
        """
        if position is None:
            self.last_position = None
            return None

        if self.last_position is not None:
            dx = position[0] - self.last_position[0]
            dy = position[1] - self.last_position[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist <= self.max_distance:
                self.positions.append(position)
                self.velocities.append((dx, dy))
                self.last_position = position

                # Detecta quique: mudanca brusca de direcao vertical (para cima depois de para baixo)
                if len(self.velocities) >= 2:
                    prev_vy = self.velocities[-2][1]
                    curr_vy = self.velocities[-1][1]
                    # Vy positivo = indo para baixo (no OpenCV y cresce para baixo)
                    # Quiche: estava descendo (vy > 0) e comecou a subir (vy < 0)
                    if prev_vy > self.bounce_velocity_threshold and curr_vy < -self.bounce_velocity_threshold:
                        self.bounce_count += 1
                        return True
                return False
            else:
                # Perdeu o rastreio, reseta
                self.last_position = position
                self.positions = [position]
                self.velocities = []
                return None
        else:
            self.positions = [position]
            self.velocities = []
            self.last_position = position
            return None

    def get_positions(self) -> List[Tuple[int, int]]:
        return self.positions.copy()

    def reset(self) -> None:
        self.positions = []
        self.velocities = []
        self.last_position = None
        self.bounce_count = 0
