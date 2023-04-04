"""A generator that fakes a read from a file."""
import asyncio
import logging

import aiohttp

from config import LIST_FILE_REPO, RAW_FILE
from rep import build_dirs, create_path_to_load_files, get_hash, save_file
from run_queue import run_queue


class ExceptionLoadError(Exception):
    """Исключение возникает если файлы не найдены."""

    def __init__(self, unloaded_files):
        """Создание исключения."""
        message = ','.join(map(str, unloaded_files))
        self.message = "D'nt load files {msg}".format(msg=message)

    def __str__(self):
        """Представление в виде строки."""
        return self.message


async def get_request(url, mode='json'):
    """Выполнить асинхронный запрос.

    Args:
        url: string
            Путь запроса.
        mode: string
            Тип получаемых данных. М/б json или поток битов

    Returns:
        json: список файлов в директории
        file: загруженный файл
    """
    async with aiohttp.ClientSession(trust_env=True) as session:
        succses_request = 200
        async with session.get(url) as response:
            if response.status == succses_request:
                if mode == 'json':
                    return await response.json()
                return await response.read()


async def create_file_downloader(begin_url_file, path_to_save):
    """Создает функцию для загрузки файла.

    Передает в нее начало url пути для скачивания,
    путь временной папки куда сохранять файлы

    Args:
        begin_url_file: string
            Начало url пути для скачивания.
        path_to_save: string
            Путь временной папки куда сохранять файлы.

    Returns:
        function: функция загрузки файла
    """
    async def factory(title_file):
        """Скачивает и сохраняет файл.

        Args:
            title_file: string
                Flask for functionaly testing.
        """
        path_to_file = begin_url_file + title_file
        file_for_save = await get_request(path_to_file, 'read')
        save_file(file_for_save, path_to_save, title_file)
    return factory


async def load_repo(repo, path_to_load):
    """
    Сохраняет файлы репозитория repo в каталог path_to_load.

    Args:
        repo: string
            Репозиторий из которого сохраняют файлы.
        path_to_load: string
            Каталог для сохранения.

    Returns:
            list Список путей загруженных файлов.
    """
    list_files_repo = await get_request(repo + LIST_FILE_REPO)
    build_dirs(path_to_load, list_files_repo)
    downloader = await create_file_downloader(repo + RAW_FILE, path_to_load)
    await run_queue(list_files_repo, downloader, 3)
    return create_path_to_load_files(list_files_repo)


def get_hash_files(path_to_load, list_load_file):
    """
    Возвращает хэш каждого файла из каталога.

    Args:
        path_to_load: string
            Путь каталога в котором считают хэши.
        list_load_file: set[Path]
            список путей для которых считается хеш.

    Returns:
        dict Словарь {путь_до_файла: хэш_файла}

    Raises:
        ExceptionLoadError: Вызывает исключение если не все файлы сохранены.
    """
    unloaded_files = []
    dict_files_hashes = {}
    for path in list_load_file:
        hash_file = get_hash(path_to_load, path)
        if hash_file:
            dict_files_hashes[str(path)] = hash_file
            continue
        unloaded_files.append(path)
    if unloaded_files:
        raise ExceptionLoadError(unloaded_files)
    return dict_files_hashes


if __name__ == '__main__':
    url_repo = 'https://gitea.radium.group/radium/project-configuration'
    path_to_load = 'temp4'
    list_load_files = asyncio.run(load_repo(url_repo, path_to_load))
    logging.basicConfig(level=logging.INFO)
    logging.info(get_hash_files(path_to_load, list_load_files))
