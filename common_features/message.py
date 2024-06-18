import sys
from config import CONSOLE_COLORS


def output_message(error_message: str, additional_info: str = None) -> None:
    """ Выводит в консоль сообщение об ошибке. """
    error_color = CONSOLE_COLORS["RED"]
    reset_color = CONSOLE_COLORS["RESET"]
    print(f"{error_color}{error_message}{reset_color}")
    if additional_info:
        info_color = CONSOLE_COLORS["YELLOW"]
        print(f"{info_color}\t-->> {additional_info}{reset_color}")


def output_message_exit(text_red: str, text_yellow: str):
    """ Выводит в консоль сообщение об ошибке и завершает приложение. """
    output_message(text_red, text_yellow)
    sys.exit()

if __name__ == "__main__":
    output_message("red text", "yellow text")
    output_message_exit("red", "yellow")