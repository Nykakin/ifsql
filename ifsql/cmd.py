from ifsql import analyse
from ifsql import database
from ifsql import parser

from pygments.lexers.sql import SqlLexer
from pygments.token import Token
from pygments.style import Style as PygmentsStyle
from pygments.lexers.sql import SqlLexer

from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.styles import merge_styles
from prompt_toolkit.completion import WordCompleter, merge_completers
from prompt_toolkit.styles import Style as PromptToolkitStyle

ColumnToken = Token.ColumnToken
PathToken = Token.PathToken


class SQLSyntaxStyle(PygmentsStyle):
    default_style = ""
    styles = {ColumnToken: "italic #808", PathToken: "bold #AA0"}


CompletionMenuStyle = PromptToolkitStyle.from_dict(
    {
        "completion-menu.completion": "bg:#008888 #ffffff",
        "completion-menu.completion.current": "bg:#00aaaa #000000",
        "scrollbar.background": "bg:#88aaaa",
        "scrollbar.button": "bg:#222222",
    }
)


class IfsqlLexer(SqlLexer):
    name = "IfsqlLexer"
    aliases = ["IfsqlLexer"]

    def get_tokens_unprocessed(self, text):
        for index, token, value in SqlLexer.get_tokens_unprocessed(self, text):
            if value in database.fields():
                yield index, ColumnToken, value
            else:
                yield index, token, value


IfsqlCompleter = merge_completers(
    [
        WordCompleter(
            [
                "select",
                "distinct",
                "all",
                "from",
                "collate",
                "asc",
                "desc",
                "order",
                "by",
                "limit",
                "offset",
                "where",
                "group",
                "having" "as",
                "not",
                "like",
                "glob",
                "regexp",
                "match",
                "escape",
                "isnull",
                "notnull",
                "not null",
                "not",
                "and",
                "or",
                "is",
                "in",
                "between",
                "case",
                "when",
                "then",
                "else",
                "end",
                "raise",
                "ignore",
                "rollback",
                "abort",
                "fail",
                "null",
            ],
            ignore_case=True,
        ),
        WordCompleter(database.fields(), ignore_case=True),
    ]
)


class Cmd:
    def __init__(self, root):
        self._database = database.Database()
        self._parser = parser.Parser()
        self._path_id_cache = {}

        self.prompt_session = PromptSession(
            lexer=PygmentsLexer(IfsqlLexer),
            completer=IfsqlCompleter,
            style=merge_styles(
                [CompletionMenuStyle, style_from_pygments_cls(SQLSyntaxStyle)]
            ),
        )

        analyse.walk(root, self._database, self._path_id_cache)

    def run(self):
        while True:
            try:
                text = self.prompt_session.prompt("> ")
            except KeyboardInterrupt:
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D pressed.

            print(text)

    def query(self, input_query):
        s = self._parser.parse(input_query)
        path = s.froms[0].name
        s._from_obj.clear()
        s = s.select_from(table("another_table"))

        print(s)
