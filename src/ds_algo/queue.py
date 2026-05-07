# src/ds_algo/queue.py
import heapq

class TurnNode:
    """
    우선순위 큐에 들어갈 노드 객체입니다.
    비교 연산자(__lt__)를 오버라이딩하여 heapq가 'time_to_act' 기준으로 정렬하게 합니다.
    """
    def __init__(self, entity, time_to_act):
        self.entity = entity
        self.time_to_act = time_to_act

    def __lt__(self, other):
        return self.time_to_act < other.time_to_act


class TurnQueue:
    """
    [자료구조: Priority Queue (Min-Heap)]
    각 캐릭터의 행동 대기 시간(Time to act)을 기반으로 다음 턴을 결정합니다.
    """
    def __init__(self):
        self.heap = []

    def enqueue(self, entity, current_time=0):
        """
        엔티티를 큐에 추가합니다. Time Complexity: O(log N)
        Speed가 높을수록 다음 행동까지의 대기 시간(delay)이 짧아집니다.
        """
        # 속도가 0인 경우를 방지하기 위해 max(1, speed) 사용
        delay = 100 / max(1, entity.speed) 
        time_to_act = current_time + delay
        
        node = TurnNode(entity, time_to_act)
        heapq.heappush(self.heap, node)

    def dequeue(self):
        """
        가장 먼저 행동해야 할(대기 시간이 가장 짧은) 엔티티를 꺼냅니다. Time Complexity: O(log N)
        Returns: (행동할 엔티티, 해당 엔티티의 행동 시간)
        """
        if not self.is_empty():
            node = heapq.heappop(self.heap)
            return node.entity, node.time_to_act
        return None, 0

    def is_empty(self):
        return len(self.heap) == 0