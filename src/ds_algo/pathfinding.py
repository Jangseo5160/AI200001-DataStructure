# src/ds_algo/pathfinding.py
import heapq

def heuristic(a, b):
    """
    [알고리즘: Heuristic Function]
    Manhattan Distance (격자 기반 맵이므로 대각선 이동을 안 한다면 맨해튼이 최적입니다.)
    """
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(dungeon_map, start, goal):
    """
    [알고리즘: A* Pathfinding]
    start 좌표에서 goal 좌표까지의 최단 경로를 탐색합니다.
    
    Args:
        dungeon_map: is_walkable(x, y) 메서드를 가진 맵 객체
        start: (x, y) 튜플
        goal: (x, y) 튜플
        
    Returns:
        최단 경로를 나타내는 좌표들의 리스트 [(x1,y1), (x2,y2)...] (도달 불가시 빈 리스트)
    """
    # 우선순위 큐 (f_score 가 가장 낮은 노드를 먼저 탐색)
    frontier = []
    heapq.heappush(frontier, (0, start))
    
    # 경로 추적을 위한 딕셔너리 (어느 타일에서 왔는지 기록)
    came_from = {}
    came_from[start] = None
    
    # 시작점부터 현재 노드까지의 실제 비용 (g_score)
    cost_so_far = {}
    cost_so_far[start] = 0
    
    # 4방향 이동 (상, 하, 좌, 우)
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while frontier:
        _, current = heapq.heappop(frontier)
        
        # 목표 지점에 도달하면 탐색 종료
        if current == goal:
            break
            
        # 인접한 4방향 타일 탐색
        for dx, dy in directions:
            next_node = (current[0] + dx, current[1] + dy)
            
            # 맵을 벗어나거나 벽이면 패스
            if not dungeon_map.is_walkable(next_node[0], next_node[1]) and next_node != goal:
                continue
                
            new_cost = cost_so_far[current] + 1 # 이동 비용은 1로 고정
            
            # 처음 방문하거나 더 적은 비용으로 도달 가능한 경우 업데이트
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                # f(n) = g(n) + h(n)
                priority = new_cost + heuristic(next_node, goal)
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current
                
    # 목표 지점에 도달하지 못함 (길이 막힘)
    if goal not in came_from:
        return []
        
    # 역추적하여 경로 생성
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse() # 역순으로 담겼으므로 뒤집기
    
    return path