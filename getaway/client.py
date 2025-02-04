from .config import *
from .activity import *
from .info import *
import threading
from collections import deque
import posixpath
import os
from PIL import Image, ImageTk

__all__ = ['Client']


class Client(object):

    def __init__(self, player_name):
        self._canvas_img = {}
        self._timer_count = {}

        self._act = Activity()
        self._player_name = player_name
        self._player_info = Info()

        self._pos_pool = deque(['none'] * 21)

        self._zoom_mode = False
        self._gun_walk_loop_id = 1

    @staticmethod
    def play_sound(sound_path):
        def __os_system(sound_path_):
            os.system('play ' + sound_path_)

        threading.Thread(target=__os_system, args=(sound_path,)).start()

    def add_image(self, keyword, x, y, filename, timer=5):
        img = Image.open(filename).convert('RGBA')
        img = img.resize((200, 200), Image.ANTIALIAS)
        self._canvas_img[keyword] = (x, y, img)
        self._timer_count[keyword] = timer

    def remove_image(self, keyword):
        self._canvas_img.pop(keyword, None)

    def write_camera_image(self, img):
        emoji, pos = self._act.read_pos_emoji(img)
        self._player_info.set_friend_avatars(self._player_name, emoji)
        self.__add_pos(pos)

    def __add_pos(self, pos):
        if len(self._pos_pool) >= 21:
            self._pos_pool.popleft()
        self._pos_pool.append(pos)

    def query_pos(self):
        lst = list(self._pos_pool)
        if lst.count('forward') > 5:
            self._zoom_mode = True
            return 'forward'
        elif lst.count('down_left') > 5:
            self._zoom_mode = False
            return 'down_left'
        elif lst.count('down_right') > 5:
            self._zoom_mode = False
            return 'down_right'
        elif lst.count('turn_left') > 15:
            self._zoom_mode = False
            return 'turn_left'
        elif lst.count('turn_right') > 15:
            self._zoom_mode = False
            return 'turn_right'
        else:
            self._zoom_mode = False
            return 'none'

    def refresh(self):
        self._gun_walk_loop_id += 1
        if self._gun_walk_loop_id > 18:
            self._gun_walk_loop_id = 1

        tmp_timer_count = self._timer_count.copy()
        for keyword, val in tmp_timer_count.items():
            self._timer_count[keyword] -= 1
            if self._timer_count[keyword] == 0:
                self._timer_count.pop(keyword, None)
                self._canvas_img.pop(keyword, None)

    @property
    def zoom_mode(self):
        return self._zoom_mode

    @property
    def gun_walk_loop_id(self):
        return self._gun_walk_loop_id

    @property
    def canvas_img(self):
        return self._canvas_img

    @property
    def friend_avatars(self):
        return self._player_info.friend_avatars

    @property
    def enemy_avatars(self):
        return self._player_info.enemy_avatars

    @property
    def friend_names(self):
        return self._player_info.friend_names

    @property
    def enemy_names(self):
        return self._player_info.enemy_names
