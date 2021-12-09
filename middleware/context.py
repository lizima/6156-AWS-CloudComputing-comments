
import os

# This is a bad place for this import
import pymysql

def get_db_info():
    """
    This is crappy code.

    :return: A dictionary with connect info for MySQL
    """
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)

    if db_host is not None:
        db_info = {
            "host": db_host,
            "user": db_user,
            "password": db_password,
            "cursorclass": pymysql.cursors.DictCursor
        }
    else:
        db_info = {
            "host": "sprint-hw1.c9u6tpsdswam.us-east-2.rds.amazonaws.com",
            "user": "teamnamenotfound",
            "password": "teamnamenotfound6156",
            "cursorclass": pymysql.cursors.DictCursor
        }

    return db_info

def get_context(api_name):
    if api_name == "SMARTY":
        auth_id = "55db43b6-6c8d-8af6-c1de-302bf949bc48"
        auth_token = "8zIBqRgihSDMg4fdjdW2"
        return {"auth_id":auth_id, "auth_token":auth_token}

