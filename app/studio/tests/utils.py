import os

from studio.file_utils import FileUtils


class TestUtils:
    @staticmethod
    def get_test_dir() -> str:
        filepath = os.path.realpath(__file__)
        return os.path.dirname(filepath)

    @staticmethod
    def get_data_path(file_name: str = '', sub_dir: str = '') -> str:
        return FileUtils.join_path(TestUtils.get_test_dir(), 'data', sub_dir, file_name)
