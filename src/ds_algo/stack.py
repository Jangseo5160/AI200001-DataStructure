# src/ds_algo/stack.py

class UndoStack:
    """
    [자료구조: Stack (LIFO)]
    사용자의 이전 행동(상태)을 저장하여 되돌리기(Undo) 기능을 제공합니다.
    메모리 제한을 위해 최대 저장 개수(max_size)를 설정합니다.
    """
    def __init__(self, max_size=50):
        self.items = []
        self.max_size = max_size

    def push(self, state):
        """
        새로운 게임 상태를 스택의 맨 위에 추가합니다. Time Complexity: O(1)
        용량을 초과하면 가장 오래된 상태(인덱스 0)를 삭제합니다.
        """
        if len(self.items) >= self.max_size:
            self.items.pop(0)  # 가장 오래된 기록 삭제 (O(N) 이지만 N이 작아 무방)
        self.items.append(state)

    def pop(self):
        """
        가장 최근의 게임 상태를 꺼내어 반환합니다. Time Complexity: O(1)
        """
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        """
        스택에서 꺼내지 않고 가장 최근 상태만 확인합니다. Time Complexity: O(1)
        """
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def clear(self):
        """새로운 층으로 이동할 때 등 스택을 초기화합니다."""
        self.items = []