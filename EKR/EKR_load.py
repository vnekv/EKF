import pandas
import sqlite3
from sqlite3 import Error
import numpy as np

DB_FILE = 'TKR_OOSP.db'
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
df = pandas.read_csv(CSV_FILE, sep=SEPARATOR, names=["conn_element_value", "measure_value", "measure_name"],
                     encoding=ENCODING,dtype={"measure_value": np.float64})
df['rank'] = df.groupby("measure_name")["measure_value"].rank(ascending=0)
df.to_sql('new_measure', conn, if_exists='replace', index=False)

measures = df.measure_name.unique().tolist()
c = conn.cursor()
c.execute('select name from measure')
old = []
for o in c.fetchall():
    old.append(o[0])
    print(o[0])
print(old)
for m in measures:
    if m not in old:
        print(m)
        cur = conn.cursor()
        cur.execute("insert into measure (name) values (?)", (m,))
conn.commit()

curs = conn.cursor()
c.execute("insert into data (id_conn_element_value, id_measure, measure_rank, measure_value) "
          "select cv.id, m.id, rank, measure_value from new_measure n left join measure m on measure_name = m.name "
          "left join conn_element_value cv on cv.name = n.conn_element_value")
conn.commit()
conn.close()

