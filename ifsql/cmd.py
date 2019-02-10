from ifsql import analyse
from ifsql import database
from ifsql import parser


class Cmd:
    def __init__(self, root):
        self._database = Database()
        self._parser = Parser()
        self._path_id_cache = {}

        analyse.walk(root, self._database, self._path_id_cache)

    def query(self, input_query):
        s = self._parser.parse(input_query)
        path = s.froms[0].name
        s._from_obj.clear()
        s = s.select_from(table("another_table"))

        print(s)
