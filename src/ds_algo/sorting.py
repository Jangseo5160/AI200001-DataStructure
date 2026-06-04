# src/ds_algo/sorting.py
import heapq

class ScoreRecord:
    def __init__(self, player_name, score, floor_reached):
        self.player_name = player_name
        self.score = score
        self.floor_reached = floor_reached

    # Min-Heap 구성을 위한 비교 연산자 (점수 오름차순)
    def __lt__(self, other):
        return self.score < other.score

def get_top_k_scores(score_list, k=10):
    """
    [알고리즘: Top K Elements using Min-Heap]
    전체 데이터를 정렬하지 않고, 크기 K의 Min-Heap을 유지하여 상위 K개의 스코어만 추출합니다.
    Time Complexity: O(N log K)
    """
    if not score_list:
        return []
        
    min_heap = []
    
    for record in score_list:
        # 힙의 크기가 K보다 작으면 일단 푸시
        if len(min_heap) < k:
            heapq.heappush(min_heap, record)
        else:
            # 힙의 최솟값(가장 점수가 낮은 기록)보다 현재 기록이 높으면 교체
            if record.score > min_heap[0].score:
                heapq.heappushpop(min_heap, record)
                
    # 힙 안의 데이터는 상위 K개지만 정렬되어 있지는 않으므로, 내림차순 정렬하여 반환
    top_scores = sorted(min_heap, key=lambda x: x.score, reverse=True)
    return top_scores