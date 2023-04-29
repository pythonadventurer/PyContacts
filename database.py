"""
PyContacts - a contact manager.
Copyright (C) 2023  Robert T. Fowler IV

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
import sqlite3
import csv
from config import *

def get_csv_data(csv_file):
    """
    file must have column names on first row.
    return columns and data separately, in a dict.
    """
    with open(csv_file,"r",encoding="utf-8") as f:
        reader=csv.reader(f)
        csv_data = [row for row in reader]
    columns = csv_data.pop(0)
    return {"columns":columns,"data":csv_data}

def create_table(db,table_name,columns):
    """
    columns = list of column names
    All columns except ID are text.
    """
    sql_create = f"CREATE TABLE {table_name}"

    # all tables get a primary key.
    sql_id = "(ID INTEGER PRIMARY KEY, "
    
    sql_cols = ""
    for col in columns:
        sql_cols += col + " TEXT"

        # add a comma for all columns except the last one
        if columns.index(col) < len(columns) - 1:
            sql_cols += ", "
    sql_cols += ");"    

    sql = sql_create + sql_id + sql_cols

    conn = sqlite3.connect(db)
    with conn:
        cur = conn.cursor()
        cur.execute(sql)

def insert_records(db,table_name,columns, data):

    sql_insert = f"INSERT INTO {table_name} ("
    sql_cols = ""
    for col in columns:
        sql_cols += col

        # add a comma for all columns except the last one
        if columns.index(col) < len(columns) - 1:
            sql_cols += ", "
    sql_cols += ") VALUES ("    
    sql_cols += "?, " * (len(columns) - 1)
    sql_cols += "?);"
    sql = sql_insert + sql_cols
    conn = sqlite3.connect(db)
    with conn:
        cur = conn.cursor()
        cur.executemany(sql, data)


data = get_csv_data("us-500.csv")
create_table(varDatabase, "contacts", data["columns"])
insert_records(varDatabase, "contacts", data["columns"], data["data"])


