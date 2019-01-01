import os
import tempfile

import pytest


class MockFilesystem:
    def __init__(self):
        self.root = tempfile.mkdtemp()

    def add_directory(self, path):
        full_path = os.path.join(self.root, path)
        os.makedirs(full_path)

    def add_file(self, path, size):
        full_path = os.path.join(self.root, path)
    
        with open(full_path, "wb") as f:
            f.write((0).to_bytes(size, "big"))


def test_select_all_items(database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs = MockFilesystem()
    fs.add_file(path="file1", size=100)
    fs.add_file(path="file2", size=200)
    fs.add_file(path="file3", size=300)
    fs.add_file(path="file4", size=400)
    fs.add_file(path="file5", size=500)
    
    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM .")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 6
    assert sorted(r.file_name for r in result) == [".", "file1", "file2", "file3", "file4", "file5"]


def test_select_all_files(database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs = MockFilesystem()
    fs.add_file(path="file1", size=100)
    fs.add_file(path="file2", size=200)
    fs.add_file(path="file3", size=300)
    fs.add_file(path="file4", size=400)
    fs.add_file(path="file5", size=500)
    
    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM . WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 5
    assert sorted(r.file_name for r in result) == ["file1", "file2", "file3", "file4", "file5"]


def test_select_one_file(database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs = MockFilesystem()
    fs.add_file(path="file1", size=100)
    fs.add_file(path="file2", size=200)
    fs.add_file(path="file3", size=300)
    fs.add_file(path="file4", size=400)
    fs.add_file(path="file5", size=500)
    
    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM . WHERE file_name = 'file1'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name == 'file1'
