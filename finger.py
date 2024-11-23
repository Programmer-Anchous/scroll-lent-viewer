from math import hypot
from tools import sign


class Finger:
    def __init__(self, fps):
        self.finger_down = False
        self.finger_up = False

        self.finger_down_pos = (-1, -1)
        self.finger_up_pos = (-1, -1)

        self.finger_down_timer = 0
        self.clicked = False
        self.is_drag = False
        self.drag_threshold_dist = 8

        self.last_motion = 0
        self.is_inertion = False
        self.motion_coeff = 1.5

        self.fps = fps
        self.delay = int(self.fps * 0.6)

        self.dx = 0
        self.dy = 0
        self.path_length = 0
        self.frame = None

    def update(self, frame=None):
        self.frame = frame
        if self.is_inertion:
            self.last_motion = sign(self.last_motion) * \
                (abs(self.last_motion) - 1.3)
            if abs(self.last_motion) < 1.5:
                self.last_motion = 0
                self.is_inertion = False

        self.clicked = False

        if self.finger_down:
            self.finger_down_timer += 1
            self.path_length += hypot(self.dx, self.dy)

        if self.path() >= self.drag_threshold_dist and self.is_press_in_frame():
            self.is_drag = True

        if self.is_drag:
            self.is_inertion = False

        if self.finger_up:
            if self.finger_down_timer < self.delay and self.distance() < 5 \
                    and self.path() < self.drag_threshold_dist:
                self.clicked = True
            self.finger_up = False
            self.finger_down = False
            self.finger_down_timer = 0
            self.path_length = 0

            if self.is_drag:
                if self.is_press_in_frame():
                    self.is_inertion = True
            self.is_drag = False

        self.dx = 0
        self.dy = 0

    def is_press_in_frame(self):
        return self.frame.collidepoint(self.finger_down_pos)

    def distance(self):
        """
        distance between finger press and release positions
        """
        return hypot(
            self.finger_down_pos[0] - self.finger_up_pos[0],
            self.finger_down_pos[1] - self.finger_up_pos[1]
        )

    def path(self):
        """
        length of the finger trajectory
        """
        return self.path_length

    def is_clicked(self):
        return self.clicked

    def down(self, finger_down_pos):
        self.finger_down_pos = finger_down_pos
        self.finger_down = True

    def up(self, finger_up_pos):
        self.finger_up_pos = finger_up_pos
        self.finger_up = True

    def motion(self, motion):
        self.dx, self.dy = motion
        if not self.is_inertion:
            self.last_motion = self.dy

    def get_scroll(self):
        if self.is_drag:
            return self.last_motion * self.motion_coeff
        return 0

    def get_inertion_scroll(self):
        if self.is_inertion:
            return self.last_motion * self.motion_coeff
        return 0
