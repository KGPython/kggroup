from django.test import TestCase

# Create your tests here.
import pymysql
import sellcard.common.Method as mth
def executeTest():
    conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='root',db='test',charset='utf8mb4')
    # sql = 'insert into tb1 (name,age) values("name1",22)'
    slqUpdate = 'update tb1 set age=25 where name="name2"'
    cur = conn.cursor()
    # res = cur.execute(sql)
    res = cur.execute(slqUpdate)
    print(res)
executeTest()

def updateCard(list,mode):
    cards = "'"
    for obj in list:
        cards += str(obj)
        cards += "','"
    cards = cards[0:len(cards)-2]
    sql = "UPDATE guest SET Mode ='"+mode+"' WHERE CardNO in ("+cards+")"
    conn = mth.getMssqlConn()

    conn.autocommit(False)
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    if res is None:
        return 0
    else:
        return len(res)
print('test')