from .db import Database as dbDatabase
from .db import Table as dbTable
from .db import View as dbView
from .db import (resolve_extracts, COLUMN_TYPE_MAPPING, ForeignKey, ForeignKeysType, AlterError, validate_column_names,
                 NotFoundError, jsonify_if_needed)
from typing import Union, Literal, Any, Optional, Dict, List, Iterable, cast, Sequence

#table
class Table(dbTable):
    def find(self, *args, toTuple: bool = False, orderBy: Dict[str,Literal['ASC','DESC']]=None)->Union[None, List[Dict[str, Any]]]:
        '''
        Condition pattern: (column, operator, value). condition1, condition2, condition3...
        Condition can be =, !=, <, <=, >, >=, like, not like, is, is not, in, not in
        orderBy: {"column1": "ASC", "column2": "DESC"}
        '''
        pass
    def find_first(self, *args)->Union[None, Dict[str, Any]]:
        '''condition pattern: (column, operator, value). condition1, condition2, condition3...
        Condition can be =, !=, <, <=, >, >=, like, not like, is, is not, in, not in'''
        pass
    def printTable(self):
        pass
    def add_trigger(self, name, event: Literal["INSERT", "DELETE", "UPDATE"], sql: str,
                    time: Literal["BEFORE", "AFTER"] = "AFTER", column: str = None, if_not_exists:bool=False,
                    whenExpr:str=None):
        pass
    def remove_trigger(table, name):
        pass
    def getTableSequence(self)->Union[None, int]:
        pass
    def update(
        self,
        pk_values: Union[list, tuple, str, int, float, dict],
        updates: Optional[dict] = None,
        alter: bool = False,
        conversions: Optional[dict] = None,
    ) -> "Table":
        """
        Execute a SQL ``UPDATE`` against the specified row.
        See :ref:`python_api_update`.
        Special case: if ``pk_values`` is a dictionary, it will find primary keys automatically, and redo update with correct parameters.

        :param pk_values: The primary key of an individual record - can be a tuple if the
          table has a compound primary key.
        :param updates: A dictionary mapping columns to their updated values.
        :param alter: Set to ``True`` to add any missing columns.
        :param conversions: Optional dictionary of SQL functions to apply during the update, for example
          ``{"mycolumn": "upper(?)"}``."""
        pass
originUpdate = dbTable.update
def update(
        self,
        pk_values: Union[list, tuple, str, int, float, dict],
        updates: Optional[dict] = None,
        alter: bool = False,
        conversions: Optional[dict] = None,
) -> "Table":
    if isinstance(pk_values, dict) and updates is None:
        print('here')
        _pks = []
        for pk in self.pks:
            if pk in pk_values:
                _pks.append(pk_values[pk])
        return originUpdate(self, _pks, pk_values, alter=alter, conversions=conversions)
    return originUpdate(self, pk_values, updates, alter=alter, conversions=conversions)
def find(self, *args, toTuple: bool = False, orderBy: dict = None):
    if len(args) == 3 and not isinstance(args[0], tuple) and not isinstance(args[0], list):
        return self.find(tuple(args), toTuple=toTuple, orderBy=orderBy)
    else:
        sql = f"SELECT * FROM {self.name} WHERE "
        for i, pattern in enumerate(args):
            if i > 0:
                sql += " AND "
            sql += f"{pattern[0]} {pattern[1]} '{pattern[2]}'"
        if orderBy is not None:
            sql += " ORDER BY "
            for i, key in enumerate(orderBy):
                sql += f"{key} {orderBy[key]},"
            sql = sql[:-1]
        if not toTuple:
            return self.db.query(sql)
        else:
            output = []
            for data in self.db.query(sql):
                output.append(data)
            return tuple(output)
def find_first(self, *args)->Union[None, Dict[str, Any]]:
    if len(args) == 3 and not isinstance(args[0], tuple) and not isinstance(args[0], list):
        return self.find_first(tuple(args))
    else:
        sql = f"SELECT * FROM {self.name} WHERE "
        for i, pattern in enumerate(args):
            if i > 0:
                sql += " AND "
            sql += f"{pattern[0]} {pattern[1]} '{pattern[2]}'"
        for data in self.db.query(sql):
            return data #return first
        return None
def printTable(self):
    print('-----------------')
    print("table:", self.name)
    for row in self.rows:
        print(row)
    print('-----------------')
def add_trigger_table(self, name, event: Literal["INSERT", "DELETE", "UPDATE"], command: str,
                time: Literal["BEFORE", "AFTER"] = "AFTER", column: str = None, if_not_exists:bool=False,
                    whenExpr:str=None):
    _name = self.name + "_" + name
    _command = command+ ";" if command[-1] != ";" else command
    self.db.add_trigger(_name, event, self, _command, time, column, if_not_exists, whenExpr)
def remove_trigger(self, name):
    _name = self.name + "_" + name
    self.db.remove_trigger(_name)
def getTableSequence(self)->Union[None, int]:
    try:
        return self.db['sqlite_sequence'].find_first('name','=',self.name)['seq']
    except:
        return None
setattr(dbTable, "find", find)
setattr(dbTable, "find_first", find_first)
setattr(dbTable, "printTable", printTable)
setattr(dbTable, "add_trigger", add_trigger_table)
setattr(dbTable, "remove_trigger", remove_trigger)
setattr(dbTable, "getTableSequence", getTableSequence)
setattr(dbTable, "update", update)

#view
class View(dbView):
    def add_trigger(self, name, event: Literal["INSERT", "DELETE", "UPDATE"], command: str,
                    column: str = None, if_not_exists:bool=False, whenExpr:str=None):
        '''view trigger is name of table + "_" + name. Column is ignored for DELETE event.'''
        pass
    def remove_trigger(self, name):
        pass
    def find(self, *args, toTuple: bool = False, orderBy: Dict[str, Literal['ASC', 'DESC']] = None):
        '''pattern: (column, operator, value)'''
        pass
    def printView(self):
        pass
def add_trigger_view(self, name, event: Literal["INSERT", "DELETE", "UPDATE"], command: str,
                column: str = None, if_not_exists:bool=False, whenExpr:str=None):
    _name = self.name + "_" + name
    _command = command+ ";" if command[-1] != ";" else command
    self.db.add_trigger(_name, event, self, _command, "AFTER", column, if_not_exists, whenExpr)
def printView(self):
    print('-----------------')
    print("editable view:", self.name)
    for row in self.rows:
        print(row)
    print('-----------------')
setattr(dbView, "add_trigger", add_trigger_view)
setattr(dbView, "remove_trigger", remove_trigger)
setattr(dbView, "find", find)
setattr(dbView, "find_first", find_first)
setattr(dbView, "printView", printView)
class EditableView(View):
    def __init__(self, db:'Database', name:str, pks:Union[str,Sequence[str]]=None,
                 defaults:Dict[str,Any]=None):
        super().__init__(db, name)
        self.pks = [pks] if isinstance(pks,str) else pks if pks is not None else []
        self.defaults = defaults if defaults else {}
    def get(self, pk_values: Union[list, tuple, str, int]) -> dict:
        if not isinstance(pk_values, (list, tuple)):
            pk_values = [pk_values]
        pks = self.pks
        last_pk = pk_values[0] if len(pks) == 1 else pk_values
        if len(pks) != len(pk_values):
            raise NotFoundError(
                "Need {} primary key value{}".format(
                    len(pks), "" if len(pks) == 1 else "s"
                )
            )
        wheres = ["[{}] = ?".format(pk_name) for pk_name in pks]
        rows = self.rows_where(" and ".join(wheres), pk_values)
        try:
            row = list(rows)[0]
            self.last_pk = last_pk
            return row
        except IndexError:
            raise NotFoundError
    def delete(self, pk_values: Union[list, tuple, str, int, float]) -> "EditableView":
        if not isinstance(pk_values, (list, tuple)):
            pk_values = [pk_values]
        self.get(pk_values)
        wheres = ["[{}] = ?".format(pk_name) for pk_name in self.pks]
        sql = "delete from [{table}] where {wheres}".format(
            table=self.name, wheres=" and ".join(wheres)
        )
        with self.db.conn:
            self.db.execute(sql, pk_values)
        return self
    def delete_where(self, where: str = None, where_args: Optional[Union[Iterable, dict]] = None,) -> "EditableView":
        """
        Delete rows matching the specified where clause, or delete all rows in the table.

        See :ref:`python_api_delete_where`.

        :param where: SQL where fragment to use, for example ``id > ?``
        :param where_args: Parameters to use with that fragment - an iterable for ``id > ?``
          parameters, or a dictionary for ``id > :id``
        :param analyze: Set to ``True`` to run ``ANALYZE`` after the rows have been deleted.
        """
        if not self.exists():
            return self
        sql = "delete from [{}]".format(self.name)
        if where is not None:
            sql += " where " + where
        self.db.execute(sql, where_args or [])
        return self
    def update(self,pk_values: Union[list, tuple, str, int, float],updates: Optional[dict] = None, conversions: Optional[dict] = None) -> "EditableView":
        updates = updates or {}
        conversions = conversions or {}
        if not isinstance(pk_values, (list, tuple)):
            pk_values = [pk_values]
        # Soundness check that the record exists (raises error if not):
        self.get(pk_values)
        if not updates:
            return self
        args = []
        sets = []
        pks = self.pks
        validate_column_names(updates.keys())
        for key, value in updates.items():
            sets.append("[{}] = {}".format(key, conversions.get(key, "?")))
            args.append(jsonify_if_needed(value))
        wheres = ["[{}] = ?".format(pk_name) for pk_name in pks]
        args.extend(pk_values)
        sql = "update [{table}] set {sets} where {wheres}".format(
            table=self.name, sets=", ".join(sets), wheres=" and ".join(wheres)
        )
        with self.db.conn:
            rowcount = self.db.execute(sql, args).rowcount
            assert rowcount == 1
        self.last_pk = pk_values[0] if len(pks) == 1 else pk_values
        return self
    def insert(self, record: Dict[str, Any], ignore: bool=False, replace: bool=False) -> "EditableView":
        return self.insert_all([record],ignore=ignore,replace=replace)
    def insert_all(self,records:Iterable[Dict[str, Any]],ignore: bool=False, replace: bool=False) -> "EditableView":
        assert not (ignore and replace), "Use either ignore=True or replace=True, not both"
        allKeys = self.columns_dict.keys()
        for record in records:
            validate_column_names(record.keys())
            if not ignore and not replace:
                for key in allKeys:
                    if key not in record:
                        value = self.defaults.get(key, None)
                        if value is not None:
                            record[key] = value
            recordKeys = []
            recordValues = []
            for key in record:
                recordKeys.append(str(key))
                if self.columns_dict[key] == str:
                    recordValues.append(f"'{record[key]}'")
                else:
                    recordValues.append(str(record[key]))
            _sql = "INSERT " + ("OR IGNORE " if ignore else "OR REPLACE " if replace else "") + f"INTO [{self.name}] ({','.join(recordKeys)}) VALUES ({','.join(recordValues)})"
            with self.db.conn:
                self.db.execute(_sql)
        return self
    def drop(self, ignore=False):
        self.db._editableViews.pop(self.name)
        super().drop(ignore)
setattr(EditableView, "add_trigger", add_trigger_view)
setattr(EditableView, "remove_trigger", remove_trigger)
setattr(EditableView, "find", find)
setattr(EditableView, "printView", printView)

#database
class Database(dbDatabase):
    _editableViews = {}
    def joinCreate_EditableView(self, name: str, leftTable:Table, rightTable:Table, columns:Sequence[str], conditionSQLs:Union[str,Sequence[str]], deleteSQL:str=None,
                                insertSQL:str=None, updateSQL:str=None, method:Literal["LEFT","CROSS","INNER"]="INNER", defaults:Dict[str,Any]=None,
                                primaryKeys:Union[str,Sequence[str]]=None) -> EditableView:
        '''Create a view from two tables. If table name is not provided in columns, it will try to add automatically.'''
        _defaults = {} if defaults is None else defaults
        leftTableKeys = list(leftTable.columns_dict.keys())
        rightTableKets = list(rightTable.columns_dict.keys())
        _conditionSQLs = conditionSQLs if isinstance(conditionSQLs, (list, tuple)) else [conditionSQLs]
        _join = "LEFT OUTER" if method == "LEFT" else method
        _columns = []
        for column in columns:
            if "." not in column:
                if column in leftTableKeys:
                    _columns.append(f"{leftTable.name}.{column}")
                elif column in rightTableKets:
                    _columns.append(f"{rightTable.name}.{column}")
                else:
                    raise ValueError(f"Column {column} not found in either tables.")
            else:
                _columns.append(column)
        _sql = f"SELECT {','.join(_columns)} FROM {leftTable.name} {_join} JOIN {rightTable.name} ON {' AND '.join(_conditionSQLs)}"
        self.create_view(name, _sql)
        if primaryKeys:
            pks = primaryKeys if isinstance(primaryKeys, (list, tuple)) else [primaryKeys]
            for pk in pks:
                if pk not in leftTableKeys and pk not in rightTableKets:
                    pks.remove(pk)
        else:
            pks = list(dict.fromkeys(leftTable.pks + rightTable.pks))
            for pk in pks:
                if pk not in leftTableKeys and pk not in rightTableKets:
                    pks.remove(pk)
        view = EditableView(self, name, pks=pks, defaults=_defaults)
        self._editableViews[name] = view
        self.add_trigger(f"{name}_delete", "DELETE", view, deleteSQL) if deleteSQL is not None else None
        self.add_trigger(f"{name}_insert", "INSERT", view, insertSQL) if insertSQL is not None else None
        self.add_trigger(f"{name}_update", "UPDATE", view, updateSQL) if updateSQL is not None else None
        return view

    def add_trigger(self, name, event:Literal["INSERT","DELETE","UPDATE"], table:Union[dbTable, dbView],
                    command:str, time:Literal["BEFORE","AFTER"]="AFTER", column:str=None, if_not_exists:bool=False,
                    whenExpr:str=None):
        '''Time is ignored for view. Column is ignored for DELETE event.'''
        _sql = 'CREATE TRIGGER ' + ("IF NOT EXISTS " if if_not_exists else "") + f"{name} "
        _whenEpr = (f" WHEN {whenExpr}" if whenExpr is not None else "")
        _command = command + ";" if command[-1] != ";" else command
        if isinstance(table, dbTable):
            if column is None or event == "DELETE":
                self.execute(_sql + f"{time} {event} ON {table.name}{_whenEpr} FOR EACH ROW BEGIN {_command} END;")
            else:
                self.execute(_sql +f"{time} {event} OF {column} ON {table.name}{_whenEpr} BEGIN {_command} END;")
        elif isinstance(table, dbView):
            if column is None or event == "DELETE":
                self.execute(_sql+f"INSTEAD OF {event} ON {table.name}{_whenEpr} BEGIN {_command} END;")
            else:
                self.execute(_sql+f"INSTEAD OF {event} OF {column} ON {table.name}{_whenEpr} BEGIN {_command} END;")
        else:
            raise TypeError("table must be a Table or View")
    def remove_trigger(self, name):
        self.execute(f"DROP TRIGGER IF EXISTS {name};")
    def printTables(self):
        for table in self.tables:
            print("table:", table.name)
            for row in table.rows:
                print(row)
        print('-----------------')
    def table(self, *args, **kwargs) -> Union[Table, View, EditableView]:
        if args[0] in self._editableViews.keys():
            return self._editableViews[args[0]]
        return super().table(*args, **kwargs)
    def __getitem__(self, item)->Union[Table, View, EditableView]:
        return super().__getitem__(item)
    def hasTable(self, tableName: str) -> bool:
        return tableName in [t.name for t in self.tables]
    def setForeignKeyRestrict(self, set: bool):
        cursor = self.execute("PRAGMA foreign_keys = {};".format("ON" if set else "OFF"))
        cursor.close()
    def create_table(
        self,
        name: str,
        columns: Dict[str, Any],
        pk: Optional[Any] = None,
        foreign_keys: Optional[ForeignKeysType] = None,
        column_order: Optional[List[str]] = None,
        not_null: Iterable[str] = None,
        defaults: Optional[Dict[str, Any]] = None,
        hash_id: Optional[str] = None,
        hash_id_columns: Optional[Iterable[str]] = None,
        extracts: Optional[Union[Dict[str, str], List[str]]] = None,
        if_not_exists: bool = False,
        transform: bool = False,
        foreign_key_cascade: Optional[Union[str,Iterable[str]]] = None,
        autoincrement:  Optional[str] = None,
    ) -> Table:
        """
        Create a table with the specified name and the specified ``{column_name: type}`` columns.

        See :ref:`python_api_explicit_create`.

        :param name: Name of table
        :param columns: Dictionary mapping column names to their types, for example ``{"name": str, "age": int}``
        :param pk: String name of column to use as a primary key, or a tuple of strings for a compound primary key covering multiple columns
        :param foreign_keys: List of foreign key definitions for this table
        :param column_order: List specifying which columns should come first
        :param not_null: List of columns that should be created as ``NOT NULL``
        :param defaults: Dictionary specifying default values for columns
        :param hash_id: Name of column to be used as a primary key containing a hash of the other columns
        :param hash_id_columns: List of columns to be used when calculating the hash ID for a row
        :param extracts: List or dictionary of columns to be extracted during inserts, see :ref:`python_api_extracts`
        :param if_not_exists: Use ``CREATE TABLE IF NOT EXISTS``
        :param transform: If table already exists transform it to fit the specified schema
        :param foreign_key_cascade: List of columns that should be created as ``FOREIGN KEY`` with ``ON DELETE CASCADE`` and ``ON UPDATE CASCADE``
        :param autoincrement: primary key that should be created as ``AUTOINCREMENT``(must be of type ``int``)
        """
        # Transform table to match the new definition if table already exists:
        if transform and self[name].exists():
            table = cast(Table, self[name])
            should_transform = False
            # First add missing columns and figure out columns to drop
            existing_columns = table.columns_dict
            missing_columns = dict(
                (col_name, col_type)
                for col_name, col_type in columns.items()
                if col_name not in existing_columns
            )
            columns_to_drop = [
                column for column in existing_columns if column not in columns
            ]
            if missing_columns:
                for col_name, col_type in missing_columns.items():
                    table.add_column(col_name, col_type)
            if missing_columns or columns_to_drop or columns != existing_columns:
                should_transform = True
            # Do we need to change the column order?
            if (
                column_order
                and list(existing_columns)[: len(column_order)] != column_order
            ):
                should_transform = True
            # Has the primary key changed?
            current_pks = table.pks
            desired_pk = None
            if isinstance(pk, str):
                desired_pk = [pk]
            elif pk:
                desired_pk = list(pk)
            if desired_pk and current_pks != desired_pk:
                should_transform = True
            # Any not-null changes?
            current_not_null = {c.name for c in table.columns if c.notnull}
            desired_not_null = set(not_null) if not_null else set()
            if current_not_null != desired_not_null:
                should_transform = True
            # How about defaults?
            if defaults and defaults != table.default_values:
                should_transform = True
            # Only run .transform() if there is something to do
            if should_transform:
                table.transform(
                    types=columns,
                    drop=columns_to_drop,
                    column_order=column_order,
                    not_null=not_null,
                    defaults=defaults,
                    pk=pk,
                )
            return table
        sql = self.create_table_sql(
            name=name,
            columns=columns,
            pk=pk,
            foreign_keys=foreign_keys,
            column_order=column_order,
            not_null=not_null,
            defaults=defaults,
            hash_id=hash_id,
            hash_id_columns=hash_id_columns,
            extracts=extracts,
            if_not_exists=if_not_exists,
            foreign_key_cascade=foreign_key_cascade,
            autoincrement=autoincrement,
        )
        self.execute(sql)
        created_table = self.table(
            name,
            pk=pk,
            foreign_keys=foreign_keys,
            column_order=column_order,
            not_null=not_null,
            defaults=defaults,
            hash_id=hash_id,
            hash_id_columns=hash_id_columns,
        )
        return cast(Table, created_table)

    def create_table_sql(
            self,
            name: str,
            columns: Dict[str, Any],
            pk: Optional[Any] = None,
            foreign_keys: Optional[ForeignKeysType] = None,
            column_order: Optional[List[str]] = None,
            not_null: Optional[Iterable[str]] = None,
            defaults: Optional[Dict[str, Any]] = None,
            hash_id: Optional[str] = None,
            hash_id_columns: Optional[Iterable[str]] = None,
            extracts: Optional[Union[Dict[str, str], List[str]]] = None,
            if_not_exists: bool = False,
            foreign_key_cascade: Optional[Union[str,Iterable[str]]] = None,
            autoincrement:  Optional[str] = None,
    ) -> str:
        """
        Returns the SQL ``CREATE TABLE`` statement for creating the specified table.

        :param name: Name of table
        :param columns: Dictionary mapping column names to their types, for example ``{"name": str, "age": int}``
        :param pk: String name of column to use as a primary key, or a tuple of strings for a compound primary key covering multiple columns
        :param foreign_keys: List of foreign key definitions for this table
        :param column_order: List specifying which columns should come first
        :param not_null: List of columns that should be created as ``NOT NULL``
        :param defaults: Dictionary specifying default values for columns
        :param hash_id: Name of column to be used as a primary key containing a hash of the other columns
        :param hash_id_columns: List of columns to be used when calculating the hash ID for a row
        :param extracts: List or dictionary of columns to be extracted during inserts, see :ref:`python_api_extracts`
        :param if_not_exists: Use ``CREATE TABLE IF NOT EXISTS``
        :param foreign_key_cascade: List of foreign keys to cascade on delete and update
        :param autoincrement: primary key to be autoincremented(must be integer)
        """
        if hash_id_columns and (hash_id is None):
            hash_id = "id"
        foreign_keys = self.resolve_foreign_keys(name, foreign_keys or [])
        foreign_keys_by_column = {fk.column: fk for fk in foreign_keys}
        # any extracts will be treated as integer columns with a foreign key
        extracts = resolve_extracts(extracts)
        for extract_column, extract_table in extracts.items():
            if isinstance(extract_column, tuple):
                assert False
            # Ensure other table exists
            if not self[extract_table].exists():
                self.create_table(extract_table, {"id": int, "value": str}, pk="id")
            columns[extract_column] = int
            foreign_keys_by_column[extract_column] = ForeignKey(
                name, extract_column, extract_table, "id"
            )
        # Soundness check not_null, and defaults if provided
        not_null = not_null or set()
        defaults = defaults or {}
        assert columns, "Tables must have at least one column"
        assert all(
            n in columns for n in not_null
        ), "not_null set {} includes items not in columns {}".format(
            repr(not_null), repr(set(columns.keys()))
        )
        assert all(
            n in columns for n in defaults
        ), "defaults set {} includes items not in columns {}".format(
            repr(set(defaults)), repr(set(columns.keys()))
        )
        validate_column_names(columns.keys())
        column_items = list(columns.items())
        if column_order is not None:
            def sort_key(p):
                return column_order.index(p[0]) if p[0] in column_order else 999

            column_items.sort(key=sort_key)
        if hash_id:
            column_items.insert(0, (hash_id, str))
            pk = hash_id
        # Soundness check foreign_keys point to existing tables
        for fk in foreign_keys:
            if not any(
                    c for c in self[fk.other_table].columns if c.name == fk.other_column
            ):
                raise AlterError(
                    "No such column: {}.{}".format(fk.other_table, fk.other_column)
                )

        if foreign_key_cascade and type(foreign_key_cascade) is str:
            foreign_key_cascade = [foreign_key_cascade]
        column_defs = []
        # ensure pk is a tuple
        single_pk = None
        if isinstance(pk, list) and len(pk) == 1 and isinstance(pk[0], str):
            pk = pk[0]
        if isinstance(pk, str):
            single_pk = pk
            if pk not in [c[0] for c in column_items]:
                column_items.insert(0, (pk, int))
        for column_name, column_type in column_items:
            column_extras = []
            if column_name == single_pk:
                column_extras.append("PRIMARY KEY")
            if autoincrement and column_name == autoincrement and COLUMN_TYPE_MAPPING[column_type] == "INTEGER" and column_name == single_pk:
                column_extras.append("AUTOINCREMENT")
            if column_name in not_null:
                column_extras.append("NOT NULL")
            if column_name in defaults and defaults[column_name] is not None:
                column_extras.append(
                    "DEFAULT {}".format(self.quote(defaults[column_name]))
                )
            if column_name in foreign_keys_by_column:
                column_extras.append(
                    "REFERENCES [{other_table}]([{other_column}]){cascade}".format(
                        other_table=foreign_keys_by_column[column_name].other_table,
                        other_column=foreign_keys_by_column[column_name].other_column,
                        cascade=" ON DELETE CASCADE ON UPDATE CASCADE" if foreign_key_cascade and column_name in foreign_key_cascade else "",
                    )
                )
            column_defs.append(
                "   [{column_name}] {column_type}{column_extras}".format(
                    column_name=column_name,
                    column_type=COLUMN_TYPE_MAPPING[column_type],
                    column_extras=(" " + " ".join(column_extras)) if column_extras else "",
                )
            )
        extra_pk = ""
        if single_pk is None and pk and len(pk) > 1:
            extra_pk = ",\n   PRIMARY KEY ({pks})".format(
                pks=", ".join(["[{}]".format(p) for p in pk])
            )
        columns_sql = ",\n".join(column_defs)
        sql = """CREATE TABLE {if_not_exists}[{table}] (
{columns_sql}{extra_pk}
);
        """.format(
            if_not_exists="IF NOT EXISTS " if if_not_exists else "",
            table=name,
            columns_sql=columns_sql,
            extra_pk=extra_pk,
        )
        return sql

__all__ = ["Table", "Database", "View", "EditableView"]


