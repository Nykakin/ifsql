from ifsql import analyse
from ifsql import database
from ifsql import parser

class Cmd:
    def __init__(self, root):
        self._database = Database()
        self._parser = Parser()
        self._path_id_cache = {}

        analyse.walk(root, self._database, self._path_id_cache)
