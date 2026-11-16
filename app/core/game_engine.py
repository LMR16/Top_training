from app.core.homography import HomographyManager


class GameEngine:
    """
    Motor de regras do Top Training:
      - Níveis:
        * 'basico': 2 zonas (2 colunas: Esquerda, Direita)
        * 'medio': 3 zonas (3 colunas: Esquerda, Centro, Direita)
        * 'avancado': 6 zonas (Grade 3x2: 3 colunas x 2 profundidades separadas pela linha de saque)
      - Pontuação:
        * Quique dentro da zona-foco: +10 pontos (Acerto)
        * Quique dentro da área calibrada, mas fora da zona-foco: -5 pontos (Erro, mínimo 0)
        * Quique fora da área calibrada: estritamente ignorado
      - Filtro de 1º quique:
        * Bloqueia quiques secundários da mesma bola após o 1º impacto válido na quadra.
    """

    HIT_POINTS = 10
    MISS_PENALTY = 5
    FIRST_BOUNCE_COOLDOWN_SEC = 1.8

    def __init__(self, homography: HomographyManager):
        self.homography = homography

    def get_zones(self, level: str) -> list:
        W = self.homography.width_m
        L = self.homography.length_m
        S = self.homography.service_line_y

        level = (level or "basico").lower()
        zones = []

        if level == "basico":
            zones = [
                {"id": 0, "name": "Esquerda (Cruzada)", "x1": 0.0, "y1": 0.0, "x2": round(W / 2, 3), "y2": L},
                {"id": 1, "name": "Direita (Paralela)", "x1": round(W / 2, 3), "y1": 0.0, "x2": W, "y2": L},
            ]
        elif level == "medio":
            w3 = W / 3.0
            zones = [
                {"id": 0, "name": "Coluna Esquerda", "x1": 0.0, "y1": 0.0, "x2": round(w3, 3), "y2": L},
                {"id": 1, "name": "Coluna Central", "x1": round(w3, 3), "y1": 0.0, "x2": round(2 * w3, 3), "y2": L},
                {"id": 2, "name": "Coluna Direita", "x1": round(2 * w3, 3), "y1": 0.0, "x2": W, "y2": L},
            ]
        else:  # avancado (grade 3x2)
            w3 = W / 3.0
            zones = [
                {"id": 0, "name": "Funda Esquerda", "x1": 0.0, "y1": 0.0, "x2": round(w3, 3), "y2": S},
                {"id": 1, "name": "Funda Centro", "x1": round(w3, 3), "y1": 0.0, "x2": round(2 * w3, 3), "y2": S},
                {"id": 2, "name": "Funda Direita", "x1": round(2 * w3, 3), "y1": 0.0, "x2": W, "y2": S},
                {"id": 3, "name": "Curta Esquerda (Saque)", "x1": 0.0, "y1": S, "x2": round(w3, 3), "y2": L},
                {"id": 4, "name": "Curta Centro (Saque)", "x1": round(w3, 3), "y1": S, "x2": round(2 * w3, 3), "y2": L},
                {"id": 5, "name": "Curta Direita (Saque)", "x1": round(2 * w3, 3), "y1": S, "x2": W, "y2": L},
            ]
        return zones

    def find_zone_for_point(self, xm: float, ym: float, level: str) -> int:
        zones = self.get_zones(level)
        xc = min(max(xm, 0.0), self.homography.width_m)
        yc = min(max(ym, 0.0), self.homography.length_m)
        for z in zones:
            if z["x1"] <= xc <= z["x2"] and z["y1"] <= yc <= z["y2"]:
                return z["id"]
        return -1

    def evaluate_bounces(
        self,
        raw_bounces: list,
        fps: float,
        level: str,
        target_zone: int,
        is_video_mode: bool = False
    ) -> dict:
        """
        Filtra estritamente os quiques dentro do polígono calibrado de 4 pontos,
        aplica cooldown de 1º quique e avalia acerto/erro por zona.
        """
        fps = fps or 30.0
        score = 0
        hits = 0
        misses = 0
        evaluated_events = []
        last_valid_time = -999.0
        cooldown = 0.95 if is_video_mode else self.FIRST_BOUNCE_COOLDOWN_SEC

        zones = self.get_zones(level)
        zone_counts = {
            z["id"]: {"id": z["id"], "name": z["name"], "hits": 0, "misses": 0, "total": 0}
            for z in zones
        }

        for b in raw_bounces:
            frame_idx = int(b["frame"])
            time_sec = frame_idx / fps
            u, v = float(b["x"]), float(b["y"])

            xm, ym, inside = self.homography.pixel_to_meters(u, v)

            # Regra estrita: qualquer quique fora do polígono de 4 pontos calibrado é ignorado
            if not inside:
                continue

            # Filtro de 1º quique: ignora quiques secundários muito próximos da mesma bola
            if (time_sec - last_valid_time) < cooldown:
                continue

            last_valid_time = time_sec
            zone_id = self.find_zone_for_point(xm, ym, level)
            zone_obj = next((z for z in zones if z["id"] == zone_id), None)
            zone_name = zone_obj["name"] if zone_obj else f"Zona {zone_id + 1}"
            is_hit = (zone_id == int(target_zone))

            if is_hit:
                hits += 1
                score += self.HIT_POINTS
            else:
                misses += 1
                score = max(0, score - self.MISS_PENALTY)

            if zone_id in zone_counts:
                zone_counts[zone_id]["total"] += 1
                if is_hit:
                    zone_counts[zone_id]["hits"] += 1
                else:
                    zone_counts[zone_id]["misses"] += 1

            evaluated_events.append({
                "shot_number": len(evaluated_events) + 1,
                "frame": frame_idx,
                "time_sec": round(time_sec, 2),
                "pixel_u": round(u, 1),
                "pixel_v": round(v, 1),
                "x_m": xm,
                "y_m": ym,
                "zone_id": zone_id,
                "zone_name": zone_name,
                "target_zone": int(target_zone),
                "is_hit": is_hit,
                "score_after": score
            })

        total_shots = hits + misses
        accuracy = round((hits / total_shots) * 100.0, 1) if total_shots > 0 else 0.0

        zone_stats_list = list(zone_counts.values())
        best_hit_z = max(zone_stats_list, key=lambda z: z["hits"], default=None)
        most_miss_z = max(zone_stats_list, key=lambda z: z["misses"], default=None)

        most_hits_summary = (
            f"Z{best_hit_z['id'] + 1} ({best_hit_z['name']}): {best_hit_z['hits']} acerto(s)"
            if best_hit_z and best_hit_z["hits"] > 0
            else "Nenhum acerto na zona-foco"
        )
        most_misses_summary = (
            f"Z{most_miss_z['id'] + 1} ({most_miss_z['name']}): {most_miss_z['misses']} erro(s)"
            if most_miss_z and most_miss_z["misses"] > 0
            else "Nenhum erro registrado"
        )

        return {
            "score": score,
            "hits": hits,
            "misses": misses,
            "total_shots": total_shots,
            "accuracy": accuracy,
            "events": evaluated_events,
            "zone_stats": zone_stats_list,
            "most_hits_summary": most_hits_summary,
            "most_misses_summary": most_misses_summary
        }
