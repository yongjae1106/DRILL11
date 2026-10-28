from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_a


# 이벤트 판별 함수 - e 는 ('INPUT', sdl_event) 또는 ('TIME_OUT', 0) 형태의 튜플
def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


class StateMachine:
    def __init__(self, start_state, rules):
        # rules: {상태 객체: {판별 함수: 다음 상태 객체}}
        self.cur_state = start_state
        self.rules = rules
        self.event_q = []
        self.cur_state.enter(('START', 0))

    def add_event(self, e):
        # 상태 내부(do)에서 발생한 이벤트는 큐에 넣어두고 do 가 끝난 뒤 처리한다
        self.event_q.append(e)

    def handle_event(self, e):
        # 현재 상태의 전이 규칙 중 처음으로 맞는 것 하나만 적용, 맞는 게 없으면 무시
        for check_event, next_state in self.rules[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(e)
                self.cur_state = next_state
                self.cur_state.enter(e)
                return

    def update(self):
        self.cur_state.do()
        while self.event_q:
            self.handle_event(self.event_q.pop(0))

    def draw(self):
        self.cur_state.draw()
