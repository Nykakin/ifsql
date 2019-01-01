import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.sql
import sqlalchemy.orm


Base = sqlalchemy.ext.declarative.declarative_base()

class File(Base):
    __tablename__ = "files"
    __table_args__ = {"sqlite_autoincrement": True}

    file_id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    file_name = sqlalchemy.Column(sqlalchemy.String())
    file_path = sqlalchemy.Column(sqlalchemy.String())
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
            "file_path",
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
    __tablename__ = "relations"

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

        p = Relation(ancestor_id=f.file_id, descendant_id=f.file_id, path_length=0)
        self._session.add(p)
        self._session.flush()

        if parent_id is not None:
            for rel in self._session.query(Relation).filter(
                Relation.descendant_id == parent_id
            ):
                r = Relation(
                    ancestor_id=rel.ancestor_id,
                    descendant_id=f.file_id,
                    path_length=rel.path_length + 1,
                )
                self._session.add(r)
                self._session.flush()

        return f.file_id

    def query(self, query, path_id_cache):
        """
            SELECT f.*
            FROM files AS f
            JOIN relations AS r ON f.file_id = r.descendant_id
            WHERE r.ancestor_id = 4;
        """
        path_id = path_id_cache[query.froms[0].name]
        query._from_obj.clear()
        join = sqlalchemy.orm.join(File, Relation, File.file_id == Relation.descendant_id)
        query = query.select_from(join).where(Relation.ancestor_id == path_id)
        return self._session.execute(query)

    @property
    def files(self):
        return self._session.query(File)

    @property
    def relations(self):
        return self._session.query(Relation).options(
            sqlalchemy.orm.joinedload("ancestor"),
            sqlalchemy.orm.joinedload("descendant"),
        )
