import pytest


@pytest.mark.parametrize(
    "input_query",
    [
        "SELECT * from .",
        "SELECT * from 'dir'",
        'SELECT * from "dir"',
        "SELECT * from 'nested/path'",
        'SELECT * from "nested/path"',
        "SELECT * from './nested/path'",
        'SELECT * from "./nested/path"',
        "SELECT file_name from .",
        "select file_name, file_size from .",
        "select file_name as fn from .",
        "select file_name as fn, file_size as fs from .",
        "select file_size+12 from .",
        "select distinct * from .",
        "select * from . where file_size < 10",
        "select * from . where (file_size * 2) > 12",
        "select * from . where file_name like 'test%.txt'",
        "select * from . where file_name is NULL",
        "select * from . where file_name is not null",
        "select * from . where file_name IN ('a', 'b', 'c')",
        "select * from . where file_size BETWEEN 1 and 12",
        "select * from . where file_name BETWEEN some_column + 12 and (123232/32)",
        "select * from . where file_name NOT IN (1, 2, 3 ,4)",
        "SELECT a, b, CASE WHEN a > 30 THEN 'x' when a = 30 then 'y' else 'z' end from .",
        "select sum(*), a from . group by a",
        "select sum(*), a from . where a < 100 group by a",
        "select count(abc) from . where abc < 100 group by x having count(abc) < 9",
    ],
)
def test_parser(parser, input_query):
    parser.parse(input_query)
