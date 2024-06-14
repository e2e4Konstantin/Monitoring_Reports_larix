import os
import pathlib




def construct_absolute_file_path(directory_path: str, file_name: str) -> str | None:
    """Создает абсолютный путь к файлу."""
    if directory_path and file_name and isinstance(directory_path, str) and isinstance(file_name, str):
        return os.path.join(directory_path, file_name)
    return None

def create_abspath_file(path: str=None, file_name: str=None) -> str | None:
    """ Создает абсолютный маршрут к файлу. Если путь не указан то берется место запуска."""
    if file_name:
        path = pathlib.Path(path).resolve() if path else pathlib.Path(__file__).parent.resolve()
        return pathlib.Path.joinpath(path, file_name).__str__()
    return None


def does_file_exist(file_path: str) -> bool:
    """Проверяет, существует ли заданный путь и является ли он файлом."""
    return pathlib.Path(file_path).exists() and pathlib.Path(file_path).is_file()


def is_file_in_use(file_path: str) -> bool:
    """Проверьте, не используется ли файл другим приложением."""
    if os.path.exists(file_path):
        if not os.access(file_path, os.W_OK):
            return True
        # try:
        #     os.rename(file_path, file_path)  # if not os.access(file_path, os.W_OK):
        # except OSError:
        #     return True
    return False


def generate_result_file_name(file_path: str, supplement: int, index: int) -> str:
    """Добавляет к имени файла номер дополнения и индекса."""
    file_path = pathlib.Path(file_path)
    new_name = f"{file_path.stem}_{supplement}_{index}"
    return str(file_path.with_name(new_name).with_suffix(file_path.suffix))
