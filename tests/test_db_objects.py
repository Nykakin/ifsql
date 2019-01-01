import pytest


@pytest.fixture
def filesystem():
    import os
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    full_path = os.path.join(tmp_dir, "subdir1/subdir2")
    os.makedirs(full_path)
    with open(os.path.join(full_path, "test_file"), "wb") as f:
        f.write((0).to_bytes(8196, "big"))

    return tmp_dir


def test_files(filesystem, database):
    import datetime
    import os
    import os.path
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}
    ifsql.analyse.walk(filesystem, database, path_id_cache)
    files = database.files.all()

    paths = (
        (filesystem, "."),
        (filesystem, "subdir1"),
        (os.path.join(filesystem, "subdir1"), "subdir2"),
        (os.path.join(filesystem, "subdir1/subdir2"), "test_file"),
    )

    for i, (file_path, file_name) in enumerate(paths):
        path = os.path.join(file_path, file_name)

        assert files[i].owner_id == os.getuid()
        assert files[i].group_id == os.getgid()
        assert files[i].file_path == file_path
        assert files[i].file_name == file_name
        assert datetime.datetime.now() - files[i].access_time < datetime.timedelta(
            seconds=1
        )
        assert datetime.datetime.now() - files[
            i
        ].modification_time < datetime.timedelta(seconds=1)

        if os.path.isfile(path):
            assert files[i].file_size == 8196
            assert files[i].file_type == "F"
        else:
            assert files[i].file_type == "D"


def test_relations(fs, database):
    import ifsql.database
    import ifsql.analyse

    fs.add_directory("subdir1")
    fs.add_directory("subdir2")
    fs.add_directory("subdir2/subdir3")
    fs.add_file(path="file1", size=100)
    fs.add_file(path="subdir1/file2", size=200)
    fs.add_file(path="subdir1/file3", size=300)
    fs.add_file(path="subdir2/file4", size=400)
    fs.add_file(path="subdir2/subdir3/file5", size=500)

    path_id_cache = {}
    ifsql.analyse.walk(fs.root, database, path_id_cache)

    file_map = {f.file_name: f.file_id for f in database.files.all()}

    expected_relations = (
        # .
        (file_map["."], file_map["."], 0),
        # file1
        (file_map["file1"], file_map["file1"], 0),
        (file_map["."], file_map["file1"], 1),
        # subdir1
        (file_map["subdir1"], file_map["subdir1"], 0),
        (file_map["."], file_map["subdir1"], 1),
        # subdir2
        (file_map["subdir2"], file_map["subdir2"], 0),
        (file_map["."], file_map["subdir2"], 1),
        # file2
        (file_map["file2"], file_map["file2"], 0),
        (file_map["subdir1"], file_map["file2"], 1),
        (file_map["."], file_map["file2"], 2),
        # file3
        (file_map["file3"], file_map["file3"], 0),
        (file_map["subdir1"], file_map["file3"], 1),
        (file_map["."], file_map["file3"], 2),
        # file4
        (file_map["file4"], file_map["file4"], 0),
        (file_map["subdir2"], file_map["file4"], 1),
        (file_map["."], file_map["file4"], 2),
        # subdir3
        (file_map["subdir3"], file_map["subdir3"], 0),
        (file_map["subdir2"], file_map["subdir3"], 1),
        (file_map["."], file_map["subdir3"], 2),
        # file5
        (file_map["file5"], file_map["file5"], 0),
        (file_map["subdir3"], file_map["file5"], 1),
        (file_map["subdir2"], file_map["file5"], 2),
        (file_map["."], file_map["file5"], 3),
    )

    relations = database.relations.all()
    assert len(relations) == len(expected_relations)
    for i, relation in enumerate(relations):
        expected_relation = ifsql.database.Relation(
            ancestor_id=expected_relations[i][0],
            descendant_id=expected_relations[i][1],
            path_length=expected_relations[i][2],
        )
        assert expected_relation == relation
