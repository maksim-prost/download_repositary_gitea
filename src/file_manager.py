"""Модуль работы с файловой системой."""
import hashlib
from pathlib import Path


def create_path_to_load_files(list_files_repo):
    """
    Создает список путей из списка загруженных файлов.

    Args:
        list_files_repo: list
            Список загруженных файлов.

    Returns:
        list список путей.
    """
    return {Path(path_file) for path_file in list_files_repo}


def save_file(bit_stream, folder, title_file):
    """
    Сохраняет поток битов по указоному путю.

    Args:
        bit_stream: file
            Сохраняемый поток битов.
        folder:  string
            Путь к временной папке,
            в которой происходит сохранение файлов.
        title_file: string
            Путь к файлу, внутри folder.

    """
    (Path(folder) / title_file).write_bytes(bit_stream)


def build_dirs(path_to_load, list_files):
    """Создает каталоги для сохранения файлов репозитория.

    Args:
        path_to_load: string
            Путь к каталогу для сохранения.
        list_files: list
            Список путей файлов, для сохранения.
    """
    for title_path in list_files:
        cur_dir = path_to_load / Path(title_path).parent
        cur_dir.mkdir(parents=True, exist_ok=True)


def get_hash(parent_dir, path: Path):
    """
    Получает хеш файла.

    Args:
        parent_dir: string
            Parent dir.
        path: Path
            Load file.

    Returns:
        string: hexdigest
    """
    try:
        stream_bytes = (parent_dir / path).read_bytes()
    except OSError:
        return None
    hsh = hashlib.sha256()
    hsh.update(stream_bytes)
    return hsh.hexdigest()
