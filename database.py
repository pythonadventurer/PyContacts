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
from pathlib import Path

def get_csv_data(csv_file):
    """
    file must have column names on first row.
    return columns and data separately, in a dict.
    """
    csv_file = Path(csv_file)
    table_name = csv_file.stem

    with open(csv_file,"r",encoding="utf-8") as f:
        reader=csv.reader(f)
        csv_data = [row for row in reader]
    
    columns_row = csv_data.pop(0)
       

    return {"name":table_name, "columns":columns_row,"data":csv_data}


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

def get_table_columns(db,table_name):
    """
    return a list of the column names and 
    maximum widths from a table
    """
    sql = f"SELECT * FROM pragma_table_info('{table_name}')"
    conn = sqlite3.connect(db)
    with conn:
        cur = conn.cursor()
        cur.execute(sql)
        pragma =  cur.fetchall()
   
    column_names = [col[1] for col in pragma]
    table_data = query_all(db, table_name)

    columns = {}

    # Get max column widths based on content
    for column in column_names:
        max_width = 0
        for row in table_data:
            if len(str(row[column_names.index(column)])) > max_width:
                max_width = len(str(row[column_names.index(column)]))
        columns[column] = max_width
    return columns

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

def query_all(db,table_name):
    sql = f"SELECT * FROM {table_name};"
    conn = sqlite3.connect(db)
    with conn:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
    return data

def update_record(db,table_name,record_id,row):
    """
    row = list of values for the update.
    all rows get updated, even if there is no change.
    """
    columns = get_table_columns(db, table_name)
    sql_update = f"UPDATE {table_name} SET "
    sql_columns = ""
    for n in range(1,len(columns)):
        sql_columns += columns[n] + " = '" + row[n-1] + "'"        
        if n < len(columns) - 1:
            sql_columns += ", "
    sql_columns += " "
    sql_where = "WHERE ID = " + str(record_id) + ";"
    sql = sql_update + sql_columns + sql_where
    conn = sqlite3.connect(db)
    with conn:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

def delete_record(db,table_name,record_id):
    sql_delete = f"DELETE FROM {table_name} WHERE ID = {record_id};"
    conn = sqlite3.connect(db)
    with conn:
        cur = conn.cursor()
        cur.execute(sql_delete)
        conn.commit() 
