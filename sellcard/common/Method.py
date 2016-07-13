__author__ = 'admin'
import pymssql
from sellcard.common import Constants
def getMssqlConn(as_dict=True):
    conn = pymssql.connect(host=Constants.SCM_DB_SERVER,
                           port=Constants.SCM_DB_PORT,
                           user=Constants.SCM_DB_USER,
                           password=Constants.SCM_DB_PASSWORD,
                           database=Constants.SCM_DB_DATABASE,
                           charset='utf8',
                           as_dict=as_dict)
    return conn