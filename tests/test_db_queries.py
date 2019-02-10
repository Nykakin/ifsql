import operator

import pytest


def test_select_all_items_one_level(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=100)
    fs.add_file(path="file2", size=200)
    fs.add_file(path="file3", size=300)
    fs.add_file(path="file4", size=400)
    fs.add_file(path="file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM .")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 6
    expected = [".", "file1", "file2", "file3", "file4", "file5"]
    assert sorted(r.file_name for r in result) == expected


def test_select_all_files_one_level(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=100)
    fs.add_file(path="file2", size=200)
    fs.add_file(path="file3", size=300)
    fs.add_file(path="file4", size=400)
    fs.add_file(path="file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM . WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 5
    expected = ["file1", "file2", "file3", "file4", "file5"]
    assert sorted(r.file_name for r in result) == expected


def test_select_one_file_one_level(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=100)
    fs.add_file(path="file2", size=200)
    fs.add_file(path="file3", size=300)
    fs.add_file(path="file4", size=400)
    fs.add_file(path="file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM . WHERE file_name = 'file5'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    expected = ["file5"]
    assert sorted(r.file_name for r in result) == expected


def test_select_all_items_multiple_levels(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("subdir1")
    fs.add_directory("subdir2")
    fs.add_directory("subdir2/subdir3")
    fs.add_file(path="file1", size=100)
    fs.add_file(path="subdir1/file2", size=200)
    fs.add_file(path="subdir1/file3", size=300)
    fs.add_file(path="subdir2/file4", size=400)
    fs.add_file(path="subdir2/subdir3/file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM .")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 9
    expected = [
        ".",
        "file1",
        "file2",
        "file3",
        "file4",
        "file5",
        "subdir1",
        "subdir2",
        "subdir3",
    ]
    assert sorted(r.file_name for r in result) == expected


def test_select_all_files_multiple_levels(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("subdir1")
    fs.add_directory("subdir2")
    fs.add_directory("subdir2/subdir3")
    fs.add_file(path="file1", size=100)
    fs.add_file(path="subdir1/file2", size=200)
    fs.add_file(path="subdir1/file3", size=300)
    fs.add_file(path="subdir2/file4", size=400)
    fs.add_file(path="subdir2/subdir3/file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM . WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 5
    expected = ["file1", "file2", "file3", "file4", "file5"]
    assert sorted(r.file_name for r in result) == expected


def test_select_one_file_multiple_levels(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("subdir1")
    fs.add_directory("subdir2")
    fs.add_directory("subdir2/subdir3")
    fs.add_file(path="file1", size=100)
    fs.add_file(path="subdir1/file2", size=200)
    fs.add_file(path="subdir1/file3", size=300)
    fs.add_file(path="subdir2/file4", size=400)
    fs.add_file(path="subdir2/subdir3/file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM . WHERE file_name = 'file5'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    expected = ["file5"]
    assert sorted(r.file_name for r in result) == expected


def test_select_all_items_from_subdir(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("subdir1")
    fs.add_directory("subdir2")
    fs.add_directory("subdir2/subdir3")
    fs.add_file(path="file1", size=100)
    fs.add_file(path="subdir1/file2", size=200)
    fs.add_file(path="subdir1/file3", size=300)
    fs.add_file(path="subdir2/file4", size=400)
    fs.add_file(path="subdir2/subdir3/file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM subdir1")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 3
    expected = ["file2", "file3", "subdir1"]
    assert sorted(r.file_name for r in result) == expected


def test_select_all_files_from_subdir(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("subdir1")
    fs.add_directory("subdir2")
    fs.add_directory("subdir2/subdir3")
    fs.add_file(path="file1", size=100)
    fs.add_file(path="subdir1/file2", size=200)
    fs.add_file(path="subdir1/file3", size=300)
    fs.add_file(path="subdir2/file4", size=400)
    fs.add_file(path="subdir2/subdir3/file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * FROM subdir1 WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 2
    expected = ["file2", "file3"]
    assert sorted(r.file_name for r in result) == expected


def test_select_one_file_from_subdir(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("subdir1")
    fs.add_directory("subdir2")
    fs.add_directory("subdir2/subdir3")
    fs.add_file(path="file1", size=100)
    fs.add_file(path="subdir1/file2", size=200)
    fs.add_file(path="subdir1/file3", size=300)
    fs.add_file(path="subdir2/file4", size=400)
    fs.add_file(path="subdir2/subdir3/file5", size=500)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT * FROM subdir1 WHERE file_type = 'F' AND file_name = 'file2'"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    expected = ["file2"]
    assert sorted(r.file_name for r in result) == expected


def test_select_depth(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("level_1")
    fs.add_directory("level_1/level_2")
    fs.add_directory("level_1/level_2/level_3")
    fs.add_file(path="level_0_file", size=10)
    fs.add_file(path="level_1/level_1_file", size=10)
    fs.add_file(path="level_1/level_2/level_2_file", size=10)
    fs.add_file(path="level_1/level_2/level_3/level_3_file", size=10)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT file_name, depth FROM . WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 4
    expected = [
        ("level_0_file", 1),
        ("level_1_file", 2),
        ("level_2_file", 3),
        ("level_3_file", 4),
    ]
    sorted_result = sorted(result, key=operator.attrgetter("file_name"))
    assert [(r.file_name, r.depth) for r in sorted_result] == expected


def test_expression(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=100)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT (file_size-1)*10 FROM . WHERE file_name = 'file1'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][0] == 990


def test_select_distinct(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=100)
    fs.add_file(path="file2", size=100)
    fs.add_file(path="file3", size=100)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT DISTINCT file_size FROM . WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][0] == 100


def test_select_where(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=10)
    fs.add_file(path="file2", size=20)
    fs.add_file(path="file3", size=30)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT file_name, file_size FROM . WHERE file_type = 'F' AND file_size = 20"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name == "file2"
    assert result[0].file_size == 20


def test_select_alias(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=100)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        """SELECT file_name as file_name_alias FROM . WHERE file_name_alias = 'file1'"""
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name_alias == "file1"


def test_select_where_expr(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="file1", size=11)
    fs.add_file(path="file2", size=22)
    fs.add_file(path="file3", size=33)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT * from . WHERE (file_size % 2) == 0 AND file_type = 'F'"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name == "file2"
    assert result[0].file_size == 22


def test_select_where_like(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=100)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=100)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * from . WHERE file_name LIKE 'second_%'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name == "second_file"


def test_select_where_in(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=100)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=100)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT * from . WHERE file_name IN ('second_file', 'fourth_file', 'sixth_file')"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name == "second_file"


def test_select_where_between(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=10)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=200)
    fs.add_file(path="fourth_file", size=1000)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT * from . WHERE file_size BETWEEN 50 AND 500")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 2
    assert result[0].file_name == "third_file"
    assert result[1].file_name == "second_file"


def test_select_where_not_in(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=100)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=100)
    fs.add_file(path="fourth_file", size=100)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT * from . WHERE file_name NOT IN ('first_file', 'second_file')"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 3
    assert result[0].file_name == "."
    assert result[1].file_name == "third_file"
    assert result[2].file_name == "fourth_file"


def test_select_case(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=10)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        """
        SELECT file_name, CASE 
            WHEN file_size < 100 then '<100'
            WHEN file_size > 100 then '>100'
            ELSE '=100' END
            AS 'case_query'
        from . WHERE file_type = 'F'
    """
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 3
    assert result[0].file_name == "third_file"
    assert result[0][1] == ">100"
    assert result[1].file_name == "second_file"
    assert result[1][1] == "=100"
    assert result[2].file_name == "first_file"
    assert result[2][1] == "<100"


def test_select_count(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("dir1")
    fs.add_directory("dir2")
    fs.add_directory("dir3")
    fs.add_directory("dir4")

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT COUNT(*) FROM .")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][0] == 5


def test_select_sum(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=10)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT sum(file_size) FROM . WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][0] == 310


def test_select_group_concat(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("dir1")
    fs.add_directory("dir2")

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT GROUP_CONCAT(file_name) FROM .")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][0] == ".,dir1,dir2"


def test_select_min(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=10)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT file_name, min(file_size) FROM . WHERE file_type = 'F'"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name == "first_file"


def test_select_max(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=10)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT file_name, max(file_size) FROM . WHERE file_type = 'F'"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0].file_name == "third_file"


def test_select_avg(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=3)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse("SELECT avg(file_size) FROM . WHERE file_type = 'F'")
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][0] == 101.0


def test_select_sum_where(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_file(path="first_file", size=10)
    fs.add_file(path="second_file", size=100)
    fs.add_file(path="third_file", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT sum(file_size) FROM . WHERE file_type = 'F' AND file_size > 10"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][0] == 300


def test_select_sum_group_by(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("dir1")
    fs.add_directory("dir2")
    fs.add_file(path="dir1/file1", size=10)
    fs.add_file(path="dir1/file2", size=100)
    fs.add_file(path="dir2/file1", size=20)
    fs.add_file(path="dir2/file2", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        "SELECT file_name, sum(file_size) FROM . WHERE file_type = 'F' GROUP BY file_name"
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 2
    assert result[0][1] == 30
    assert result[1][1] == 300


def test_select_sum_group_by_having(fs, database, parser):
    import ifsql.database
    import ifsql.analyse

    path_id_cache = {}

    fs.add_directory("dir1")
    fs.add_directory("dir2")
    fs.add_file(path="dir1/file1", size=10)
    fs.add_file(path="dir1/file2", size=100)
    fs.add_file(path="dir2/file1", size=20)
    fs.add_file(path="dir2/file2", size=200)

    ifsql.analyse.walk(fs.root, database, path_id_cache)

    query = parser.parse(
        """
        SELECT file_name, sum(file_size) as total_sum FROM .
        WHERE file_type = 'F' GROUP BY file_name HAVING total_sum < 100
    """
    )
    result = list(database.query(query, path_id_cache))

    assert len(result) == 1
    assert result[0][1] == 30
