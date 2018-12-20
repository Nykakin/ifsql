import pytest


@pytest.fixture
def filesystem():
    import os
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tree1 = os.path.join(tmp_dir, "tree1_subdir_1/tree1_subdir_2")
    tree2 = os.path.join(tmp_dir, "tree2_subdir_1/tree2_subdir_2")
    os.makedirs(tree1)
    os.makedirs(tree2)

    files = (
        ("tree1_subdir_1/file1", 2000),
        ("tree1_subdir_1/tree1_subdir_2/file2", 20),
        ("tree2_subdir_1/file3", 3000),
        ("tree2_subdir_1/tree2_subdir_2/file4", 1000),
    )
    for path, size in files:
        with open(os.path.join(tmp_dir, path), "wb") as f:
            f.write((0).to_bytes(size, "big"))

    return tmp_dir


def test_select_all(filesystem, database):
    database.walk(filesystem)

    database.query("SELECT file_name, file_size from .")


def test_select_tree1(filesystem, database):
    database.walk(filesystem)

    database.query("SELECT file_name, file_size from tree1_subdir_1")


def test_select_tree1_deep(filesystem, database):
    database.walk(filesystem)

    database.query("SELECT file_name, file_size from tree1_subdir_1/tree1_subdir_2")


def test_select_where(filesystem, database):
    database.walk(filesystem)

    database.query("SELECT file_name, file_size from . WHERE name = 'file1'")


def test_select_depth(filesystem, database):
    database.walk(filesystem)

    database.query("SELECT file_name, file_size from . WHERE depth = 1")


def test_select_count(filesystem, database):
    database.walk(filesystem)

    database.query("SELECT COUNT(*) from .")
