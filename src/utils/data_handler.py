import json
from datetime import datetime
from pathlib import Path

from src.ds_algo.sorting import get_top_k_scores, ScoreRecord


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
    """
    [알고리즘: Min-Heap Top-K] 리더보드를 상위 10개만 추출해 저장합니다.

    get_top_k_scores()는 크기 K의 Min-Heap을 유지하여 O(N log K)로 상위 K개를 추출합니다.
    대안인 sorted()[:10]은 O(N log N)으로 전체 정렬 후 슬라이싱 — 항목이 많을수록 비효율.
    상위 10개만 필요하므로 Heap Top-K가 더 적합합니다.
    """
    LEADERBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)

    records = [ScoreRecord(e.get("name", ""), e.get("score", 0), e.get("floor", 0)) for e in entries]
    top_records = get_top_k_scores(records, k=10)
    top_names = {r.player_name + str(r.score) for r in top_records}

    top_entries = [e for e in entries if (e.get("name", "") + str(e.get("score", 0))) in top_names]
    top_entries = sorted(top_entries, key=lambda e: e.get("score", 0), reverse=True)[:10]

    with LEADERBOARD_PATH.open("w", encoding="utf-8") as file:
        json.dump(top_entries, file, ensure_ascii=False, indent=2)


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
