from pico2d import load_image, get_time, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT

from state_machine import StateMachine, space_down, time_out, right_down, left_down, right_up, left_up


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
        if get_time() - self.boy.idle_start_time >= 5:
            self.boy.state_machine.add_event(('TIME_OUT', 0))

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
    SPEED = 10
    MIN_X, MAX_X = 50, 750  # 캐릭터 폭 100 의 절반만큼 화면 안쪽

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.left_held = self.right_held = False
        self.image = load_image('animation_sheet.png')

        self.IDLE = Idle(self)
        self.SLEEP = Sleep(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {time_out: self.SLEEP, right_down: self.RUN, left_down: self.RUN},
                self.SLEEP: {space_down: self.IDLE, right_down: self.RUN, left_down: self.RUN},
                # 방향키를 하나라도 누르고 있으면 RUN 유지
                self.RUN: {self.all_dir_keys_released: self.IDLE},
            }
        )

    def is_dir_key_held(self):
        return self.left_held or self.right_held

    def all_dir_keys_released(self, e):
        return (right_up(e) or left_up(e)) and not self.is_dir_key_held()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            # 마지막으로 누른 방향으로 달린다
            if event.key == SDLK_LEFT:
                self.left_held, self.dir = True, -1
            else:
                self.right_held, self.dir = True, 1
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
        self.state_machine.handle_event(('INPUT', event))

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
