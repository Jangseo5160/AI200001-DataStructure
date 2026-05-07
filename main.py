# main.py
import curses
import sys
import traceback

# 우리가 작성한 게임 엔진 임포트
from src.engine import GameEngine

def main(stdscr):
    """
    curses.wrapper에 의해 호출되는 메인 함수입니다.
    터미널 환경을 초기화하고 게임 루프를 시작합니다.
    """
    # 1. Curses 환경 최적화 설정
    curses.curs_set(0)          # 화면에서 깜빡이는 커서 숨기기
    stdscr.nodelay(True)        # 키 입력을 기다리지 않고 게임 루프 계속 진행 (Non-blocking)
    stdscr.keypad(True)         # 방향키 등 터미널 특수 키 입력 활성화
    curses.mousemask(0)         # 마우스 입력 무시 (텍스트 기반이므로)

    # 2. 게임 엔진 인스턴스 생성
    engine = GameEngine()
    
    # 3. 게임 실행
    try:
        # engine.py에 작성해둔 메인 루프 실행
        engine.run(stdscr)
    except Exception as e:
        # curses 환경 내부에서 에러가 나면 화면이 깨진 채로 멈출 수 있습니다.
        # 에러를 잡아서 밖으로 던져, 안전하게 터미널을 복구한 뒤 에러 로그를 보게 합니다.
        raise e

if __name__ == "__main__":
    print("던전 크롤러를 로딩 중입니다...")
    
    try:
        # curses.wrapper: 터미널을 제어 모드로 안전하게 진입시키고,
        # 에러가 나거나 종료될 때 터미널 설정을 원래대로 완벽하게 복구(Cleanup)해 줍니다.
        curses.wrapper(main)
    except KeyboardInterrupt:
        # 사용자가 Ctrl+C를 눌러 강제 종료했을 때의 처리
        pass
    except Exception as e:
        # 게임 루프 내에서 발생한 치명적 에러를 터미널 복구 후 출력
        print("\n[치명적 오류 발생] 게임이 예기치 않게 종료되었습니다:")
        traceback.print_exc()
    finally:
        print("\n게임이 안전하게 종료되었습니다. 터미널 환경이 복구되었습니다.")
        sys.exit(0)