"""Тестирование модуля загрузки репозитория."""
import hashlib
import shutil
import unittest
from pathlib import Path

from config import LIST_FILE_REPO
from file_manager import create_path_to_load_files, get_hash, save_file
from get_hashs_files_repository import (
    ExceptionLoadError,
    get_hash_files,
    get_request,
    load_repo,
)

URL_REPOSITORY = 'https://gitea.radium.group/radium/project-configuration'


def get_hash_string(string):
    """Получить хеш строки."""
    hsh = hashlib.sha256()
    hsh.update(str.encode(string))
    return hsh.hexdigest()


class TestLoad(unittest.IsolatedAsyncioTestCase):
    """Тестирование модуля load_repo."""

    def setUp(self):
        """Настройка перед выполнения теста."""
        self.repository = URL_REPOSITORY
        self.temporary_dir = 'temporary_dir'
        Path(self.temporary_dir).mkdir(exist_ok=True)

    async def test_load(self):
        """Тестирование функции load."""
        list_load_files = {
            self.temporary_dir / path
            for path in (await load_repo(self.repository, self.temporary_dir))
        }
        list_files = {
            path
            for path in Path(self.temporary_dir).rglob('*')
            if path.is_file()
        }
        self.assertEqual(list_load_files, list_files)

    def test_get_hash_files(self):
        """
        Тестирование функции get_hash_files.

        На возбуждение исключения и
        создание хеша.
        """
        list_files = [Path('test_1'), Path('test_2')]
        self.assertRaises(
            ExceptionLoadError,
            get_hash_files,
            self.temporary_dir,
            list_files,
        )
        hashes_files = {}
        for temporary_path in list_files:
            text_file = 'SOme Test Text {path}'.format(path=temporary_path)
            (self.temporary_dir / temporary_path).write_text(text_file)
            hashes_files[str(temporary_path)] = get_hash_string(text_file)

        creating_hash = get_hash_files(self.temporary_dir, list_files)
        self.assertEqual(creating_hash, hashes_files)

    async def test_get_request(self):
        """Тестирование функции get_request."""
        files_repository = [
            'LICENSE',
            'README.md',
            'nitpick/all.toml',
            'nitpick/darglint.toml',
            'nitpick/editorconfig.toml',
            'nitpick/file-structure.toml',
            'nitpick/flake8.toml',
            'nitpick/isort.toml',
            'nitpick/pytest.toml',
            'nitpick/styleguide.toml',
        ]
        load_files = await get_request(self.repository + LIST_FILE_REPO)
        self.assertListEqual(load_files, files_repository)

    def tearDown(self):
        """Настройка после выполнения теста."""
        shutil.rmtree(self.temporary_dir)


class TestRep(unittest.TestCase):
    """Тестирование модуля load_repo."""

    def setUp(self):
        """Настройка перед выполнения теста."""
        self.repository = URL_REPOSITORY
        self.temporary_dir = 'temporary_dir'
        Path(self.temporary_dir).mkdir(exist_ok=True)

    def test_create_path_to_load_files(self):
        """Тестирование функции create_path_to_load_files."""
        list_files = ['test1', 'test2']
        list_path = {Path(title_file) for title_file in list_files}
        self.assertEqual(create_path_to_load_files(list_files), list_path)

    def test_save_file(self):
        """Тестирование функции save_file."""
        byte_stream = str.encode('Тестовый поток битов')
        title_file = 'temporary_file.bytes'
        save_file(byte_stream, self.temporary_dir, title_file)
        test_byte_stream = (Path(self.temporary_dir) / title_file).read_bytes()
        self.assertEqual(byte_stream, test_byte_stream)

    def test_get_hash(self):
        """Тестирование функции get_hash."""
        path = Path('test_file')
        hash_file = get_hash(self.temporary_dir, path)
        self.assertIsNone(hash_file)

        test_text = 'Тестовый поток битов'
        (self.temporary_dir / path).write_bytes(str.encode(test_text))
        hash_file = get_hash(self.temporary_dir, path)
        self.assertEqual(hash_file, get_hash_string(test_text))

    def tearDown(self):
        """Настройка после выполнения теста."""
        shutil.rmtree(self.temporary_dir)


# Executing the tests in the above test case class
if __name__ == '__main__':
    unittest.main()
