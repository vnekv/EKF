import pandas
import sqlite3
from sqlite3 import Error
import numpy as np

DB_FILE = 'EKR_PROD.db'
CSV_FILE = 'health.csv'
SEPARATOR = ';'
ENCODING = "cp1250"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


conn = create_connection(DB_FILE)
df = pandas.read_csv(CSV_FILE, sep=SEPARATOR, names=["conn_att_category", "ea_value", "ea_name"],
                     encoding=ENCODING,dtype={"ea_value": np.float64})
df['rank'] = df.groupby("ea_name")["ea_value"].rank(ascending=0)
df.to_sql('new_ea', conn, if_exists='replace', index=False)

eas = df.ea_name.unique().tolist()
c = conn.cursor()
c.execute('select name from ea')
old = []
for o in c.fetchall():
    old.append(o[0])
    print(o[0])
print(old)
for m in eas:
    if m not in old:
        print(m)
        cur = conn.cursor()
        cur.execute("insert into ea (name) values (?)", (m,))
conn.commit()

curs = conn.cursor()
c.execute("insert into item_ea (id_conn_att_category, id_ea, ea_rank, ea_value) "
          "select cv.id, m.id, rank, ea_value from new_ea n left join ea m on ea_name = m.name "
          "left join conn_att_category cv on cv.name = n.conn_att_category")
conn.commit()
conn.close()

