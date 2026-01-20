import psycopg2

conn = psycopg2.connect('postgresql://postgres:1234@localhost:5432/telegram')
cur = conn.cursor()
cur.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_name='stg_image_detections';")
print('tables:', cur.fetchall())
cur.execute('SELECT count(*) FROM public.stg_image_detections')
print('rows:', cur.fetchone()[0])
cur.close()
conn.close()
