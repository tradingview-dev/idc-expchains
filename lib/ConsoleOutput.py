import enum
import os
import sys
from typing import Callable, overload


class ConsoleOutput:
    """
    A Simple Logger
    """

    class Foreground(enum.StrEnum):

        def __add__(self, other: str):
            return self.value + other

        def __radd__(self, other: str):
            return other + self.value

        REGULAR_RED = '\033[0;31m'
        REGULAR_GREEN = '\033[0;32m'
        REGULAR_YELLOW = '\033[0;33m'
        REGULAR_BLUE = '\033[0;34m'

        BOLD_RED = '\033[1;31m'
        BOLD_GREEN = '\033[1;32m'
        BOLD_YELLOW = '\033[1;33m'
        BOLD_BLUE = '\033[1;34m'

        REGULAR_BRIGHT_RED = '\033[0;91m'
        REGULAR_BRIGHT_GREEN = '\033[0;92m'
        REGULAR_BRIGHT_YELLOW = '\033[0;93m'
        REGULAR_BRIGHT_BLUE = '\033[0;94m'

        BOLD_BRIGHT_RED = '\033[1;91m'
        BOLD_BRIGHT_GREEN = '\033[1;92m'
        BOLD_BRIGHT_YELLOW = '\033[1;93m'
        BOLD_BRIGHT_BLUE = '\033[1;94m'

        DEFAULT = '\033[39m'

        BOLD = '\033[1m'
        RESET = '\033[0m'

    # private static consts
    __BACKGROUND_BLACK = '\033[40m'
    __BACKGROUND_RED = '\033[41m'
    __BACKGROUND_GREEN = '\033[42m'
    __BACKGROUND_WHITE = '\033[47m'
    __BACKGROUND_DEFAULT = '\033[49m'

    def __init__(self, name: str):
        super().__init__()
        # protected non-static variables
        self._name = name
        self._waiting_eol = False

    def debug(self, message: str) -> None:
        msg = '\n' if self._waiting_eol else '' + f"[DEBUG] {self._name} - {message}"
        self._waiting_eol = False
        print(ConsoleOutput.Foreground.REGULAR_BLUE + msg + ConsoleOutput.Foreground.RESET)

    def info(self, message: str, eol=True, color: Foreground = Foreground.RESET) -> None:
        msg = message if self._waiting_eol else f"[INFO] {self._name} - {message}"
        self._waiting_eol = not eol
        print(color + msg + ConsoleOutput.Foreground.RESET if color else msg, end='\n' if eol else '')

    def weak_warn(self, message: str) -> None:
        msg = '\n' if self._waiting_eol else '' + f"[WEAK_WARN] {self._name} - {message}"
        self._waiting_eol = False
        print(ConsoleOutput.Foreground.REGULAR_YELLOW + msg + ConsoleOutput.Foreground.RESET)

    def warn(self, message: str) -> None:
        msg = '\n' if self._waiting_eol else '' + f"[WARN] {self._name} - {message}"
        self._waiting_eol = False
        print(ConsoleOutput.Foreground.BOLD_BRIGHT_YELLOW + msg + ConsoleOutput.Foreground.RESET)

    @overload
    def error(self, exception: Exception) -> None: ...

    @overload
    def error(self, exception: str) -> None: ...

    def error(self, exception: Exception | str) -> None:
        caused_in = self._find_cause_issuer(sys.exc_info(), self._name)
        reason = str(exception)
        if isinstance(exception, Exception) and len(exception.args) > 1 and isinstance(exception.args[1], Exception):
            reason = f"<{type(exception).__name__}> {' '.join(ConsoleOutput.unwind_exception(exception))}"
        msg = '\n' if self._waiting_eol else '' + f"[ERROR] {caused_in} - {reason}"
        self._waiting_eol = False
        print(ConsoleOutput.Foreground.BOLD_BRIGHT_RED + msg + ConsoleOutput.Foreground.RESET, flush=True)

    def fatal(self, message: str) -> None:
        msg = '\n' if self._waiting_eol else '' + f"[FATAL] {self._name} - {message}"
        self._waiting_eol = False
        print(ConsoleOutput.__BACKGROUND_RED + ConsoleOutput.Foreground.BOLD + msg +
              ConsoleOutput.__BACKGROUND_DEFAULT + ConsoleOutput.Foreground.RESET, flush=True)

    def log(self, msg: str, func: Callable, *args) -> None:
        """

        :param msg:
        :param func:
        :param args:
        :return:
        :raise Exception:
        """
        self.info(msg, False)
        try:
            func(*args)
        except Exception as e:
            self.info("FAIL", True, ConsoleOutput.Foreground.REGULAR_RED)
            raise e
        else:
            self.info("OK", True, ConsoleOutput.Foreground.REGULAR_GREEN)

    @staticmethod
    def unwind_exception(e: Exception) -> list[str]:
        messages = []
        if len(e.args) > 1 and isinstance(e.args[1], Exception):
            messages += ConsoleOutput.unwind_exception(e.args[1])
        messages.append(e.args[0])
        return messages

    @staticmethod
    def _find_cause_issuer(exc_info, default: str):
        caused_in = default
        if len(exc_info) > 2 and exc_info[2]:
            tb = exc_info[2]
            while tb.tb_next is not None:
                tb = tb.tb_next
            caused_in = f"{os.path.basename(tb.tb_frame.f_code.co_filename)}:{tb.tb_frame.f_lineno}"
        return caused_in