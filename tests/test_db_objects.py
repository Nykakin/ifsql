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


def test_relations(filesystem, database):
    import os
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}
    ifsql.analyse.walk(filesystem, database, path_id_cache)

    relations = database.relations.all()

    filesystem_id = path_id_cache["."]
    subdir1_id = path_id_cache[os.path.join(filesystem, "subdir1")]
    subdir2_id = path_id_cache[os.path.join(filesystem, "subdir1/subdir2")]
    test_file_id = database.files.filter(ifsql.database.File.file_name=="test_file").first().file_id

    expected_relations = (
        (filesystem_id, filesystem_id, 0),
        (subdir1_id, subdir1_id, 0),
        (filesystem_id, subdir1_id, 1),
        (subdir2_id, subdir2_id, 0),
        (subdir1_id, subdir2_id, 1),
        (filesystem_id, subdir2_id, 2),
        (test_file_id, test_file_id, 0),
        (subdir2_id, test_file_id, 1),
        (subdir1_id, test_file_id, 2),
        (filesystem_id, test_file_id, 3),
    )

    for i, relation in enumerate(relations):
        expected_relation = ifsql.database.Relation(
            ancestor_id=expected_relations[i][0],
            descendant_id=expected_relations[i][1],
            path_length=expected_relations[i][2],
        )
        assert expected_relation == relation
