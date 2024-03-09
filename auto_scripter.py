import platform
from dataclasses import dataclass
import pynput as pn
from typing import Callable, Optional
from pynput.keyboard import Listener
from repeated_timer import RepeatedTimer


@dataclass
class Register:
    keys: frozenset[pn.keyboard.Key]
    callback: Callable[[], None]
    repeat: Optional[float]
    exclusive_keys: bool


class AutoScripter:
    __machine_name: str
    __on_press_registers: list[Register]
    __listener: Listener
    __timers: dict[set[pn.keyboard.Key], RepeatedTimer]
    __current_pressed_keys: set[pn.keyboard.Key]

    def __init__(self):
        self.__machine_name = platform.node()
        self.__on_press_registers = []
        self.__timers = {}
        self.__current_pressed_keys = set()

    def register_key_on_press(self, key: pn.keyboard.Key | set[pn.keyboard.Key], callback: Callable[[], None],
                              exclusive_keys: bool = True):
        self.register_key_on_press_repeatedly(key, callback, every_seconds=None, exclusive_keys=exclusive_keys)

    def register_key_on_press_repeatedly(self, key: pn.keyboard.Key | set[pn.keyboard.Key], callback: Callable[[], None],
                                         every_seconds: Optional[float], exclusive_keys: bool = True):
        keys = key if type(key) is set else {key}
        register = Register(keys=frozenset(keys), callback=callback,
                            repeat=every_seconds, exclusive_keys=exclusive_keys)
        self.__on_press_registers.append(register)

    def __find_keys(self, keys: frozenset[pn.keyboard.Key]) -> list[Register]:
        result = []
        for register in self.__on_press_registers:
            if register.exclusive_keys:
                if register.keys == keys:
                    result.append(register)
            else:
                if register.keys.issubset(keys):
                    result.append(register)
        return result

    def __on_press(self, key):
        self.__current_pressed_keys.add(key)
        print("Pressed keys: {}".format(self.__current_pressed_keys))
        for register in self.__find_keys(frozenset(self.__current_pressed_keys)):
            if register.repeat is None:
                print("executing function for keys: {}".format(register.keys))
                register.callback()
            else:
                timer = self.__timers.get(key)
                if timer is not None:
                    print("stopping timer for keys: {}".format(register.keys))
                    timer.stop()
                    self.__timers.pop(key, None)
                else:
                    print("executing timer for keys: {}".format(register.keys))
                    self.__timers[key] = RepeatedTimer(register.repeat, register.callback)

    def __on_release(self, key):
        if key in self.__current_pressed_keys:
            self.__current_pressed_keys.remove(key)
        print("Pressed keys: {}".format(self.__current_pressed_keys))

    def reset(self):
        for timer in self.__timers.values():
            timer.stop()
        self.__timers.clear()
        self.__current_pressed_keys.clear()
        print("===> Class has been reset")

    def listen(self):
        self.__listener = pn.keyboard.Listener(on_press=self.__on_press, on_release=self.__on_release)
        self.__listener.start()
        self.__listener.join()
