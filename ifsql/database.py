import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.sql
import sqlalchemy.orm


Base = sqlalchemy.ext.declarative.declarative_base()


def fields():
    return list(File._field_names) + ["depth"]


class File(Base):
    __tablename__ = "files"

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
    dirname = sqlalchemy.Column(sqlalchemy.String())
    full_path = sqlalchemy.Column(sqlalchemy.String())
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

    relation_id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    ancestor_id = sqlalchemy.Column(
        sqlalchemy.Integer(), sqlalchemy.ForeignKey("files.file_id"), index=True
    )
    descendant_id = sqlalchemy.Column(
        sqlalchemy.Integer(), sqlalchemy.ForeignKey("files.file_id"), index=True
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
        self.SessionMaker = sqlalchemy.orm.sessionmaker(engine)
        self.file_count = 0
        self.connection = engine.connect()

    def begin(self):
        self.insert_transaction = self.connection.begin()

    def commit(self):
        self.insert_transaction.commit()

    def create_session(self):
        self._session = self.SessionMaker()

    def insert_file(self, data, parent_id):
        self.file_count += 1
        data["file_id"] = self.file_count
        self.connection.execute(File.__table__.insert(), [data])

        relation_data = {
            "ancestor_id": self.file_count,
            "descendant_id": self.file_count,
            "depth": 0,
        }
        self.connection.execute(Relation.__table__.insert(), relation_data)

        if parent_id is not None:
            select = Relation.__table__.select().where(
                Relation.descendant_id == parent_id
            )
            result = self.connection.execute(select)
            relation_data = []
            for rel in result:
                relation_data.append(
                    {
                        "ancestor_id": rel.ancestor_id,
                        "descendant_id": self.file_count,
                        "depth": rel.depth + 1,
                    }
                )
            self.connection.execute(Relation.__table__.insert(), relation_data)

        return self.file_count

    def query(self, query, path_id_cache):
        # replace from clause into a join with relationship table
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
        fields = (
            File.file_name,
            File.dirname,
            File.full_path,
            File.file_type,
            File.file_size,
            File.access_time,
            File.modification_time,
            File.group_id,
            File.owner_id,
            Relation.depth,
        )
        for c in query._raw_columns:
            if str(c).strip() == "*":
                cols.extend(fields)
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
