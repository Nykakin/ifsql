import datetime
import os
import os.path
import stat

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

Base = sqlalchemy.ext.declarative.declarative_base()


class File(Base):
    __tablename__ = "files"
    __table_args__ = {"sqlite_autoincrement": True}

    file_id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    file_name = sqlalchemy.Column(sqlalchemy.String())
    file_type = sqlalchemy.Column(sqlalchemy.String(1))
    file_size = sqlalchemy.Column(sqlalchemy.Integer())
    access_time = sqlalchemy.Column(sqlalchemy.DateTime())
    modification_time = sqlalchemy.Column(sqlalchemy.DateTime())
    group_id = sqlalchemy.Column(sqlalchemy.Integer())
    owner_id = sqlalchemy.Column(sqlalchemy.Integer())

    def __eq__(self, other):
        if isinstance(other, File):
            return self._fields == other._fields
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def _fields(self):
        fields = (
            "file_id",
            "file_name",
            "file_type",
            "file_size",
            "access_time",
            "modification_time",
            "group_id",
            "owner_id",
        )
        return {f: getattr(self, f) for f in fields}

    def __str__(self):
        return self.file_name

    def __repr__(self):
        args = [
            "{}={}".format(field, repr(value))
            for (field, value) in self._fields.items()
        ]
        return "File({})".format(", ".join(args))


class Relation(Base):
    __tablename__ = "paths"

    ancestor_id = sqlalchemy.Column(
        sqlalchemy.Integer(), sqlalchemy.ForeignKey("files.file_id"), primary_key=True
    )
    descendant_id = sqlalchemy.Column(
        sqlalchemy.Integer(), sqlalchemy.ForeignKey("files.file_id"), primary_key=True
    )
    path_length = sqlalchemy.Column(sqlalchemy.Integer())

    ancestor = sqlalchemy.orm.relationship(
        "File", uselist=False, foreign_keys=[ancestor_id]
    )
    descendant = sqlalchemy.orm.relationship(
        "File", uselist=False, foreign_keys=[descendant_id]
    )

    def __eq__(self, other):
        if isinstance(other, Relation):
            return self._fields == other._fields
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def _fields(self):
        fields = ("ancestor_id", "descendant_id", "path_length")
        return {f: getattr(self, f) for f in fields}

    def __str__(self):
        return "{} - {}".format(self.ancestor_id, self.descendant_id)

    def __repr__(self):
        args = [
            "{}={}".format(field, repr(value))
            for (field, value) in self._fields.items()
        ]
        return "Relation({})".format(", ".join(args))


def file_type(mode):
    if stat.S_ISDIR(mode):
        return "D"
    if stat.S_ISREG(mode):
        return "F"
    if stat.S_ISCHR(mode):
        return "C"
    if stat.S_ISBLK(mode):
        return "B"
    if stat.S_ISFIFO(mode):
        return "N"
    if stat.S_ISLNK(mode):
        return "L"
    if stat.S_ISSOCK(mode):
        return "S"


def analyse_file(path):
    result = os.stat(path)

    return {
        "file_type": file_type(result.st_mode),
        "file_size": result.st_size,
        "access_time": datetime.datetime.fromtimestamp(result.st_atime),
        "modification_time": datetime.datetime.fromtimestamp(result.st_mtime),
        "owner_id": result.st_uid,
        "group_id": result.st_gid,
    }


class Database:
    def __init__(self):
        engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        self._session = Session()
        self._path_id_cache = {}

    def insert_file(self, path, parent):
        f = File(file_name=path, **analyse_file(path))
        self._session.add(f)
        self._session.flush()
        self._path_id_cache[path] = f.file_id
        p = Relation(ancestor_id=f.file_id, descendant_id=f.file_id, path_length=0)
        self._session.add(p)
        self._session.flush()

        if parent is not None:
            for rel in self._session.query(Relation).filter(
                Relation.descendant_id == parent.file_id
            ):
                r = Relation(
                    ancestor_id=rel.ancestor_id,
                    descendant_id=f.file_id,
                    path_length=rel.path_length + 1,
                )
                self._session.add(r)
                self._session.flush()
        return f

    def walk(self, fs):
        parent = None
        for root, _, files in os.walk(fs):
            parent = self.insert_file(root, parent)

            for name in files:
                self.insert_file(os.path.join(root, name), parent)

    def path_id(self, path):
        return self._path_id_cache[path]

    def query(self, query):
        pass

    @property
    def files(self):
        return self._session.query(File)

    @property
    def relations(self):
        return self._session.query(Relation).options(
            sqlalchemy.orm.joinedload("ancestor"),
            sqlalchemy.orm.joinedload("descendant"),
        )
