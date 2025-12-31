import asyncio
from pygame import *
from math import floor, copysign
from random import randint
from typing import Any, Optional, Union, Callable, Sequence, Tuple, List, Dict


ENABLE_CONTROLLERS = True
IS_WEB = False
IS_MOBILE = False


# File Locations
CONTROLLERS = "assets/controllers.dat"
KEY_BINDS = "assets/key binds.dat"
KEY_BIND_DEFAULT = "assets/default key binds.dat"
LEADERBOARD = "assets/leaderboard.dat"
FONT_MAIN = "assets/msgothic.ttc"
FONT_SCORE = "assets/bahnschrift.ttf"
SCREEN_START = "assets/startscreen.jpg"
SCREEN_END = "assets/endscreen.jpg"
SPLASH = "assets/splash.png"
SHEET_SPRITE = "assets/spritesheet.png"
SHEET_UI = "assets/controller.png"
SOUND_MUSIC = "assets/music.ogg"
SOUND_SFX = ("assets/quack1.ogg", "assets/quack2.ogg", "assets/quack3.ogg", "assets/grass1.ogg", "assets/grass2.ogg",
             "assets/error.ogg", "assets/cannon.ogg", "assets/levelup.ogg", "assets/gameover.ogg")

# set global variables
UI_CROP = {
    "leftclick": Rect(0, 0, 1, 1), "middleclick": Rect(1, 0, 1, 1), "rightclick": Rect(2, 0, 1, 1),
    "sidebutton1": Rect(3, 0, 1, 1), "sidebutton2": Rect(0, 1, 1, 1), "mouse": Rect(1, 1, 1, 1),
    "guide": Rect(0, 2, 1, 1), "guide.ps": Rect(1, 2, 1, 1), "guide.xbox": Rect(2, 2, 1, 1), "dpx": Rect(3, 2, 1, 1),
    "misc1": Rect(0, 3, 2, 1), "start.xbox": Rect(2, 3, 1, 1), "back.xbox": Rect(3, 3, 1, 1),
    "start": Rect(0, 4, 2, 1), "back": Rect(2, 4, 2, 1),
    "a": Rect(0, 5, 1, 1), "b": Rect(1, 5, 1, 1), "x": Rect(2, 5, 1, 1), "y": Rect(3, 5, 1, 1),
    "a.ps": Rect(0, 6, 1, 1), "b.ps": Rect(1, 6, 1, 1), "x.ps": Rect(2, 6, 1, 1), "y.ps": Rect(3, 6, 1, 1),
    "dpup": Rect(0, 7, 1, 1), "dpright": Rect(1, 7, 1, 1), "dpdown": Rect(2, 7, 1, 1), "dpleft": Rect(3, 7, 1, 1),
    "lefttrigger": Rect(0, 8, 1, 1), "righttrigger": Rect(1, 8, 1, 1),
    "leftshoulder": Rect(2, 8, 1, 1), "rightshoulder": Rect(3, 8, 1, 1),
    "lefttrigger.ps": Rect(2, 9, 1, 1), "righttrigger.ps": Rect(3, 9, 1, 1),
    "leftshoulder.ps": Rect(0, 9, 1, 1), "rightshoulder.ps": Rect(1, 9, 1, 1),
    "leftstick": Rect(0, 10, 1, 1), "rightstick": Rect(1, 10, 1, 1),
    "leftx": Rect(2, 10, 1, 1), "rightx": Rect(3, 10, 1, 1)}
KEYBOARD_ID = "0" * 32
RESOLUTION = 256
QUICK_KEYBINDS = 10
CONTROLLER_SENSITIVITY = 0.1
MENU_TRANSITION_TIME = 700
S_NUM_TYPES = 7
S_DECORATOR, S_ROAD, S_OBSTACLE, S_LOAF, S_DUCK, S_BREAD, S_PLAYER = range(S_NUM_TYPES)

GREY_GREEN = (127, 191, 127)


class UserInterface:
    """
    class for handling user input
    """

    UI_TYPE = Tuple[Union[Sequence[bool], Sequence[float]]]  # type used to store sequences of user-input data

    @staticmethod
    def read_controllers(file: str) -> Dict[str, List[List[str]]]:
        """
        Returns a dictionary representation of the "controllers.dat" file
        """

        contents = read(file)
        keys, values = [], []
        for line in contents:
            line = line.split(":")
            keys.append(line[0])
            value = line[1]
            new_value = []
            for device in value.split("|"):
                new_value.append(device.split(","))
            values.append(new_value)
        return dict(zip(keys, values))

    def __init__(self, device: int = -1, img: Optional[Surface] = None):
        self.img = img
        self.key_binds: Dict[str, Tuple[int, int]] = {}
        self.device: Optional[joystick.Joystick] = None
        self.device_name: str = "Mouse and Keyboard"
        self.device_id: str = KEYBOARD_ID
        if device != -1:
            self.device = joystick.Joystick(device)
            self.device_name = self.device.get_name()
            self.device_id = self.device.get_guid()
            self.device.init()
        self.current: UI.UI_TYPE = ([],)
        self.last: UI.UI_TYPE = self.current
        self.controllers = UI.read_controllers(CONTROLLERS)[self.device_id]

    def __str__(self) -> str:
        return f"{self.device_name}:{self.device_id}"

    def __repr__(self) -> str:
        """
        Returns the string used for saving and loading the user's key bind options
        """

        items = self.key_binds.items()
        if self.device is not None:
            items = list(items)[QUICK_KEYBINDS:]
        return f"{self.device_name}\n" + '\n'.join([f"{b}:{i[0]}:{i[1]}" for b, i in items]) + "\n"

    def save(self, file: str) -> None:
        """
        Saves key bind data to a given file
        """

        contents = read(file)
        if f"{self.device_name}" in contents:  # if the key bind data already exists then delete it to be replaced
            i = contents.index(self.device_name)
            del contents[i:contents.index('', i) + 1]
        contents += repr(self).split("\n")
        write(file, contents)

    def load(self, file: str) -> None:
        """
        Loads key bind data from a given file
        """

        if self.device is not None:
            self.key_binds = {str(i): (0, 0) for i in range(QUICK_KEYBINDS)}
        contents = read(file)
        if self.device_name not in contents:
            self.key_binds.update({i: (0, 0) for i in ("Left", "Right", "Throw", "Aim", "Menu")})
            keys = ("dpleft", "dpright", "rightshoulder", "rightx", "start")
            for a, l in enumerate(self.controllers):
                for b, i in enumerate(l):
                    if i in keys:
                        i = list(self.key_binds.keys())[keys.index(i) + QUICK_KEYBINDS]
                        self.key_binds[i] = (a, b)
        else:
            i = contents.index(self.device_name)
            contents = contents[i + 1:contents.index('', i)]
            for i in contents:
                i = i.split(':')
                self.key_binds[i[0]] = (int(i[1]), int(i[2]))

    def update(self) -> None:
        """
        Updates user-input data
        """

        self.last = self.current
        if self.device is None:
            self.current = (key.get_pressed(), mouse.get_pressed(5), mouse.get_pos())
        else:
            self.current = ([self.device.get_button(i) for i in range(self.device.get_numbuttons())],
                            [self.device.get_hat(i) for i in range(self.device.get_numhats())],
                            [self.device.get_axis(i) for i in range(self.device.get_numaxes())])
            if len(self.last) == len(self.current):
                for i, j in enumerate(self.current[2]):
                    if abs(j) < CONTROLLER_SENSITIVITY:
                        i = i // 2 * 2
                        self.current[2][i] = self.last[2][i]
                        self.current[2][i + 1] = self.last[2][i + 1]

    def pressed(self, button: str) -> bool:
        """
        True when a key or button is held by the user
        """

        return bool(self.current[self.key_binds[button][0]][self.key_binds[button][1]])

    def tapped(self, button: str) -> bool:
        """
        True for the first frame a key or button is pushed by the user
        """

        return bool(self.pressed(button) and not self.last[self.key_binds[button][0]][self.key_binds[button][1]])

    def any(self, event_keyboard: List[int], mouse_movement: Vector2,
            button_or_cursor: int = 2) -> Optional[Tuple[int, int]]:
        """
        Returns any key, button, mouse, or joystick being used by the user
        """

        for i, inputs in enumerate(self.current):
            if len(inputs) > 0:
                if isinstance(inputs[0], float) or (self.device_id == KEYBOARD_ID and i == 2):
                    if button_or_cursor > 0:
                        for j, pressed in enumerate(inputs):
                            if self.device_id == KEYBOARD_ID and i == 2:
                                pressed = mouse_movement
                            elif pressed == self.last[i][j]:
                                pressed = (0, 0)
                            if pressed != (0, 0):
                                return i, j // 2 * 2
                elif button_or_cursor != 1:
                    if self.device_id == KEYBOARD_ID and i == 0:
                        if event_keyboard:
                            return i, event_keyboard[0]
                    else:
                        lst = inputs[:]
                        if True in lst:
                            return i, lst.index(True)

    def get_cursor(self, button: str, point: Vector2, bar_mode: int) -> Vector2:
        """
        Returns a Vector2 from a given mouse or joystick user-input
        """

        button = self.key_binds[button]
        i = self.current[button[0]]
        if self.device_id == KEYBOARD_ID:
            c = mouse_pos(bar_mode)
            c[0] -= RESOLUTION // 2
            c[1] = RESOLUTION - c[1]
            c -= point
        else:
            c = Vector2(i[button[1]], -i[button[1] + 1])
        if c:
            return c.normalize()
        else:
            return Vector2(0, 1)

    def get_image(self, button: str, use_font: font.Font) -> Surface:
        """
        Returns an image corresponding to the given key, button, mouse, joystick, or trackball
        """

        if self.device_id == KEYBOARD_ID and self.key_binds[button][0] == 0:
            text = use_font.render(key.name(self.key_binds[button][1]).capitalize(), False, Color("White"))
            size = Vector2(text.get_size()) + Vector2(4, 3)
            padding = 0
            if size[0] < 16:
                padding = (16 - size[0]) / 2
                size[0] = 16
            surf = Surface(size)
            surf.fill(Color("grey50"))
            draw.polygon(surf, Color("black"), ((0, 0), (size[0] - 1, 0), size - Vector2(1, 1), (0, size[1] - 1)), 3)
            surf.blit(text, (padding + 3, 2))
            return surf
        else:
            button = self.key_binds[button]
            button = self.controllers[button[0]][button[1]]
            cropper = UI_CROP
            if "ps" in self.device_name.lower() and button + ".ps" in cropper.keys():
                button += ".ps"
            elif "xbox" in self.device_name.lower() and button + ".xbox" in cropper.keys():
                button += ".xbox"
            cropper = cropper[button].copy()
            for i in range(4):
                cropper[i] *= 16
            return self.img.subsurface(cropper).copy()


UI = UserInterface  # shorter name for the UserInterface class


class Sprite:

    def __init__(self, sprite_type, costumes: List[Surface], position: Vector2,
                 on_update: Callable[[Any], None] = lambda self_: None):
        self.sprite_type = sprite_type
        self.velocity: Vector2 = Vector2(0, 0)
        self.costumes = costumes
        self.costume: int = 0
        self.flip_costume: List[bool, bool] = [False, False]
        self.arrange: Vector2 = Vector2(0, -1)
        self.position: Vector2 = position
        self.update: Callable[[Sprite], None] = on_update

        self.mode = ""
        self.timer = None
        self.bonus = None
        self.feet = None
        self.feet_frame = None

    def delete(self, sprites):
        """
        Removes the sprite from a given list
        """

        sprite_type = sprites[self.sprite_type]
        if self in sprite_type:
            del sprite_type[sprite_type.index(self)]

    def get_image(self) -> Surface:
        return transform.flip(self.costumes[self.costume], self.flip_costume[0], self.flip_costume[1])

    def get_size(self) -> Vector2:
        return Vector2(self.get_image().get_size())

    def get_screen_position(self) -> Vector2:
        """Converts the sprite's unit position to its position on screen"""
        position = (Vector2(floor(self.position[0]), floor(self.position[1]))
                    + v_mul(Vector2(RESOLUTION, RESOLUTION) - self.get_size(),
                            (self.arrange + Vector2(1, -1)) / 2))
        position[1] = -position[1]
        return position

    def flip_horizontally(self) -> None:
        self.flip_costume[0] = not self.flip_costume[0]

    def flip_vertically(self) -> None:
        self.flip_costume[1] = not self.flip_costume[1]

    def snap(self, arrangement: str) -> None:
        """
        Sets the side or corner to which the sprite is arranged;
        e.g. "Top Left" snaps the sprite to the top left corner if its position is set to (0, 0)
        """

        arrangement = arrangement.lower()
        if "center" in arrangement:
            self.arrange.update(0, 0)
        if "top" in arrangement:
            self.arrange[1] = 1
        elif "bottom" in arrangement:
            self.arrange[1] = -1
        if "left" in arrangement:
            self.arrange[0] = -1
        elif "right" in arrangement:
            self.arrange[0] = 1

    def move_by(self, vector: Vector2) -> None:
        """
        Changes the x and y position of the sprite by the given amount
        """

        self.position += vector

    def draw(self, screen: Surface, paused: bool, player: Any, player_speed: float, aim_override: Vector2, ui: UI,
             bar_mode: int, level: int, pause: bool) -> None:
        """
        Blits the sprite onto the given surface
        """

        if not paused:
            self.update(self)
        if self.sprite_type == S_DUCK and (level != 2 or self.mode == "full"):
            self.draw_feet(screen)
        elif self.sprite_type == S_BREAD:
            self.draw_shadow(screen, player, player_speed)
        elif self is player and not IS_MOBILE:
            self.draw_laser(screen, ui, bar_mode, pause, aim_override)
        costume = self.get_image()
        screen.blit(costume, self.get_screen_position()[:])

    def draw_shadow(self, screen: Surface, player: Any, player_speed: float) -> None:
        """
        Used mainly for the bread sprite when it is thrown
        """

        player: Sprite

        down = round((player.position[1] - self.position[1]) * (self.velocity[1] - player_speed) / 8)
        if down < 0:
            costume = self.get_image().copy()
            costume.fill((0, 0, 0, 127), None, BLEND_RGBA_MULT)
            screen.blit(costume, (self.get_screen_position() - Vector2(0, down))[:])

    def draw_laser(self, screen: Surface, ui: UI, bar_mode: int, override: bool, aim_override: Vector2 = None) -> None:
        v_start = self.position + Vector2(0, 8)
        if override:
            v_aim = aim_override
        else:
            v_aim = ui.get_cursor("Aim", v_start, bar_mode) * 24
            v_aim[1] = -v_aim[1]
            aim_override.update(v_aim)
        v_start[1] = -v_start[1]
        v_start += Vector2(RESOLUTION // 2, RESOLUTION)
        draw.line(screen, Color("red"), v_start, v_start + v_aim)

    def draw_feet(self, screen: Surface) -> None:
        img = self.feet[self.feet_frame // 100]
        img = transform.flip(img, *self.flip_costume)
        screen.blit(img, (self.get_screen_position() + Vector2(4, 12))[:])

    def colliding(self, *others) -> bool:
        others: Tuple[Sprite]
        mask1 = mask.from_surface(self.get_image())
        for other in others:
            mask2 = mask.from_surface(other.get_image())
            offset = other.position - self.position
            offset: any
            if mask1.overlap(mask2, offset):
                return True
        return False


class Button:
    """
    Class for handling on screen buttons widgets
    """

    def __init__(self, use_font: font.Font, text: str,
                 hover_sound: Optional[mixer.Sound] = None, click_sound: Optional[mixer.Sound] = None,
                 animate: bool = True):
        self.font = use_font
        self.text = ""
        self.img = None
        self.update_text(text)
        self.position = Vector2(0, 0)
        if IS_MOBILE:
            self.hover_sound = False
            self.click_sound = hover_sound
        else:
            self.hover_sound = hover_sound
            self.click_sound = click_sound
        self.animate = animate
        self.hover = False

    def update_text(self, text: str) -> None:
        """
        Replaces the button's text and updates its image to match
        """

        if self.img:
            trans = self.img.get_alpha()
        else:
            trans = None
        self.text = text
        text = self.font.render(text, False, Color("white"))
        size = Vector2(text.get_size()) + Vector2(5, 4)
        padding = 0
        if size[0] < 16:
            padding = (16 - size[0]) / 2
            size[0] = 16
        self.img = Surface(size)
        self.img.fill(Color("grey50"))
        draw.polygon(self.img, Color("black"), ((0, 0), (size[0] - 1, 0), size - Vector2(1, 1), (0, size[1] - 1)), 3)
        self.img.blit(text, (padding + 3, 2))
        self.img.set_alpha(trans)

    def set_image(self, img: Surface) -> None:
        self.img = img

    def center(self) -> None:
        """
        Moves the button to the center of the screen horizontally
        """

        self.position[0] = (RESOLUTION - self.img.get_width()) // 2

    def update(self, quick_keys: UI, bar_mode: int, trans: bool, tabbed: bool = False,
               only_widget: bool = False) -> bool:
        """
        Updates and returns if the button has been pressed
        """

        animate = self.animate and not (only_widget or IS_MOBILE)
        mouse_p = mouse_pos(bar_mode)
        last_hover = self.hover
        hover_amount = Vector2(0, (1 + animate)) * (not IS_MOBILE)
        if trans:
            self.hover = False
            if animate:
                self.img.set_alpha(240)
        else:
            self.hover = (Rect(self.position - hover_amount + hover_amount * last_hover,
                               Vector2(self.img.get_size()) + hover_amount).collidepoint(*mouse_p) or tabbed)
        if only_widget and (quick_keys.tapped("qEnter") or quick_keys.tapped("qEnter2")):
            if self.click_sound:
                self.click_sound.play()
            return True
        elif self.hover:
            if not last_hover:
                if self.hover_sound:
                    self.hover_sound.play()
                self.position -= hover_amount
            if (quick_keys.tapped("Click"), quick_keys.tapped("qEnter") or quick_keys.tapped("qEnter2"))[tabbed]:
                if self.click_sound:
                    self.click_sound.play()
                return True
        elif last_hover and not self.hover:
            self.position += hover_amount
        if animate:
            self.img.set_alpha((240, None)[self.hover])
        return False

    def get_image(self) -> Tuple[Surface, Vector2]:
        return self.img, self.position


class Slider:
    """
    Class for handling on screen slider widgets
    """

    def __init__(self, starting_value: float, bg_color: Color, fg_color: Color):
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.img = Surface((80, 8))
        self.img.fill(bg_color)
        self.position = Vector2(0, 0)
        self.value: float = starting_value
        self.selected = False
        self.update_image()

    def update_image(self) -> None:
        """
        Updates the image of the slider to match its value
        """

        self.img.fill(self.bg_color)
        draw.rect(self.img, self.fg_color, Rect((0, 0), (self.value * self.img.get_width(), self.img.get_height())))

    def center(self) -> None:
        """
        Moves the slider to the center of the screen horizontally
        """

        self.position[0] = (RESOLUTION - self.img.get_width()) // 2

    def update(self, quick_keys: UI, bar_mode: int, tabbed: bool, trans: bool, sound: mixer.Sound = None) -> float:
        """
        Updates and returns the value that the slider is put to
        """

        mouse_p = mouse_pos(bar_mode)
        hover_amount = Vector2(0, 1)
        if trans:
            hover = False
        else:
            hover = (Rect(self.position - hover_amount + hover_amount * self.selected,
                          Vector2(self.img.get_size()) + hover_amount).collidepoint(*mouse_p))
        last_selected = self.selected
        if (hover and quick_keys.tapped("Click")) or (tabbed and not self.selected):
            self.selected = True
            self.position[1] -= 1
        if self.selected:
            if tabbed or quick_keys.pressed("Click"):
                if tabbed:
                    self.value += (quick_keys.pressed("qRight") - quick_keys.pressed("qLeft")) * 0.01
                else:
                    self.value = (mouse_p - self.position)[0] / self.img.get_width()
                self.value = min(max(self.value, 0), 1)
                self.update_image()
            else:
                self.selected = False
                self.position[1] += 1
        if last_selected and not self.selected:
            sound.play()
        return self.value

    def get_image(self) -> Tuple[Surface, Vector2]:
        return self.img, self.position


def read(file: str, binary: bool = False) -> Union[List[str], Dict[str, str]]:
    """
    Quick and easy function for reading from a file
    """

    m = "r"
    if binary:
        m += "b"
    with open(file, m) as f:
        if binary:
            contents = f.read()
        else:
            contents = ''.join(f.readlines()).split('\n')
    return contents


def write(file: str, contents: Union[List[str], bytes], binary: bool = False) -> None:
    """
    Quick and easy function for writing to a file
    """

    m = "w"
    if binary:
        m += "b"
    with open(file, m) as f:
        if binary:
            contents: str
            f.write(contents)
        else:
            f.writelines('\n'.join(contents))


def v_mul(*vectors: Vector2) -> Vector2:
    """
    Multiplies together all the x and y values of the given vectors
    """

    output = Vector2(1, 1)
    for v in vectors:
        output[0] *= v[0]
        output[1] *= v[1]
    return output


def render_text(use_font: font.Font, text: str, font_color: Color = Color("black"), position: Vector2 = Vector2(0, 0),
                screen: Surface = None, center: bool = False, on_right: bool = False) -> Surface:
    """
    Blits the given text with the given options onto the screen
    """
    write_position = Vector2(position)
    for line in text.split("\n"):
        render = use_font.render(line, False, font_color)
        if center:
            write_position[0] = (RESOLUTION - render.get_width()) // 2
        if on_right:
            write_position[0] -= render.get_width()
        screen.blit(render, write_position)
        write_position[0] += render.get_width()
        if not center:
            write_position[0] = position[0]
        write_position[1] += render.get_height()
    return screen


def get_game_screen(bar_mode, size_override: Optional[Sequence[float]] = None) -> Rect:
    """
    Returns a rectangle object that represents the portion of the screen that the game actually covers
    """

    if size_override:
        size = size_override
    else:
        size = display.get_window_size()
    if bar_mode == 0:
        bar_mode = (size[1] > size[0]) + 1
    elif bar_mode == 3:
        bar_mode = (size[1] < size[0]) + 1
    if bar_mode == 1:
        return Rect(0, (size[1] - size[0]) / (1 + (size[1] > size[0])), size[0], size[0])
    elif bar_mode == 2:
        return Rect((size[0] - size[1]) / 2, 0, size[1], size[1])


def mouse_pos(bar_mode: int) -> Vector2:
    """
    Returns the mouse position converted into in game units
    """

    game_screen = get_game_screen(bar_mode)
    scale = Vector2(RESOLUTION / game_screen.size[0], RESOLUTION / game_screen.size[1])
    mouse_p = v_mul(Vector2(mouse.get_pos()) - Vector2(game_screen.topleft), scale)
    return mouse_p


def get_desktop_size() -> Vector2:
    sizes = display.get_desktop_sizes()
    return Vector2(sizes[0])


async def main() -> None:
    init()
    key.stop_text_input()

    # import files
    splash_font = font.Font(FONT_MAIN, 10)
    use_font = font.Font(FONT_MAIN, 14)
    score_font = font.Font(FONT_SCORE, 40)
    score_font_big = font.Font(FONT_SCORE, 48)
    start_screen = image.load(SCREEN_START)
    end_screen = image.load(SCREEN_END)
    splash = image.load(SPLASH)
    sprite_sheet = image.load(SHEET_SPRITE)
    ui_sheet = image.load(SHEET_UI)
    mobile_sheet = ui_sheet.subsurface(32, 16, 16, 16)
    mobile_sheet = (mobile_sheet, transform.flip(mobile_sheet, True, False),
                    transform.scale(ui_sheet.subsurface(48, 16, 16, 16), (32, 32)))
    music = mixer.Sound(SOUND_MUSIC)
    sfx = {f.split('.')[0].split('/')[-1]: mixer.Sound(f) for f in SOUND_SFX}

    # initialize display
    def reset_screen() -> None:
        nonlocal screen, screen_full

        display.quit()
        if IS_MOBILE:
            screen = display.set_mode(screen_size, FULLSCREEN)
        else:
            screen = display.set_mode(screen_size, RESIZABLE)
            screen_full = False
        display.set_icon(sprite_sheet.subsurface(48, 128, 16, 16))
        display.set_caption("Roboduck")

    def fullscreen() -> None:
        nonlocal screen, screen_full, screen_size

        if not IS_WEB:
            screen_full = not screen_full
            if screen_full:
                screen_size = display.get_window_size()
                display.set_mode(get_desktop_size(), FULLSCREEN)
                screen_rect = get_game_screen(bar_mode, screen_size)
                screen_full_rect = get_game_screen(bar_mode)
                mouse.set_pos(*v_mul(Vector2(mouse.get_pos()) - Vector2(screen_rect.topleft),
                                     Vector2(screen_full_rect.width / screen_rect.width,
                                             screen_full_rect.height / screen_rect.height)) + Vector2(screen_full_rect.topleft))
            else:
                screen_rect = get_game_screen(bar_mode, screen_size)
                screen_full_rect = get_game_screen(bar_mode)
                mouse.set_pos(*v_mul(Vector2(mouse.get_pos()) - Vector2(screen_full_rect.topleft),
                                     Vector2(screen_rect.width / screen_full_rect.width,
                                             screen_rect.height / screen_full_rect.height)) + Vector2(screen_rect.topleft))
                display.set_mode(screen_size)
                display.set_mode(screen_size, RESIZABLE)

    def trans(blit: bool, to: str, trans_time: int, backward: bool = False) -> None:
        nonlocal mode, old_mode, new_mode, transition1, transition2, trans_dir, anim_timer, total_time

        if blit:
            old_mode = mode
            new_mode = to
            transition1 = update(False)
            mode = to
            transition2 = update(False)
            mode = "transition"
            anim_timer = trans_time
            total_time = trans_time
            if backward:
                trans_dir = -1
            else:
                trans_dir = 1

    def update(blit: bool = True) -> Surface:
        nonlocal mode, anim_timer, score_timer, last_score, score_i, pause, score_name, leaderboard_timer
        nonlocal tabbed_widget, bar_mode, volume_music, volume_effect, keybind_select, keybind_selected, last_size
        nonlocal level, sprites, player_y, player_last_y, player_speed, duck_speed
        nonlocal transition1, transition2, trans_dir, total_time, old_mode, background, last_aim

        if not (IS_MOBILE and mode == "play"):
            screen.fill(Color("black"))
        game_surf = Surface((RESOLUTION, RESOLUTION)).convert_alpha()
        game_surf.fill((0, 0, 0, 0))
        game_screen = get_game_screen(bar_mode)
        if mode == "logo":
            background = Surface((RESOLUTION, RESOLUTION))
            background.fill(Color("black"))
        else:
            background = start_screen.copy()
        if mode == "logo":
            grey = None
            anim_timer -= clock.get_time()
            if anim_timer <= 0:
                mode = "start"
                anim_timer = 1000
            elif anim_timer <= 3000:
                splash.set_alpha(255)
                try:
                    name = ""
                except Exception:
                    name = ""
                render_text(splash_font, f"(ɔ) 2023, Evil Fish Co. All rights reserved.\nTEST{name}",
                            Color("white"), Vector2(0, 176), game_surf, True)
                if anim_timer <= 2000:
                    grey = game_surf.copy()
                    grey.fill(Color("black"))
                    grey.set_alpha((2000 - anim_timer) * 255 // 2000)
            else:
                splash.set_alpha((5000 - anim_timer) * 255 // 2000)
            game_surf.blit(splash, (64, 32))
            if grey is not None:
                game_surf.blit(grey, (0, 0))
        if mode == "transition":
            anim_x = anim_timer / total_time * RESOLUTION * trans_dir
            anim_timer -= clock.get_time()
            if anim_timer < 0:
                mode = new_mode
                if mode in ("options", "help"):
                    old_mode = "start"
            game_surf.blit(transition1, (anim_x - RESOLUTION * trans_dir, 0))
            game_surf.blit(transition2, (anim_x, 0))
        elif mode == "start":
            render_text(score_font_big, "Roboduck", Color("dark blue"), Vector2(0, 0), game_surf, True)
            if anim_timer <= 0:
                handle_tabs(len(widgets[0]))
                for i, widget in enumerate(widgets[0]):
                    if widget.update(quick_keys, bar_mode, not blit, tabbed_widget == i):
                        tabbed_widget = None
                        if widget.text.lower() == "play":
                            mode = "play"
                            reset_game()
                        elif widget.text.lower() == "quit":
                            mode = "quit"
                        else:
                            trans(blit, widget.text.lower(), MENU_TRANSITION_TIME)
            game_surf.blits(widgets_draw[0])
            if mode != "transition" and anim_timer > 0:
                anim_timer -= clock.get_time()
                grey = game_surf.copy()
                grey.fill(Color("black"))
                grey.set_alpha(anim_timer * 255 // 1000)
                game_surf.blit(grey, (0, 0))
        elif mode == "play":
            game_surf.fill(Color(("dark green", "dark blue", GREY_GREEN)[level - 1]))
            for i in sum(sprites, []):
                i.draw(game_surf, pause, player_sprite, player_speed[1], last_aim, ui, bar_mode,
                       level, pause)
            top_left = Vector2(-game_screen.left * RESOLUTION / game_screen.size[1],
                               -game_screen.top * RESOLUTION / game_screen.size[0])
            if game_screen.topleft[0] > 0:
                top_left[0] = 0
            if game_screen.topleft[1] > 0:
                top_left[1] = 0

            if IS_MOBILE and not pause:
                s = display.get_window_size()
                if s != last_size:
                    last_size = s
                    if s[0] > s[1]:
                        mobile_box_size = (s[0] - game_screen.width) / 2, game_screen.height
                        mobile_box[0].update((0, 0), mobile_box_size)
                        mobile_box[1].update((mobile_box_size[0] + game_screen.width, 0), mobile_box_size)
                    else:
                        mobile_box_size = game_screen.width / 2, (s[1] - game_screen.height) / 2
                        h = s[1] - mobile_box_size[1]
                        mobile_box[0].update((0, h), mobile_box_size)
                        mobile_box[1].update((mobile_box_size[0], h), mobile_box_size)
                    s = Vector2(game_screen.size) * 32 / RESOLUTION
                    mobile_box[2].update((game_screen.right - s[0], game_screen.top), s)
                    if mobile_box[2].collidepoint(quick_keys.current[2]):
                        mobile_sheet[2].set_alpha(None)
                    else:
                        mobile_sheet[2].set_alpha(127)
                    screen.fill("black")
                    for i in range(2):
                        screen.blit(transform.scale(mobile_sheet[i], mobile_box[i].size), mobile_box[i].topleft)
                game_surf.blit(mobile_sheet[2], (RESOLUTION - 32, 0))

            if score != last_score:
                score_i = 0
                for i in range(len(str(score)) + 1):
                    i = i + 1
                    if len(str(score)) < i:
                        score_char = "0"
                    else:
                        score_char = str(score)[-i]
                    if len(str(last_score)) < i:
                        j = "0"
                    else:
                        j = str(last_score)[-i]
                    if score_char == j:
                        score_i = 1 - i
                        break
                last_score = score
            if score_timer > 0:
                score_timer -= clock.get_time()
            else:
                score_i = 0
            if score_i == 0:
                text1 = str(score)
            else:
                text1 = str(score)[:score_i]
            text2 = str(score)[score_i:]
            render_text(score_font, text1, Color("white"), Vector2(top_left) + Vector2(3, 0), game_surf)
            if score_i != 0:
                render_text(score_font_big, text2, Color("white"), Vector2(top_left) +
                            Vector2(3 + score_font.size(text1)[0], -3), game_surf)
            render_text(use_font, str(ammo), Color("white"), Vector2(top_left) + Vector2(2, 40),
                        game_surf)
            if player_sprite.timer is not None:
                pause = False
                grey = game_surf.copy()
                grey.fill(Color("black"))
                grey.set_alpha(255 - player_sprite.timer * (255 / 1000))
                game_surf.blit(grey, (0, 0))
            elif pause:
                grey = game_surf.copy()
                grey.fill(Color("black"))
                grey.set_alpha(127)
                game_surf.blit(grey, (0, 0))
                handle_tabs(len(widgets[5]))
                for i, widget in enumerate(widgets[5]):
                    if widget.update(quick_keys, bar_mode, not blit, tabbed_widget == i):
                        if widget.text == "Main Menu":
                            mode = "start"
                            pause = False
                        elif widget.text == "Leaderboard":
                            mode = "leaderboard"
                        elif widget.text == "Back to Game":
                            pause = False
                game_surf.blits(widgets_draw[5])
        elif mode == "leaderboard":
            if score_name is not None:
                pause = True
            grey = game_surf.copy()
            grey.fill(Color("black"))
            grey.set_alpha(127)
            game_surf.blit(grey, (0, 0))
            text = read(LEADERBOARD)
            if pause:
                button_text = ("Continue", "Back")[score_name is None]
                if widgets[6][0].text != button_text:
                    widgets[6][0].update_text(button_text)
                    widgets_draw[6][0] = widgets[6][0].get_image()
                    widgets[6][0].center()
                game_surf.blits(widgets_draw[6])
                if score_name is not None:
                    if len(score_name) > 3:
                        score_name = score_name[:3]
                    if len(score_name) == 3:
                        anim_timer = 0
                        underscore = ""
                    else:
                        anim_timer += clock.get_time()
                        anim_timer %= 2000
                        underscore = "_ "[anim_timer // 1000]
                    text.insert(get_leaderboard_position(), f"{score_name}{underscore}:{score}")
                    if len(text) > 5:
                        text = text[:5] + [""]
                if widgets[6][0].update(quick_keys, bar_mode, not blit, only_widget=True):
                    if score_name is None:
                        mode = "play"
                    else:
                        mode = "gameover"
                elif score_name is not None and quick_keys.pressed("Click"):
                    key.stop_text_input()
                    key.start_text_input()
                if mode != "leaderboard":
                    tabbed_widget = None
                    if score_name is not None:
                        if score_name != "":
                            text[get_leaderboard_position()] = f"{score_name}:{score}"
                            write(LEADERBOARD, text)
                        score_name = None
                        pause = False
            elif ui.any(event_keyboard, movement):
                mode = "start"
                leaderboard_timer = 10000
            text = "\n".join(["LEADERBOARD"] + text)
            render_text(use_font, text, Color("gold"), Vector2(0, 32), game_surf, True)
        elif mode == "levelup":
            if widgets[6][0].update(quick_keys, bar_mode, not blit, only_widget=True):
                tabbed_widget = None
                if level > len(level_lengths):
                    if get_leaderboard_position() is not None:
                        mode = "leaderboard"
                        score_name = ""
                    else:
                        mode = "gameover"
                else:
                    mode = "play"
            game_surf.blit(*widgets_draw[6][0])
            if level == 4:
                text = "YOU WIN\nTHE END"
            else:
                text = f"NEXT LEVEL\n{level} OF 3"
            text += f"\n\nSCORE:{score}\nBREAD:{ammo}\n"
            render_text(use_font, text,
                        Color("black"), Vector2(0, 16), game_surf, True)
        elif mode == "gameover":
            win_or_lose = level > len(level_lengths)
            game_surf.blit((end_screen, start_screen)[win_or_lose], (0, 0))
            if widgets[7][0].update(quick_keys, bar_mode, not blit):
                mode = "play"
                reset_game()
            elif widgets[7][1].update(quick_keys, bar_mode, not blit):
                mode = "start"
            if mode != "gameover":
                tabbed_widget = None
                anim_timer = 0
            game_surf.blits(widgets_draw[7])
            use_color = Color(("dark red", "green")[win_or_lose])
            render_text(score_font, ("GAME OVER", "YOU WIN")[win_or_lose],
                        use_color, Vector2(0, 32), game_surf, True)
            render_text(use_font, f"FINAL SCORE\n{score}", use_color, Vector2(0, 80), game_surf, True)
        elif mode == "options":
            handle_tabs(len(widgets[1]))
            for i, widget in enumerate(widgets[1]):
                if widget.update(quick_keys, bar_mode, not blit, tabbed_widget == i):
                    tabbed_widget = None
                    if IS_MOBILE and widget.text.lower() == "display":
                        sfx["error"].play()
                    elif widget.text.lower() == "back":
                        trans(blit, old_mode, MENU_TRANSITION_TIME, True)
                    else:
                        trans(blit, widget.text.lower(), MENU_TRANSITION_TIME)
            game_surf.blits(widgets_draw[1])
        elif mode == "display":
            text = ("No", "Horizontal", "Vertical", "Both")[bar_mode] + " Bars"
            render_text(use_font, text, Color("dark blue"), Vector2(140, 73), game_surf, on_right=True)
            widgets[2][0].set_image(sprite_sheet.subsurface(bar_mode * 16, 144, 16, 16))
            widgets_draw[2][0] = widgets[2][0].get_image()
            handle_tabs(len(widgets[2]))
            for i, widget in enumerate(widgets[2]):
                if widget.update(quick_keys, bar_mode, not blit, tabbed_widget == i):
                    if widget.text == "":
                        bar_mode = (bar_mode + 1) % 4
                    elif widget.text == "Fullscreen":
                        fullscreen()
                    elif widget.text == "Reset":
                        bar_mode = 3
                        reset_screen()
                    elif widget.text == "Back":
                        tabbed_widget = None
                        trans(blit, old_mode, MENU_TRANSITION_TIME, True)
            game_surf.blits(widgets_draw[2])
        elif mode == "sound":
            render_text(use_font, "Music", Color("dark blue"), Vector2(80, 80), game_surf)
            render_text(use_font, "Sound", Color("dark blue"), Vector2(80, 100), game_surf)
            handle_tabs(len(widgets[3]))
            for i, widget in enumerate(widgets[3]):
                if isinstance(widget, Button) and widget.update(quick_keys, bar_mode, not blit, tabbed_widget == i):
                    if widget.text == "Reset":
                        for j, k in enumerate((0.25, 0.50)):
                            widgets[3][j].value = k
                            widgets[3][j].update_image()
                    elif widget.text == "Back":
                        tabbed_widget = None
                        trans(blit, old_mode, MENU_TRANSITION_TIME, True)
                elif isinstance(widget, Slider):
                    widget.update(quick_keys, bar_mode, tabbed_widget == i, not blit, w_sfx)
                    if i == 0:
                        volume_music = widget.value * 100
                    elif i == 1:
                        volume_effect = widget.value * 100
            game_surf.blits(widgets_draw[3])
        elif mode == "keybinds":
            if IS_MOBILE:
                render_text(use_font, "Mobile instructions", Color("dark blue"),
                            Vector2(8, 0), game_surf, center=True)
                if widgets[4][-1].update(quick_keys, bar_mode, not blit, only_widget=True):
                    tabbed_widget = None
                    trans(blit, old_mode, MENU_TRANSITION_TIME, True)
                game_surf.blit(*widgets_draw[4][-1])
            else:
                for i, k in enumerate(list(ui.key_binds.keys())[QUICK_KEYBINDS:]):
                    render_text(use_font, k, Color("dark blue"), Vector2(100, RESOLUTION // 2 - 86 + i * 20), game_surf)
                    if i != keybind_selected or keybind_select == 0:
                        i += 1
                        widgets[4][i].set_image(ui.get_image(k, use_font))
                        widgets_draw[4][i] = widgets[4][i].get_image()
                handle_tabs(len(widgets[4]))
                for i, widget in enumerate(widgets[4]):
                    if widget.update(quick_keys, bar_mode, not blit, tabbed_widget == i):
                        if widget.text == "Reset":
                            write(KEY_BINDS, read(KEY_BIND_DEFAULT))
                            ui.load(KEY_BINDS)
                            keybind_select, keybind_selected = 0, 0
                        elif widget.text == "Back":
                            tabbed_widget = None
                            trans(blit, old_mode, MENU_TRANSITION_TIME, True)
                            ui.save(KEY_BINDS)
                            keybind_select, keybind_selected = 0, 0
                        elif widget.text != "":
                            update_ui()
                            if (not ENABLE_CONTROLLERS) or len(uis) == 1:
                                sfx["error"].play()
                            else:
                                w_sfx.play()
                                if uis.index(ui) == len(uis) - 1:
                                    select_ui(0)
                                else:
                                    select_ui(uis.index(ui) + 1)
                            widget.update_text(f"Device: {ui.device_name}")
                            widgets_draw[4][i] = widget.get_image()
                            widget.center()
                            keybind_select, keybind_selected = 0, 0
                        elif keybind_select and i - 1 == keybind_selected:
                            keybind_select, keybind_selected = 0, 0
                        else:
                            new_img = widget.img.copy()
                            new_img.fill(Color("white"))
                            widget.set_image(new_img)
                            widgets_draw[4][i] = widget.get_image()
                            keybind_select = 1
                            keybind_selected = i - 1
                game_surf.blits(widgets_draw[4])
        elif mode == "help":
            game_surf.fill(Color("grey 25"))
            render_text(use_font, "Throw bread at ducks to earn points\n"
                                  "while also dodging everything\nthat's in your way.\n"
                                  "If you can hit the same duck twice\nyou get three points from it.\n"
                                  "Collect loaves off the floor for\nmore bread to throw.\n"
                                  "Rare bread cannons can be used to\nfeed all ducks on screen\nat the same time.\n"
                                  "Most importantly, have fun!",
                        Color("white"), Vector2(0, 0), game_surf, center=True)
            game_surf.blits(widgets_draw[8])
            handle_tabs(len(widgets[8]))
            for i, widget in enumerate(widgets[8]):
                if widget.update(quick_keys, bar_mode, not blit, tabbed_widget == i):
                    tabbed_widget = None
                    if widget.text == "Keybinds":
                        trans(blit, "keybinds", MENU_TRANSITION_TIME)
                    elif widget.text == "Back":
                        trans(blit, old_mode, MENU_TRANSITION_TIME, True)
        if blit:
            screen.blit(transform.scale(background, game_screen.size), game_screen.topleft)
            screen.blit(transform.scale(game_surf, game_screen.size), game_screen.topleft)
            display.flip()
        return game_surf

    bar_mode = 3
    screen_size = (500, 500)
    screen_full = False
    screen = display.get_surface()
    reset_screen()
    last_size = None

    # initialize sound
    def update_sound() -> None:
        nonlocal playing_music

        play_music = mode == "play" and (not pause) and player_sprite.mode != "gameover"
        if play_music != playing_music:
            if play_music:
                playing_music = True
                music.play(-1)
            else:
                playing_music = False
                music.stop()
        music.set_volume(volume_music / 100)
        for i in sfx.values():
            i.set_volume(volume_effect / 100)

    volume_music, volume_effect = 25, 50
    playing_music = False

    # initialize user input
    def update_ui() -> None:
        nonlocal uis

        for _ in range(joystick.get_count() - (len(uis) - 1)):
            uis.append(UI(len(uis) - 1, ui_sheet))

    def select_ui(index: int) -> None:
        nonlocal ui

        ui = uis[index]
        ui.load(KEY_BINDS)
        ui.update()

    def get_leaderboard_position() -> Optional[int]:
        for i, line in enumerate(read(LEADERBOARD)):
            if line == "" or score > int(line.split(":")[1]):
                if line != "" or i < 5:
                    return i

    def handle_tabs(number_of_buttons: int) -> None:
        nonlocal tabbed_widget

        if movement:
            tabbed_widget = None
        elif quick_keys.tapped("qTab"):
            if tabbed_widget is None:
                if quick_keys.pressed("qReverse"):
                    tabbed_widget = number_of_buttons - 1
                else:
                    tabbed_widget = 0
            else:
                tabbed_widget += 1 * (1 - 2 * quick_keys.pressed("qReverse"))
                tabbed_widget %= number_of_buttons

    quick_keys = UI(img=ui_sheet)
    uis = [quick_keys]
    ui = quick_keys
    select_ui(0)
    keybind_select = 0
    keybind_selected = 0
    mobile_box = [Rect(0, 0, 0, 0), Rect(0, 0, 0, 0), Rect(0, 0, 0, 0)]
    score_name: Optional[str] = None
    w_sfx = sfx["quack1"]
    widgets: List[List[Union[Button, Slider]]] = [
        [Button(use_font, "Play", w_sfx), Button(use_font, "Options", w_sfx),
         Button(use_font, "Help", w_sfx), Button(use_font, "Quit", w_sfx)],
        [Button(use_font, "Display", w_sfx), Button(use_font, "Sound", w_sfx),
         Button(use_font, "Keybinds", w_sfx), Button(use_font, "Back", w_sfx)],
        [Button(use_font, "", animate=False), Button(use_font, "Fullscreen", w_sfx),
         Button(use_font, "Reset", w_sfx), Button(use_font, "Back", w_sfx)],
        [Slider(0.25, Color("gray 50"), Color("dark blue")),
         Slider(0.50, Color("gray 50"), Color("dark blue")),
         Button(use_font, "Reset", w_sfx), Button(use_font, "Back", w_sfx)],
        [Button(use_font, f"Device: {ui.device_name}", w_sfx),
         Button(use_font, "", animate=False), Button(use_font, "", animate=False), Button(use_font, "", animate=False),
         Button(use_font, "", animate=False), Button(use_font, "", animate=False),
         Button(use_font, "Reset", w_sfx), Button(use_font, "Back", w_sfx)],
        [Button(use_font, "Back to Game", w_sfx), Button(use_font, "Leaderboard", w_sfx),
         Button(use_font, "Main Menu", w_sfx)],
        [Button(use_font, "Continue", w_sfx)],
        [Button(use_font, "Play Again", w_sfx), Button(use_font, "Main Menu", w_sfx)],
        [Button(use_font, "Keybinds", w_sfx), Button(use_font, "Back", w_sfx)]]
    widgets_draw = [[w.get_image() for w in ws] for ws in widgets]
    for w_s, w_screen in enumerate(widgets):
        w_y = RESOLUTION // 2 + (-64, -64, -55, -42, -115, -48, 0, 0, 40)[w_s]
        for w in w_screen:
            if w_s == 0:
                w.img.set_alpha(240)
                w.position[1] -= 2
            w.center()
            w.position[1] = w_y
            if isinstance(w, Slider):
                w.position[0] += 40
                w_y += w.img.get_height() + 10
            else:
                if w.text == "":
                    w.position[0] += 20
                    w_y += 20
                else:
                    w_y += w.img.get_height() + 10
    keybind_types = (0, 0, 0, 1, 0)
    tabbed_widget = None

    # initialize sprites
    def reset_game() -> None:
        nonlocal level, pause, last_score, score_i, score, ammo

        level = 1
        pause = False
        last_score = "0"
        score_i = -1
        score = 0
        ammo = 12
        player_sprite.mode = ""
        player_sprite.timer = None
        player_sprite.position.update(0, 8)
        player_tracks.flip_costume = [False, False]
        reset_level()

    def reset_level() -> None:
        nonlocal sprites, player_y, player_last_y, player_total_y, duck_speed

        sprites = [[] for _ in range(S_NUM_TYPES)]
        sprites[S_PLAYER] += [player_sprite, player_tracks]
        player_y = 0
        player_last_y = 0
        player_total_y = 0
        duck_speed = 0.05 + 0.05 * level

    def world_load() -> None:
        def create_sprite(x: float, y: float):
            s = None
            if randint(1, 50) == 1:
                if randint(0, 1):  # OBSTACLES
                    sheet = obstacles[level - 1]
                    img = randint(0, len(sheet) - 1)
                    s = Sprite(S_OBSTACLE, [sprite_sheet.subsurface(*sheet[img])],
                               Vector2(x, y), update_obstacle)
                    if level == 2 and img in (1, 2):
                        s.mode = "vehicle"
                    elif level == 3 and img < 2:  # create and set the image used for the building
                        # creates a list with images corresponding to parts of the building in the following order:
                        # [top_left, top_right, side_left, side_right, bottom_left, bottom_right]
                        costumes = [transform.flip(sprite_sheet.subsurface(sheet[int(1 < i < 4)]), i % 2 == 1, i > 3)
                                    for i in range(6)]

                        height = randint(2, 4)
                        s.costumes[0] = Surface((32, height * 16))
                        for layer in range(height):
                            if layer == 0:
                                costume = 0
                            elif layer == height - 1:
                                costume = 4
                            else:
                                costume = 2
                            s.costumes[0].blit(costumes[costume], (0, layer * 16))
                            s.costumes[0].blit(costumes[costume + 1], (16, layer * 16))
                    if randint(0, 1):
                        s.flip_horizontally()
                    for obstacle in sprites[S_ROAD] + sprites[S_OBSTACLE] + sprites[S_LOAF] + sprites[S_DUCK]:
                        if obstacle is not s and s.colliding(obstacle):
                            s = None
                            break
                else:
                    if randint(1, 8) == 1:  # LOAF
                        if randint(1, 10) == 1:
                            s = Sprite(S_LOAF, [sprite_sheet.subsurface(32, 32, 16, 16)], Vector2(x, y), update_cannon)
                        else:
                            s = Sprite(S_LOAF, [sprite_sheet.subsurface(16, 40, 16, 8)], Vector2(x, y), update_loaf)
                        for obstacle in sprites[S_ROAD] + sprites[S_OBSTACLE]:
                            if s.colliding(obstacle):
                                s = None
                                break
                    else:  # DUCK
                        s = Sprite(S_DUCK, [sprite_sheet.subsurface(0, 16, 16, 16),
                                            sprite_sheet.subsurface(16, 16, 16, 16),
                                            sprite_sheet.subsurface(32, 16, 16, 16),
                                            sprite_sheet.subsurface(48, 16, 16, 16)], Vector2(x, y), update_duck)
                        s.bonus, s.timer, s.mode, s.feet, s.feet_frame = 0, 0, "land", feet, 0
                        if randint(0, 1):
                            s.flip_horizontally()
            elif randint(1, 20) == 1:
                sheet = decorators[level - 1]
                s = Sprite(S_DECORATOR, [sprite_sheet.subsurface(i) for i in sheet],
                           Vector2(x + randint(0, 1) * 8, y + randint(0, 1) * 8), update_decorator)
                s.costume = randint(0, 1)
                if randint(0, 1):
                    s.flip_horizontally()
                for obstacle in sprites[S_ROAD]:
                    if s.colliding(obstacle):
                        s = None
                        break
            if s:
                sprites[s.sprite_type].insert(0, s)

        length = RESOLUTION // 16
        if level == 3 and randint(1, 20) == 1:
            r = Sprite(S_ROAD, [road_img], Vector2(0, 256 - (player_y % 16)), update_road)
            r.timer = randint(15, 25) * 100
            sprites[r.sprite_type].insert(0, r)
        else:
            for x_position in range(length):
                create_sprite((x_position - length // 2 + 0.5) * 16, 256 - (player_y % 16))

    def update_player(self: Sprite) -> None:
        nonlocal mode, pause, score_name

        if self.mode == "gameover":
            self.timer -= clock.get_time()
            if self.timer <= 0:
                if get_leaderboard_position() is not None:
                    mode = "leaderboard"
                    score_name = ""
                else:
                    mode = "gameover"
            self.position[1] += 5
        if fps > 0:
            player_speed[1] = 0.5 + player_total_y / (total_length * 32)
            if IS_MOBILE and not pause:
                mx = 0
                if quick_keys.pressed("Click"):
                    mx = quick_keys.current[2]
                    mx = mobile_box[1].collidepoint(mx) - mobile_box[0].collidepoint(mx)
            else:
                mx = ui.pressed("Right") - ui.pressed("Left")
            m = Vector2(mx, 0) * 128 / fps
            if abs(self.position[0] + m[0]) > 120:
                m[0] = copysign(120, self.position[0]) - self.position[0]
            self.move_by(m)
            if mx != 0:
                self.costume = int(mx < 0)

    def update_tracks(self: Sprite) -> None:
        if player_sprite.mode == "gameover":
            self.costume = 3
            self.flip_costume = player_sprite.flip_costume
        else:
            self.costume = level - 1
            self.timer -= clock.get_time()
            if self.timer <= 0:
                self.timer = 80
                self.flip_horizontally()

    def update_sprite(self: Sprite) -> None:
        if fps > 0:
            self.velocity *= 0.99
            self.move_by((self.velocity - player_speed) * 128 / fps)
        if abs(self.position[0]) > 144 or self.position[1] < -64:
            self.delete(sprites)

    def update_loaf(self: Sprite) -> None:
        nonlocal ammo

        update_sprite(self)
        if self.colliding(player_sprite, player_tracks):
            ammo += 6
            sfx["error"].play()
            self.delete(sprites)
            return

    def update_bread(self: Sprite) -> None:
        nonlocal score, ammo, player_speed, score_timer

        update_sprite(self)
        for i in sprites[S_DUCK]:
            if self.colliding(i):
                score_timer += 250
                if i.bonus > 0:
                    score += 2
                score += 1
                i.bonus += 1
                i.mode = "full"
                sfx[("quack1", "quack2")[randint(0, 1)]].play()
                self.delete(sprites)
                return
        if (self.mode == "up" and self.velocity[1] < player_speed[1]) and self.colliding(player_sprite, player_tracks):
            ammo += 1
            sfx["error"].play()
            self.delete(sprites)
            return

    def update_cannon(self: Sprite) -> None:
        nonlocal ammo

        if self.timer is not None:
            self.timer -= clock.get_time()
            if self.timer < 0:
                self.delete(sprites)
                return
            else:
                self.costumes[self.costume].set_alpha(self.timer / 500 * 255)
        elif self.colliding(player_sprite, player_tracks):
            ammo += 12
            for i in sprites[S_DUCK]:
                aim_ = (i.position - self.position) / randint(20, 22)
                bread_ = Sprite(1, [sprite_sheet.subsurface(0, 32, 16, 16)],
                                Vector2(self.position),
                                update_bread)
                bread_.flip_costume = [aim_[0] < 0, False]
                bread_.sprite_type, bread_.velocity = S_BREAD, Vector2(aim_) + player_speed
                bread_.mode = "up" if bread_.velocity[1] > player_speed[1] else "down"
                sprites[S_BREAD].append(bread_)
            sfx["cannon"].play()
            self.timer = 500
        update_sprite(self)

    def update_duck(self: Sprite) -> None:
        nonlocal score

        if self.timer >= 0:
            self.timer -= clock.get_time()
        if self.mode == "full":
            self.feet_frame = 300
            self.costume = (self.timer // 100) % 3 + 1
            self.velocity = Vector2(self.flip_costume[0] * -4 + 2, 2)
        else:
            if self.mode == "hit":
                self.feet_frame = 300
                if self.timer < 0:
                    self.mode = "land"
                else:
                    self.costume = (self.timer // 100) % 3 + 1
            elif self.mode == "land":
                if self.timer < 0:
                    self.timer = randint(750, 1250)
                    self.velocity += Vector2(randint(-3, 3) * duck_speed, 0)
                    self.flip_costume[0] = self.velocity[0] < 0
                if self.velocity.length() > 0.05:
                    self.feet_frame += clock.get_time()
                    self.feet_frame %= 300
                else:
                    self.feet_frame = 0
            if self.colliding(player_sprite, player_tracks):
                if self.mode != "hit":
                    sfx["quack3"].play()
                if self.mode != "hit":
                    score += 1
                self.mode = "hit"
                self.timer = 1000
                self.velocity[0] += copysign(player_speed[1], self.position.x - player_sprite.position.x)
                self.position += self.velocity
        for obstacle in sprites[S_OBSTACLE] + sprites[S_LOAF] + sprites[S_DUCK]:
            if obstacle is not self and self.colliding(obstacle):
                self.velocity += (self.position - obstacle.position) / 100
        update_sprite(self)

    def update_obstacle(self: Sprite) -> None:
        if self.mode == "vehicle":
            self.velocity[0] = 0.25 * (1 - (self.flip_costume[0] * 2))
        if player_sprite.mode != "gameover" and self.colliding(player_sprite, player_tracks):
            player_sprite.timer = 1000
            player_sprite.mode = "gameover"
            player_speed[1] = 0
            sfx["gameover"].play()
        update_sprite(self)

    def update_road(self: Sprite) -> None:
        self.timer -= clock.get_time()
        if self.timer <= 0:
            self.timer = randint(11, 20) * 100

            s = Sprite(S_OBSTACLE, [sprite_sheet.subsurface(0, 96, 32, 16), sprite_sheet.subsurface(32, 96, 32, 16)],
                       Vector2(self.position), update_obstacle)
            s.mode, s.costume = "vehicle", randint(0, 1)
            if randint(0, 1):
                s.flip_horizontally()
            s.position[0] = (RESOLUTION + 32) * (s.flip_costume[0] - 0.5)
            sprites[s.sprite_type].insert(0, s)

        update_sprite(self)

    def update_decorator(self: Sprite) -> None:
        if level == 2:
            if self.timer is None:
                self.timer = 0
            self.timer += clock.get_time()
            self.costume = (self.timer // 100) % 4
        elif self.mode == "crushed" and self.timer is not None:
            self.timer += clock.get_time()
            if self.mode == "crushed" and self.timer >= 200:
                self.timer = None
                self.costume = 3
            else:
                self.costume = 2
        elif self.mode != "crushed":
            for entity in sprites[S_DUCK] + sprites[S_PLAYER]:
                if self.colliding(entity) and entity.mode != "full":
                    self.timer = 0
                    self.mode = "crushed"
                    sfx[("grass1", "grass2")[randint(0, 1)]].play()
        update_sprite(self)

    player_sprite = Sprite(S_PLAYER, [sprite_sheet.subsurface(0, 0, 16, 16),
                                      sprite_sheet.subsurface(16, 0, 16, 16)], Vector2(0, 8), update_player)
    player_tracks = Sprite(S_PLAYER,
                           [sprite_sheet.subsurface(32, 0, 16, 8), sprite_sheet.subsurface(48, 0, 16, 8),
                            sprite_sheet.subsurface(32, 8, 16, 8), sprite_sheet.subsurface(48, 8, 16, 8)],
                           player_sprite.position, update_tracks)
    player_tracks.timer = 0
    aim = Vector2(0, 1)
    road_img = Surface((RESOLUTION, 16))
    road_sheet = sprite_sheet.subsurface(0, 64, 16, 16)
    for road_x in range(0, RESOLUTION, 16):
        road_img.blit(road_sheet, (road_x, 0))
    del road_sheet
    decorators = (((0, 128, 8, 8), (8, 128, 8, 8), (0, 136, 8, 8), (8, 136, 8, 8)),
                  ((16, 128, 8, 8), (24, 128, 8, 8), (16, 136, 8, 8), (24, 136, 8, 8)),
                  ((0, 128, 8, 8), (8, 128, 8, 8), (0, 136, 8, 8), (8, 136, 8, 8)))
    obstacles = (((32, 48, 16, 32), (0, 80, 32, 16), (32, 80, 16, 16), (48, 80, 16, 16)),
                 ((32, 128, 16, 16), (0, 112, 32, 16), (32, 112, 32, 16)),
                 ((48, 48, 16, 16), (48, 64, 16, 16), (32, 48, 16, 32), (32, 80, 16, 16)))
    feet = (sprite_sheet.subsurface(48, 32, 8, 8), sprite_sheet.subsurface(56, 32, 8, 8),
            sprite_sheet.subsurface(48, 40, 8, 8), sprite_sheet.subsurface(56, 40, 8, 8))

    # automatically reset variables
    level = 0
    pause = False
    sprites: List[List[Sprite]] = []
    last_score = ""
    score_i = 0
    score = 0
    ammo = 0
    player_y = 0
    player_last_y = 0
    player_total_y = 0
    duck_speed = 0

    # reset variables
    new_mode = ""
    old_mode = ""
    level_lengths = (400, 500, 600)
    total_length = sum(level_lengths) + RESOLUTION * len(level_lengths)
    leaderboard_timer = 10000
    score_timer = 0
    anim_timer = 5000
    total_time = 0
    transition1 = Surface((0, 0))
    transition2 = Surface((0, 0))
    background = Surface((RESOLUTION, RESOLUTION))
    trans_dir = 1
    mode = "logo"
    clock = time.Clock()
    event_keyboard = []
    movement = Vector2(0, 0)
    player_speed = Vector2(0, 0)
    last_aim = Vector2(0, 0)
    while mode != "quit":
        #  get user input
        quick_keys.update()
        if ui is not quick_keys:
            ui.update()
        event_keyboard.clear()
        movement.update(0, 0)
        if quick_keys.pressed("Escape"):
            mode = "quit"
        else:
            for e in event.get():
                if e.type == QUIT:
                    mode = "quit"
                    break
                elif e.type == KEYDOWN:
                    event_keyboard.append(e.key)
                    if score_name is not None:
                        if e.key == K_BACKSPACE:
                            score_name = score_name[:-1]
                        elif e.unicode.isalpha() or e.unicode in "-_":
                            score_name += e.unicode.capitalize()
                elif e.type == MOUSEMOTION:
                    movement.update(e.rel)
        if mode != "quit":
            if not IS_WEB:
                if quick_keys.tapped("F10"):
                    reset_screen()
                if quick_keys.tapped("F11"):
                    fullscreen()

            # run program
            fps = clock.get_fps()
            if mode == "start":
                if quick_keys.any(event_keyboard, movement):
                    leaderboard_timer = 10000
                else:
                    leaderboard_timer -= clock.get_time()
                    if leaderboard_timer <= 0:
                        mode = "leaderboard"
            elif mode == "keybinds":
                ui_any = ui.any(event_keyboard, movement, keybind_types[keybind_selected])
                if keybind_select == 1 and ui_any is None:
                    keybind_select = 2
                elif (keybind_select == 2 and ui_any is not None
                      and ui_any not in tuple(quick_keys.key_binds.values())[:3]):
                    ui.key_binds[list(ui.key_binds.keys())[keybind_selected + QUICK_KEYBINDS]] = ui_any
                    keybind_select = 3
                elif keybind_select == 3 and ui_any is None:
                    keybind_select = 0
            elif mode == "play":
                if quick_keys.tapped("Menu") or (IS_MOBILE and quick_keys.tapped("Click") and mobile_box[2].collidepoint(quick_keys.current[2])):
                    pause = not pause
                if not pause:
                    if fps > 0:
                        add = player_speed[1] * 128 / fps
                        player_y += add
                        player_total_y += add
                        if player_y > (level_lengths[level - 1]) * 16 + RESOLUTION * 1.5:
                            mode = "levelup"
                            level += 1
                            reset_level()
                            sfx["levelup"].play()
                        else:
                            while player_y - player_last_y >= 16:
                                player_last_y += 16
                                if player_last_y <= (level_lengths[level - 1]) * 16 + RESOLUTION * 0.5:
                                    world_load()
                    aim_init = ui.get_cursor("Aim", player_sprite.position + Vector2(0, 8), bar_mode)
                    if aim_init != (0, 0):
                        aim.update(aim_init)
                    del aim_init
                    if ui.tapped("Throw") and not (player_sprite.mode == "gameover" or (IS_MOBILE and any([i.collidepoint(quick_keys.current[2]) for i in mobile_box]))):
                        if ammo == 0:
                            sfx["error"].play()
                        else:
                            player_sprite.costume = int(aim[0] < 0)
                            ammo -= 1
                            bread = Sprite(1, [sprite_sheet.subsurface(0, 32, 16, 16)],
                                           Vector2(player_sprite.position) + Vector2(0, 4),
                                           update_bread)
                            bread.flip_costume = [aim[0] < 0, False]
                            bread.sprite_type, bread.velocity = S_BREAD, Vector2(aim) * 1.5 + player_speed
                            bread.mode = "up" if bread.velocity[1] > player_speed[1] else "down"
                            sprites[S_BREAD].append(bread)

            # update user output
            update()
            update_sound()
            clock.tick(60)
            await asyncio.sleep(0)
    if IS_WEB:
        await main()


asyncio.run(main())
