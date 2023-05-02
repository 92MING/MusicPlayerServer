from sqlite_utils import Database
import os
db = Database("test.db", recreate=True)
dogTable = db.create_table("dogs", {"id": int, "name": str, "age": int}, pk="id", if_not_exists=True)
dogTable.enable_fts(["name"], create_triggers=True)
dogTable.insert_all([
    {"id": 1, "name": "ABC, ED", "age": 4},
    {"id": 2, "name": "AABC", "age": 2},
    {"id": 3, "name": "EFG", "age": 7}
])
print(dogTable.find('name', 'LIKE', 'A%', toTuple=True))
