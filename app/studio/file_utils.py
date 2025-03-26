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
    def read_dict(file_name: str) -> dict:
        with open(file_name, 'rt', encoding='utf-8-sig') as file:
            content = file.read()
            return json.loads(content)

    @staticmethod
    def listdir(dir_name: str) -> [str]:
        file_names = []
        for _, _, files in os.walk(dir_name):
            file_names.extend(files)
        return file_names
