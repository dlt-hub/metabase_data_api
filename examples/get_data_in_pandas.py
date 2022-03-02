import pandas as pd
from mbdata import MetabaseDataApi as M
import json

session_params = dict(user='adrian@scalevector.ai',
                      password='tester1.',
                      url='https://getdatateam.metabaseapp.com/'
                      )

mbapi = M(**session_params)

query = 'SELECT 12 as col'

#get raw file data via export
d = mbapi.export_from_query(query, database_id=4)

d = json.loads(d.decode("utf-8"))

df = pd.DataFrame.from_records(d)
print(df)
#   col
#0   12


#using the simple query method
d = mbapi.get_query_data(query, database_id=4)
print(d)
#[{'col': 12}]


d = mbapi.get_card_data(card_id='24')
print(d)
#[{'col': 12}]



