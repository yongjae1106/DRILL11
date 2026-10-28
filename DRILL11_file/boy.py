from pico2d import load_image, get_time, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine


class Idle:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        # IDLE 에 들어갈 때마다 5초 타이머를 시작한다
        self.boy.idle_start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8

    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_draw(self.boy.frame * 100, 300, 100, 100, self.boy.x, self.boy.y)
        else:
            self.boy.image.clip_draw(self.boy.frame * 100, 200, 100, 100, self.boy.x, self.boy.y)


class Sleep:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8

    def draw(self):
        # IDLE 프레임을 90도 눕혀서 그린다
        if self.boy.face_dir == 1:
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 300, 100, 100,
                                               3.141592 / 2, '', self.boy.x - 25, self.boy.y - 25, 100, 100)
        else:
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 200, 100, 100,
                                               -3.141592 / 2, '', self.boy.x + 25, self.boy.y - 25, 100, 100)


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        # 방향(self.boy.dir)은 Boy.handle_event 에서 눌린 키를 보고 정한다
        self.boy.frame = (self.boy.frame + 1) % 8
        self.boy.face_dir = self.boy.dir
        self.boy.x = max(Boy.MIN_X, min(Boy.MAX_X, self.boy.x + self.boy.dir * Boy.SPEED))

    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y)
        else:
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y)


class Boy:
    # 상태 목록 - IDLE 에 들어갈 때마다 5초 타이머를 시작한다
    states = [
        {'name': 'IDLE', 'on_enter': 'start_idle_timer'},
        'SLEEP',
        'RUN',
    ]

    # 전이 목록
    transitions = [
        {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
        {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
        # 왼쪽/오른쪽 구분 없이 하나의 RUN 상태 - 방향은 self.dir 로 가진다
        {'trigger': 'dir_down', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
        # 방향키를 하나라도 누르고 있으면 RUN 유지
        {'trigger': 'dir_up', 'source': 'RUN', 'dest': 'IDLE', 'unless': 'is_dir_key_held'},
    ]

    SPEED = 10
    MIN_X, MAX_X = 50, 750  # 캐릭터 폭 100 의 절반만큼 화면 안쪽

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.left_held = self.right_held = False
        self.image = load_image('animation_sheet.png')

        # transitions 상태 머신: self(Boy)가 모델이 되어 self.state 로 현재 상태를 가진다
        # ignore_invalid_triggers: 현재 상태에서 정의되지 않은 이벤트는 무시 (예: IDLE 에서 SPACE)
        self.machine = Machine(model=self, states=Boy.states, transitions=Boy.transitions,
                               initial='IDLE', ignore_invalid_triggers=True)
        # 초기 상태 진입 시에는 on_enter 가 호출되지 않으므로 직접 타이머 시작
        self.start_idle_timer()

    def start_idle_timer(self):
        self.idle_start_time = get_time()

    def is_dir_key_held(self):
        return self.left_held or self.right_held

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                self.space_down()
            elif event.key in (SDLK_LEFT, SDLK_RIGHT):
                # 마지막으로 누른 방향으로 달린다
                if event.key == SDLK_LEFT:
                    self.left_held, self.dir = True, -1
                else:
                    self.right_held, self.dir = True, 1
                self.dir_down()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            # 한쪽을 떼도 반대쪽을 누르고 있으면 그 방향으로 계속 달린다
            if event.key == SDLK_LEFT:
                self.left_held = False
                if self.right_held:
                    self.dir = 1
            else:
                self.right_held = False
                if self.left_held:
                    self.dir = -1
            self.dir_up()

    def update(self):
        self.frame = (self.frame + 1) % 8
        if self.state == 'IDLE' and get_time() - self.idle_start_time >= 5:
            self.time_out()
        elif self.state == 'RUN':
            self.face_dir = self.dir
            self.x = max(Boy.MIN_X, min(Boy.MAX_X, self.x + self.dir * Boy.SPEED))

    def draw(self):
        if self.state == 'IDLE':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            # IDLE 프레임을 90도 눕혀서 그린다
            if self.face_dir == 1:
                self.image.clip_composite_draw(self.frame * 100, 300, 100, 100,
                                               3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
            else:
                self.image.clip_composite_draw(self.frame * 100, 200, 100, 100,
                                               -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)
        elif self.state == 'RUN':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 100, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)
