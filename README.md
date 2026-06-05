# Dungeon Crawler - Data Structure & Algorithm Guide

터미널에서 실행되는 `ncurses library` 기반 던전 크롤러 게임입니다.  

## 실행 방법

### 요구 사항
- Python 3.6 이상
  - # Ubuntu / Debian
    ```
    sudo apt update
    sudo apt install python3

    # Fedora / RHEL
    sudo dnf install python3
    ```
# Arch
sudo pacman -S python
- 별도 패키지 설치 불필요 (표준 라이브러리만 사용)
- macOS / Linux / WSL 환경 권장
  - Windows 네이티브 환경은 `curses`가 기본 지원되지 않습니다.
    Windows에서는 아래 명령어로 패키지를 먼저 설치하세요:
    ```
    pip install windows-curses
    ```

### 실행

프로젝트 루트 디렉토리에서 아래 명령어를 실행합니다:

```bash
python3 main.py
```

## 조작법

| 키 | 기능 |
| --- | --- |
| `WASD` / 방향키 | 이동 |
| `p` | 인벤토리의 포션 사용 |
| `u` | Undo |
| `r` | Redo |
| `i` | 인벤토리 보기 |
| `l` | 리더보드 보기 |
| `q` | 종료 |

## 프로젝트 구조

```text
main.py                  # curses 실행 진입점
src/engine.py            # 게임 루프, 입력, 턴, 전투, Undo/Redo, 아이템 처리
src/core/entities.py     # Player, Enemy, Potion, Weapon, Armor, Goal, Ladder
src/core/map.py          # 2D 배열 기반 던전 맵 생성
src/ui/renderer.py       # curses 화면 렌더링
src/utils/data_handler.py # 리더보드 JSON 저장/로드
src/ds_algo/pathfinding.py # A* 알고리즘
src/ds_algo/queue.py     # 우선순위 큐 기반 턴 관리
src/ds_algo/stack.py     # Undo/Redo 스택
src/ds_algo/sorting.py   # Top-K 점수 정렬 예시
src/test/                # unittest 테스트
```

## 핵심 기능 6개

| 기능 | 구현 위치 | 자료구조/알고리즘 | 핵심 설명 |
| --- | --- | --- | --- |
| Dungeon Map | `src/core/map.py` | 2D Array, 절차적 방/복도 생성 | `grid[y][x]`로 벽과 길을 O(1)에 조회 |
| Undo System | `src/engine.py`, `src/ds_algo/stack.py` | Stack, Deep Copy Snapshot | 플레이어 행동 전 상태를 저장하고 LIFO로 복원 |
| Turn Management | `src/engine.py`, `src/ds_algo/queue.py` | Priority Queue, Min-Heap | 속도에 따라 다음 행동 시간을 계산해 가장 빠른 엔티티부터 실행 |
| Item Inventory | `src/core/entities.py`, `src/engine.py` | List | 획득 아이템을 플레이어 인벤토리에 저장, 포션 사용/장비 장착 지원 |
| Enemy AI | `src/engine.py`, `src/ds_algo/pathfinding.py` | A* Search, Manhattan Distance | 적이 플레이어까지의 최단 경로를 계산해 추적 |
| Leaderboard | `src/utils/data_handler.py`, `src/data/leaderboard.json` | JSON List, Sorting | 클리어 점수를 저장하고 점수 내림차순 상위 10개 유지 |

## 알고리즘 설명 및 비교

### 1. Dungeon Maps

- 구현: `Floor.grid`는 2차원 리스트입니다.
- 선택 이유: 좌표 기반 게임에서는 `(x, y)` 위치의 벽/길 판정이 자주 발생하므로 O(1) 조회가 중요합니다.
- 시간복잡도:
  - 타일 조회: O(1)
  - 맵 생성: 방 개수와 방 크기에 비례, 대략 O(R * A)
- 대안 비교:
  - 그래프 인접 리스트: 길찾기에는 좋지만, 화면 렌더링과 좌표 조회가 2D 배열보다 직관적이지 않습니다.
  - 문자열 맵: 표시에는 편하지만 수정 가능한 던전 생성에는 리스트보다 불편합니다.

### 2. Undo System

- 구현: `UndoStack`이 이전 상태 스냅샷을 저장합니다.
- 선택 이유: Undo는 가장 최근 행동부터 되돌려야 하므로 LIFO 구조가 자연스럽습니다.
- 시간복잡도:
  - push/pop: O(1)
  - 최대 크기 초과 시 오래된 상태 제거: O(N)
- 대안 비교:
  - Queue: 먼저 저장된 상태부터 꺼내므로 Undo 순서와 맞지 않습니다.
  - Command Pattern: 메모리는 적게 쓸 수 있지만, 모든 행동마다 역연산을 직접 구현해야 해서 코드가 복잡해집니다.

### 3. Turn Management

- 구현: `TurnQueue`는 `heapq` 기반 Min-Heap입니다.
- 선택 이유: 플레이어와 적의 `speed`에 따라 다음 행동 시간이 다르므로, 가장 작은 행동 시간을 빠르게 꺼내야 합니다.
- 시간복잡도:
  - enqueue/dequeue: O(log N)
  - 다음 턴 확인: heap root 기준 O(1)
- 대안 비교:
  - 단순 리스트 정렬: 매 턴 정렬하면 O(N log N)이 반복됩니다.
  - 원형 큐: 모든 캐릭터가 같은 속도일 때는 좋지만, 속도 차이를 반영하기 어렵습니다.

### 4. Item Inventory

- 구현: `Player.inventory`는 리스트입니다. 포션은 `p` 키로 사용하고, 무기/방어구는 획득 시 장착됩니다.
- 선택 이유: 아이템 개수가 작고, 화면에 순서대로 보여주는 일이 중요하므로 리스트가 단순하고 충분합니다.
- 시간복잡도:
  - 아이템 추가: O(1)
  - 특정 아이템 검색/삭제: O(N)
- 대안 비교:
  - Dictionary: ID 조회는 O(1)이지만, 같은 종류 아이템 여러 개와 화면 순서 관리가 번거롭습니다.
  - Tree: 카테고리 표현에는 좋지만 현재 게임 규모에서는 과한 구조입니다.

### 5. Enemy AI

- 구현: 적은 플레이어가 인접하면 공격하고, 멀리 있으면 A*로 다음 이동 칸을 찾습니다.
- 선택 이유: A*는 실제 이동 비용 `g(n)`과 목표까지의 휴리스틱 `h(n)`을 함께 사용해 BFS보다 효율적으로 최단 경로를 찾습니다.
- 휴리스틱: 상하좌우 이동만 가능하므로 Manhattan Distance를 사용합니다.
- 시간복잡도:
  - 일반적으로 O(E log V)
  - 격자 맵에서는 V가 타일 수, E가 인접 이동 관계입니다.
- 대안 비교:
  - BFS: 모든 방향을 균등 탐색하므로 최단 경로는 보장하지만 목표 방향성이 없어 더 많은 노드를 방문할 수 있습니다.
  - DFS: 빠르게 깊게 들어가지만 최단 경로를 보장하지 않습니다.
  - Greedy Best-First Search: 목표 방향으로 빠르게 가지만 실제 비용을 무시해 우회로에서 비효율적일 수 있습니다.

### 6. Leaderboard

- 구현: 클리어 시 점수를 JSON 파일에 저장하고 내림차순 정렬 후 상위 10개만 유지합니다.
- 선택 이유: 데이터 수가 작고 파일 기반 제출 환경에서 가장 호환성이 좋습니다.
- 시간복잡도:
  - 정렬 저장: O(N log N)
  - 파일 로드: O(N)
- 대안 비교:
  - Heap Top-K: 점수가 많아질 때 O(N log K)로 효율적입니다. 예시는 `src/ds_algo/sorting.py`에 있습니다.
  - SQLite: 안정적인 DB 기능은 좋지만 제출 환경에서 설정 부담이 커집니다.

## 코드 품질 포인트

- 게임 흐름은 `GameEngine`에 모아 입력, 이동, 전투, 턴 처리를 한 곳에서 추적할 수 있습니다.
- 맵, 엔티티, 렌더링, 알고리즘, 저장 로직은 별도 모듈로 분리했습니다.
- 리더보드 파일이 없거나 JSON이 깨졌을 때 빈 리스트를 반환하도록 예외 처리를 넣었습니다.
- Undo/Redo는 플레이어 행동 전에만 스냅샷을 저장해 의미 없는 상태 저장을 줄였습니다.
- 테스트는 외부 의존성 없이 `unittest`로 실행 가능합니다.

