import os
import json
from datetime import datetime


class StorageManager:
    def __init__(self, data_dir: str = "app/data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.homography_file = os.path.join(self.data_dir, "homografia.json")
        self.profiles_file = os.path.join(self.data_dir, "profiles.json")

    def save_homography(self, data: dict):
        with open(self.homography_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_homography(self) -> dict:
        if not os.path.exists(self.homography_file):
            return {}
        try:
            with open(self.homography_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def load_profiles(self) -> dict:
        if not os.path.exists(self.profiles_file):
            return {}
        try:
            with open(self.profiles_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_profiles(self, profiles: dict):
        with open(self.profiles_file, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)

    def get_or_create_profile(self, name: str) -> dict:
        clean_name = name.strip()
        profiles = self.load_profiles()
        if clean_name not in profiles:
            profiles[clean_name] = {
                "name": clean_name,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "sessions": []
            }
            self.save_profiles(profiles)
        return profiles[clean_name]

    def record_session(self, player_name: str, session_data: dict) -> dict:
        clean_name = player_name.strip() or "Jogador"
        profiles = self.load_profiles()
        if clean_name not in profiles:
            profiles[clean_name] = {
                "name": clean_name,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "sessions": []
            }

        entry = {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "level": session_data.get("level", "basico"),
            "target_zone": session_data.get("target_zone", 0),
            "source": session_data.get("source", ""),
            "score": session_data.get("score", 0),
            "hits": session_data.get("hits", 0),
            "misses": session_data.get("misses", 0),
            "total_shots": session_data.get("total_shots", 0),
            "accuracy": session_data.get("accuracy", 0.0),
            "events": session_data.get("events", [])
        }
        profiles[clean_name]["sessions"].append(entry)
        self.save_profiles(profiles)
        return entry

    def get_ranking(self) -> dict:
        """
        Retorna o ranking separado por nível ('basico', 'medio', 'avancado'),
        exibindo a melhor sessão de cada perfil ordenada por Pontuação (e Precisão como desempate).
        """
        profiles = self.load_profiles()
        ranking = {"basico": [], "medio": [], "avancado": []}

        for level in ["basico", "medio", "avancado"]:
            level_entries = []
            for player_name, pdata in profiles.items():
                sessions = [s for s in pdata.get("sessions", []) if s.get("level") == level]
                if not sessions:
                    continue
                best = max(sessions, key=lambda s: (s.get("score", 0), s.get("accuracy", 0.0)))
                level_entries.append({
                    "player": player_name,
                    "score": best.get("score", 0),
                    "hits": best.get("hits", 0),
                    "misses": best.get("misses", 0),
                    "accuracy": best.get("accuracy", 0.0),
                    "date": best.get("date", ""),
                    "total_sessions": len(sessions)
                })

            level_entries.sort(key=lambda x: (x["score"], x["accuracy"]), reverse=True)
            ranking[level] = level_entries

        return ranking

