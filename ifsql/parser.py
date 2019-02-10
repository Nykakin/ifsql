import lark
import lark.exceptions

import sqlalchemy.sql

GRAMMAR = "".join(
    (
        # simple-select-stmt
        # https://www.sqlite.org/docsrc/doc/trunk/art/syntax/all-bnf.html#simple-select-stmt
        # WITH [ RECURSIVE ] clause is not supported
        """
            simple_select: select_core simple_select_order_by simple_select_limit_offset
    
            simple_select_order_by: [ /order/i /by/i ordering_term ( "," ordering_term )* ]
            simple_select_limit_offset: [ /limit/i expr [ [ /offset/i | "," ]~1 expr ] ]

            ordering_term: expr [ /collate/i collation_name ] [ /asc/i | /desc/i ]
        """,
        # select-core
        # https://www.sqlite.org/docsrc/doc/trunk/art/syntax/all-bnf.html#select-core
        # VALUES clause is not supported
        """    
            select_core: /select/i select_core_params select_core_columns select_core_from select_core_where select_core_aggr
            select_core_params: [ /distinct/i | /all/i ]
            select_core_columns: result_column ( "," result_column )*
            select_core_from: [ /from/i table_name ]
            select_core_where: [ /where/i expr ]
            select_core_aggr: [ /group/i /by/i expr ( "," expr )* [ /having/i expr ] ]
        """,
        # result-column
        # https://www.sqlite.org/docsrc/doc/trunk/art/syntax/all-bnf.html#result-column
        # passing table-name is not supported, since we have only one table with file data to work with
        # aliasing with as is not supported for very same reason
        """
            !result_column: "*" | expr [ /as/i string ]
        """,
        # table name in select from can be either a string (which is a path like "./path/to/my/dir"
        # or a dot ., which is translated to local directory
        """
            !table_name: string | "."
        """,
        # expr
        # https://www.sqlite.org/docsrc/doc/trunk/art/syntax/all-bnf.html#expr
        #
        # TODO: support select statements (https://www.sqlite.org/docsrc/doc/trunk/art/syntax/all-bnf.html#select-stmt)
        #   in order to allow subquerying?
        # TODO: support type casitng?
        # TODO: support collations
        """
            !expr: literal_value
                | column_name
                | unary_operator expr
                | expr binary_operator expr
                | expr binary_operator expr
                | "(" expr ")"
                | function_name "(" [ [ /distinct/i ] expr expr_comma | "*" ] ")"
                | expr [ /not/i ] ( /like/i | /glob/i | /regexp/i | /match/i ) expr [ /escape/i expr ]
                | expr ( /isnull/i | /notnull/i | /not null/i )
                | expr /is/i [ /not/i ] expr
                | expr [ /not/i ] /in/i "(" expr_comma ")"
                | expr [ /not/i ] /between/i expr /and/i expr
                | /case/i [ expr ] (/when/i expr /then/i expr)* [ /else/i expr ] /end/i
    
            !expr_comma: expr ( "," expr )*

            column_name: /[a-z_]+/
            function_name: /[a-z]+/
            collation_name: /a-z]+/

            !unary_operator: "+" 
                | "-"
                | /not/i    
                | "~"

            !binary_operator: "||"
                | "*"
                | "/"
                | "%"
                | "+"
                | "-"
                | "<<"
                | ">>"
                | "&" 
                | "|"
                | "<"
                | "<="
                | ">"
                | ">="
                | "="
                | "==" 
                | "!="
                | "<>"
                | /is not/i 
                | /is/i
                | /in/i
                | /like/i 
                | /glob/i 
                | /match/i
                | /regexp/i
                | /and/i
                | /or/i
    
            raise_function: /raise/i ( [ /ignore/i | [ /rollback/i | /abort/i | /fail/i ]~1 "," error_message ]~1 )
            error_message: /[a-zA-Z0-9]+/
        """,
        # literal_value
        # https://www.sqlite.org/docsrc/doc/trunk/art/syntax/all-bnf.html#literal-value
        """
            literal_value: SIGNED_NUMBER -> number
                | string
                | /null/i
                | "CURRENT_DATE" -> current_date
                | "CURRENT_TIME" -> current_time
                | "CURRENT_TIMESTAMP" -> current_timestamp
        """,
        # string is defined as either
        # * sequence of alphanumeric characters inside souble quotes, e.g. "test"
        # * sequence of alphanumeric characters insinde backticks, e.g. 'test'
        # * sequence of alphanumeric characters that doesn't contain comma and spaces and doesn't
        #   start with a number, e.g. test
        """
            string: ESCAPED_STRING | BACKTICK_STRING | /[^0-9"' ,][^"' ,]*/

            BACKTICK_STRING_INNER: ("\\\'"|/[^']/)
            BACKTICK_STRING: "'" BACKTICK_STRING_INNER* "'"
        """,
        # common utilities
        """
            number: SIGNED_NUMBER

            %import common.ESCAPED_STRING
            %import common.SIGNED_NUMBER
            %import common.WS
            %ignore WS
        """,
    )
)


class TreeToSqlAlchemy(lark.Transformer):
    def expr(self, args):
        return " ".join(args)

    def expr_comma(self, args):
        return ", ".join(args)

    def to_str(self, args):
        return str(args[0])

    literal_value = to_str
    string = to_str
    number = to_str
    binary_operator = to_str
    unary_operator = to_str
    column_name = to_str
    table_name = to_str
    function_name = to_str
    collation_name = to_str
    raise_function = to_str
    error_message = to_str

    def simple_select(self, args):
        select = args[0]
        if args[1] is not None:
            select = select.order_by(args[1])
        if args[2][0] is not None:
            select = select.limit(args[2][0])
        if args[2][1] is not None:
            select = select.offset(args[2][0])
        return select

    def select_core(self, args):
        select = sqlalchemy.sql.select(
            columns=args[2], from_obj=sqlalchemy.sql.table(args[3])
        )
        if args[1] is not None:
            select = select.distinct()
        if args[4] is not None:
            select = select.where(args[4])
        if args[5][0] is not None:
            select = select.group_by(args[5][0])
        if args[5][1] is not None:
            select = select.having(args[5][1])

        return select

    def select_core_from(self, args):
        return str(args[1])

    def select_core_params(self, args):
        distinct = None
        if len(args) > 0:
            if args[0].lower() == "distinct":
                distinct = object()
        return distinct

    def select_core_columns(self, args):
        return list(args)

    def result_column(self, args):
        column = sqlalchemy.sql.literal_column(str(args[0]))
        if len(args) > 1:
            column = column.label(args[2].strip("'\"'"))

        return column

    def select_core_where(self, args):
        where = None
        if len(args) > 0:
            where = sqlalchemy.sql.text(args[1])
        return where

    def select_core_aggr(self, args):
        group_by, having = None, None
        if len(args) > 0:
            group_by = sqlalchemy.sql.text(args[2])
        if len(args) > 3:
            having = sqlalchemy.sql.text(args[4])
        return group_by, having

    def ordering_term(self, args):
        return " ".join(args)

    def simple_select_order_by(self, args):
        order_by = None
        if len(args) > 0:
            order_by = sqlalchemy.sql.text(args[2])
        return order_by

    def simple_select_limit_offset(self, args):
        limit, offset = None, None
        if len(args) > 0:
            limit = sqlalchemy.sql.text(args[1])
        if len(args) > 3:
            offset = sqlalchemy.sql.text(args[3])
        return limit, offset


class ParserException(Exception):
    pass


class Parser:
    def __init__(self):
        self._parser = lark.Lark(GRAMMAR, start="simple_select")
        self._transformer = TreeToSqlAlchemy()

    def parse(self, text):
        try:
            tree = self._parser.parse(text)
            return self._transformer.transform(tree)
        except lark.exceptions.LarkError as e:
            raise ParserException("parser error") from e
