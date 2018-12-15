import pytest


@pytest.fixture
def database():
    import sqlgrep.database

    return sqlgrep.database.Database()


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
    import sqlgrep.database

    database.walk(filesystem)
    files = database.files.all()

    paths = (
        filesystem,
        os.path.join(filesystem, "subdir1"),
        os.path.join(filesystem, "subdir1/subdir2"),
        os.path.join(filesystem, "subdir1/subdir2/test_file"),
    )

    for i, path in enumerate(paths):
        assert files[i].owner_id == os.getuid()
        assert files[i].group_id == os.getgid()
        assert files[i].file_name == path
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
    import sqlgrep.database

    database.walk(filesystem)
    relations = database.relations.all()

    filesystem_id = database.path_id(filesystem)
    subdir1_id = database.path_id(os.path.join(filesystem, "subdir1"))
    subdir2_id = database.path_id(os.path.join(filesystem, "subdir1/subdir2"))
    test_file_id = database.path_id(
        os.path.join(filesystem, "subdir1/subdir2/test_file")
    )

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
        expected_relation = sqlgrep.database.Relation(
            ancestor_id=expected_relations[i][0],
            descendant_id=expected_relations[i][1],
            path_length=expected_relations[i][2],
        )
        assert expected_relation == relation
