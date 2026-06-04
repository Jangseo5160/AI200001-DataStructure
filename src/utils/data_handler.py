import json
from datetime import datetime
from pathlib import Path


LEADERBOARD_PATH = Path(__file__).resolve().parents[1] / "data" / "leaderboard.json"


def load_leaderboard():
    """리더보드 파일을 읽어 리스트로 반환합니다."""
    if not LEADERBOARD_PATH.exists() or LEADERBOARD_PATH.stat().st_size == 0:
        return []

    try:
        with LEADERBOARD_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("scores"), list):
        return data["scores"]
    return []


def save_leaderboard(entries):
    """리더보드를 점수순으로 정렬해 저장합니다."""
    LEADERBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    sorted_entries = sorted(entries, key=lambda entry: entry.get("score", 0), reverse=True)

    with LEADERBOARD_PATH.open("w", encoding="utf-8") as file:
        json.dump(sorted_entries[:10], file, ensure_ascii=False, indent=2)


def add_leaderboard_entry(player, floor_id, turns):
    """현재 플레이 기록을 리더보드에 추가합니다."""
    score = player.level * 100 + player.exp + player.hp + floor_id * 50
    entry = {
        "name": player.name,
        "score": score,
        "floor": floor_id,
        "level": player.level,
        "exp": player.exp,
        "hp": player.hp,
        "turns": turns,
        "cleared_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    entries = load_leaderboard()
    entries.append(entry)
    save_leaderboard(entries)
    return entry
