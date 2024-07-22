# -*- coding: utf-8 -*-
# @File    : sqlite.py
# @Author  : lajox
# @Email   : lajox@19www.com
# @Time    : 2024/5/4 14:17
# @Explain : sqlite数据库操作


import sqlite3


class Sqlite:

    def __init__(self, dbpath=''):
        self.dbpath = dbpath
        self.conn = sqlite3.connect(self.dbpath)
        self.cursor = self.conn.cursor()

    def _query_table(self, is_one=False, table='', fields='', where=None, order=None, limit=None, offset=None):
        fields = fields if fields else "*"
        if fields and isinstance(fields, list):
            fields = ", ".join([f"[{v}]" for v in fields])
        if where and isinstance(where, dict):
            where_items = []
            for key, value in where.items():
                where_items.append(f"[{key}]='{self.escape(value)}'" if isinstance(value, str) else f"[{key}]={value}")
            where = " AND ".join(where_items)
        if is_one:
            limit = 1
        where_str = f" AND {str(where)}" if where else ""
        order_str = f" ORDER BY {str(order)}" if order else ""
        limit_str = f" LIMIT {str(limit)}" if limit and limit > 0 else ""
        offset_str = f" OFFSET {str(offset)}" if offset else ""
        query_sql = f"SELECT {fields} FROM [{table}] where 1=1{where_str}{order_str}{limit_str}{offset_str}"
        self.cursor.execute(query_sql)
        if is_one:
            result = self.cursor.fetchone()
        else:
            result = self.cursor.fetchall()
        return result

    # 查询sqlite3表数据所有数据
    def query_table(self, table='', fields='', where=None, order=None, limit=None, offset=None):
        result = self._query_table(is_one=False, table=table, fields=fields, where=where, order=order, limit=limit, offset=offset)
        return result

    # 查询sqlite3表数据一条数据
    def query_one_table(self, table='', fields='', where=None, order=None, limit=None, offset=None):
        result = self._query_table(is_one=True, table=table, fields=fields, where=where, order=order, limit=limit, offset=offset)
        return result

    # 插入sqlite3表数据
    def insert_table(self, table, data={}):
        trans_values = []
        for key, value in data.items():
            trans_values.append(f"'{self.escape(value)}'" if isinstance(value, str) else f"{value}")
        # fields = ", ".join(data.keys())
        fields = ", ".join([f"[{v}]" for v in data.keys()])
        values = ", ".join(trans_values)
        insert_sql = f"INSERT INTO [{table}] ({fields}) VALUES ({values})"
        self.execute_sql(insert_sql)

    # 获取sqlite3上次插入记录id
    def get_last_insert_id(self):
        query_sql = f"SELECT last_insert_rowid()"
        self.cursor.execute(query_sql)
        result = self.cursor.fetchone()
        last_insert_id = result[0]
        return last_insert_id

    # 根据条件更新sqlite3表数据
    def update_table(self, table, data={}, where=None):
        update_items = []
        for key, value in data.items():
            update_items.append(f"[{key}]='{self.escape(value)}'" if isinstance(value, str) else f"[{key}]={value}")
        update_str = ", ".join(update_items)
        if where and isinstance(where, dict):
            where_items = []
            for key, value in where.items():
                where_items.append(f"[{key}]='{self.escape(value)}'" if isinstance(value, str) else f"[{key}]={value}")
            where = " AND ".join(where_items)
        where_str = f" AND {str(where)}" if where else ""
        update_sql = f"UPDATE [{table}] SET {update_str} WHERE 1=1{where_str}"
        self.execute_sql(update_sql)

    # 删除sqlite3表数据
    def delete_table(self, table, where=None):
        if where and isinstance(where, dict):
            where_items = []
            for key, value in where.items():
                where_items.append(f"[{key}]='{self.escape(value)}'" if isinstance(value, str) else f"[{key}]={value}")
            where = " AND ".join(where_items)
        where_str = f" AND {str(where)}" if where else ""
        delete_sql = f"DELETE FROM [{table}] WHERE 1=1{where_str}"
        self.execute_sql(delete_sql)

    # 查询表数据数量
    def count_table(self, table, where=None):
        if where and isinstance(where, dict):
            where_items = []
            for key, value in where.items():
                where_items.append(f"[{key}]='{self.escape(value)}'" if isinstance(value, str) else f"[{key}]={value}")
            where = " AND ".join(where_items)
        where_str = f" AND {str(where)}" if where else ""
        query_sql = f"SELECT COUNT(*) FROM [{table}] WHERE 1=1{where_str}"
        self.cursor.execute(query_sql)
        result = self.cursor.fetchone()
        count = result[0]
        return count

    # 清空重置sqlite3表
    def reset_table(self, table):
        self.execute_sql(f"DELETE FROM [{table}]")
        self.execute_sql(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{table}'")

    # 获取数据表所有字段信息
    def table_fields(self, table):
        query_sql = f"PRAGMA table_info({table})"
        self.cursor.execute(query_sql)
        result = self.cursor.fetchall()
        fields = {}
        # 获取每个字段的名称、类型等信息
        for row in result:
            field_name = row[1]  # 字段的名称
            data_type = row[2]  # 字段的类型
            fields[field_name] = data_type
        return fields

    def execute_sql(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()

    def escape(self, sql):
        sql = sql.replace("'", "''")
        return sql

    # 关闭sqlite3连接
    def close(self):
        self.cursor.close()
        self.conn.close()

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            pass
        pass
