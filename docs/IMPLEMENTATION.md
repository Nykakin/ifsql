To put it simply, `ifsql` works by creating in-memory SQLite database that is then populated with file metadata obtained from traversing the tree with `os.walk`. Management of this database is delegated to sqlalchemy library in order to avoid excesive use of raw queries.

To represent directory tree structure using RDBMS a pattern called [Closure Table](http://technobytz.com/closure_table_store_hierarchical_data.html) is used. Basically, there are two tables in the memory: `files` and `relations`. Each row of `files` table contains detailed information about a single file - its name, size, owner and so on. `relations` table is used to model the hierarchy. For every directory there are rows mapping relations between it and every of its descendants, including a relation to itself. For example, given following directory tree:

```
$ tree
.
├── DIRECTORY_1
│   └── FILE_2
├── DIRECTORY_2
│   └── DIRECTORY_3
│       └── FILE_3
└── FILE_1
```

We obtain following model:

![example](./relation-schema.png)

Every arrow in this chart represents a single relation row. Besides the pair ancestor_id/descendant_id it also contain a depth value, which makes queries limited to a certain directoryy tree depth possible.

For more information about this technique can be found in a book *[SQL Antipatterns](https://pragprog.com/book/bksqla/sql-antipatterns)* by Bill Karwin.
