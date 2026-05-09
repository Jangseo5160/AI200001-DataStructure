from pathlib import Path


class Leaderboard:
    def __init__(self, file_path="data/leaderboard.txt"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        if not self.file_path.exists():
            return []

        scores = []
        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) != 2:
                    continue

                name, score_text = parts
                try:
                    scores.append((name, int(score_text)))
                except ValueError:
                    continue

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores

    def add_score(self, name: str, score: int):
        scores = self.load()
        scores.append((name, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        scores = scores[:10]

        with self.file_path.open("w", encoding="utf-8") as file:
            for player_name, player_score in scores:
                file.write(f"{player_name} {player_score}\n")

    def display(self) -> str:
        scores = self.load()
        if not scores:
            return "No scores yet."

        lines = ["Leaderboard"]
        for index, (name, score) in enumerate(scores, start=1):
            lines.append(f"{index}. {name}: {score}")

        return "\n".join(lines)
