import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.sql
import sqlalchemy.orm


Base = sqlalchemy.ext.declarative.declarative_base()


def fields():
    return list(File._field_names) + ["depth"]


class File(Base):
    __tablename__ = "files"
    __table_args__ = {"sqlite_autoincrement": True}

    _field_names = (
        "file_id",
        "file_name",
        "file_path",
        "file_type",
        "file_size",
        "access_time",
        "modification_time",
        "group_id",
        "owner_id",
    )

    file_id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    file_name = sqlalchemy.Column(sqlalchemy.String())
    file_path = sqlalchemy.Column(sqlalchemy.String())
    file_absolute_path = sqlalchemy.Column(sqlalchemy.String())
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
        return {f: getattr(self, f) for f in File._field_names}

    def __str__(self):
        return self.file_name

    def __repr__(self):
        args = [
            "{}={}".format(field, repr(value))
            for (field, value) in self._fields.items()
        ]
        return "File({})".format(", ".join(args))


class Relation(Base):
    __tablename__ = "relations"

    ancestor_id = sqlalchemy.Column(
        sqlalchemy.Integer(), sqlalchemy.ForeignKey("files.file_id"), primary_key=True
    )
    descendant_id = sqlalchemy.Column(
        sqlalchemy.Integer(), sqlalchemy.ForeignKey("files.file_id"), primary_key=True
    )
    depth = sqlalchemy.Column(sqlalchemy.Integer())

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
        fields = ("ancestor_id", "descendant_id", "depth")
        return {f: getattr(self, f) for f in fields}

    def __str__(self):
        return "{} - {}".format(self.ancestor_id, self.descendant_id)

    def __repr__(self):
        args = [
            "{}={}".format(field, repr(value))
            for (field, value) in self._fields.items()
        ]
        return "Relation({})".format(", ".join(args))


class DatabaseException(Exception):
    pass


class Database:
    def __init__(self):
        engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        self._session = Session()

    def insert_file(self, data, parent_id):
        f = File(**data)
        self._session.add(f)
        self._session.flush()

        p = Relation(ancestor_id=f.file_id, descendant_id=f.file_id, depth=0)
        self._session.add(p)
        self._session.flush()

        if parent_id is not None:
            for rel in self._session.query(Relation).filter(
                Relation.descendant_id == parent_id
            ):
                r = Relation(
                    ancestor_id=rel.ancestor_id,
                    descendant_id=f.file_id,
                    depth=rel.depth + 1,
                )
                self._session.add(r)
                self._session.flush()

        return f.file_id

    def query(self, query, path_id_cache):
        path_id = path_id_cache.get(query.froms[0].name.rstrip())
        if path_id is None:
            raise DatabaseException("Unknown FROM path")

        query._from_obj.clear()
        join = sqlalchemy.orm.join(
            File, Relation, File.file_id == Relation.descendant_id
        )
        query = query.select_from(join).where(Relation.ancestor_id == path_id)

        # ignore ancestor_id and descendant_id in result if "select *" was used
        cols = []
        for c in query._raw_columns:
            if str(c).strip() == "*":
                cols.extend([File, Relation.depth])
            else:
                cols.append(c)
        query = query.with_only_columns(cols)

        result = self._session.execute(query)
        return result

    @property
    def files(self):
        return self._session.query(File)

    @property
    def relations(self):
        return self._session.query(Relation).options(
            sqlalchemy.orm.joinedload("ancestor"),
            sqlalchemy.orm.joinedload("descendant"),
        )
