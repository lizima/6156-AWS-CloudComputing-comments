import pymysql
import json
import logging
import sys
import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# pagination: max limit - 20
#             offset

class RDBService:

    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):

        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        try:
            db_connection = pymysql.connect(
               **db_info,
                autocommit=True
            )
        except Exception as e:
            raise e
        return db_connection

    @classmethod
    def run_sql(cls, sql_statement, args, fetch=False):

        res, _ = RDBService.cursor_exec(sql_statement, args, fetch)
        return res

    @classmethod
    def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):

        sql = "select * from " + db_schema + "." + table_name + " where " + \
            column_name + " like " + "'" + value_prefix + "%'"

        res = RDBService.cursor_exec(sql, args=None, fetch=True, print_stmt=True, exception_on=True)

        return res

    @classmethod
    def _get_where_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:

            for k,v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " +  " AND ".join(terms)

        return clause, args

    @classmethod
    def list_str(cls, field_list):
        res = ""
        for c in field_list:
            res += '`' + c + '`,'
        return res[:-1]

    @classmethod
    def find_by_template(cls, db_schema, table_name, template, limit=None, offset=None, field_list=None):

        wc,args = RDBService._get_where_clause_args(template)

        if field_list is None:
            sql = "select * from " + db_schema + "." + table_name + " " + wc + " " + \
                "limit " + str(limit) + " " + "offset " + str(offset)
        else:
            sql = "select " + RDBService.list_str(field_list) + " from " + db_schema + "." + table_name + " " + wc
            if limit is None and offset is None:
                pass
            elif limit is not None and offset is not None:
                sql += " " + "limit " + str(limit) + " " + "offset " + str(offset)
            # sql = "select " + RDBService.list_str(field_list) + " from " + db_schema + "." + table_name + " " + wc \
            #       + " " + "limit " + str(limit) + " " + "offset " + str(offset)
        res, exception_res = RDBService.cursor_exec(sql, args=args, fetch=True, print_stmt=False, exception_on=True)

        return res, exception_res

    @classmethod
    def find_linked_data(cls, db_schema, table1_name, table2_name, target, template, key):
        wc, args = RDBService._get_where_clause_args(template)
        # key = list(template.keys())[0]

        sql = "select * from " + db_schema + "." + table1_name + " where " + target + "=(select " + key + " from "\
              + db_schema + "." + table2_name + wc + ")"

        res, exception_res = RDBService.cursor_exec(sql, args=args, fetch=True, print_stmt=False, exception_on=True)
        return res, exception_res

    @classmethod
    def create(cls, db_schema, table_name, create_data):

        cols = []
        vals = []
        args = []

        for k,v in create_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)

        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        sql_stmt = "insert into " + db_schema + "." + table_name + " " + cols_clause + \
            " " + vals_clause

        res, exception_res = RDBService.processed_rsp(sql_stmt, args)
        return res, exception_res

    @classmethod
    def update(cls, db_schema, table_name, select_data, update_data):

        select_clause, select_args = RDBService._get_where_clause_args(select_data)

        cols = []
        args = []

        for k, v in update_data.items():
            cols.append(k + "=%s")
            args.append(v)
        clause = "set " + ", ".join(cols)
        args = args + select_args

        sql_stmt = "update " + db_schema + "." + table_name + " " + clause + \
                   " " + select_clause

        res, exception_res = RDBService.processed_rsp(sql_stmt, args)
        return res, exception_res

    @classmethod
    def delete(cls, db_schema, table_name, template):
        clause, args = RDBService._get_where_clause_args(template)
        sql_stmt = "delete from " + db_schema + "." + table_name + " " + clause
        res, exception_res = RDBService.processed_rsp(sql_stmt, args)
        return res, exception_res

    @classmethod
    def cursor_exec(cls, sql_stmt, args, fetch=False, print_stmt=False, exception_on=False):
        res = None
        conn = None
        try:
            conn = RDBService._get_db_connection()
            cur = conn.cursor()
            if print_stmt:
                print("SQL Statement = " + cur.mogrify(sql_stmt, args))
            res = cur.execute(sql_stmt, args=args)
            if fetch:
                res = cur.fetchall()
            conn.close()
        except Exception as e:
            if conn is None:
                pass
            else:
                conn.close()
            if exception_on:
                exc_type, exc_value, exc_traceback_obj = sys.exc_info()
                return res, (exc_type.__module__ + '.' + exc_type.__name__, e.args)
            else:
                raise e

        return res, None

    @classmethod
    def processed_rsp(cls, sql_stmt, args):
        res = None
        try:
            res = RDBService.run_sql(sql_stmt, args)
        except Exception as e:
            exc_type, exc_value, exc_traceback_obj = sys.exc_info()
            return res, (exc_type.__module__ + '.' + exc_type.__name__, e.args)
        return res, None

    @classmethod
    def find_linked_user(cls, user_schema, comment_schema, user_table, comment_table, template):
        wc, args = RDBService._get_where_clause_args(template)
        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        target_id = f'select {comment_schema}.{comment_table}.user_id from {comment_schema}.{comment_table} {wc}'
        sql = f'select * from {user_schema}.{user_table} where {user_schema}.{user_table}.id = ({target_id})'
        print(sql)
        print(args)
        res = cur.execute(sql, args)
        res = cur.fetchall()

        conn.close()

        return res
