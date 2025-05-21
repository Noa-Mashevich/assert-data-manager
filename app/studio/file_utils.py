import json
import os


class FileUtils:
    @staticmethod
    def join_path(*paths) -> str:
        return FileUtils.clean_path(os.path.join(*paths))

    @staticmethod
    def clean_path(path: str) -> str:
        return path.replace('\\', '/')

    @staticmethod
    def read_content(file_name: str) -> str:
        with open(file_name, 'rt', encoding='utf-8-sig') as file:
            return file.read()

    @staticmethod
    def read_dict(file_name: str) -> dict:
        content = FileUtils.read_content(file_name)
        return json.loads(content)

    @staticmethod
    def listdir(dir_name: str) -> [str]:
        file_names = []
        for _, _, files in os.walk(dir_name):
            file_names.extend(files)
        return file_names

    @staticmethod
    def read_test_file_content(s3_key: str):
        current_path = os.path.realpath(__file__)
        test_path = os.path.realpath(FileUtils.join_path(current_path, '..', 'tests'))
        splits = s3_key.split('studio/')
        if len(splits) != 2:
            base_name = os.path.basename(s3_key)
        else:
            base_name = splits[1]
        file_path = FileUtils.join_path(test_path, 'data', base_name)
        try:
            return FileUtils.read_dict(file_path)
        except Exception:
            return {}
