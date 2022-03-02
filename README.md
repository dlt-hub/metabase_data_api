# Usage
This is a python package meant to query metabase datasources via api.

install the package:
`pip install mbdata`

usage:

```
import pandas as pd
from metabase_data_api import MetabaseApi as M
import json

session_params = dict(user='name@company.ai',
                      password='demopass1',
                      url='https://yourteam.metabaseapp.com/'
                      )

mb_api = M(**session_params)

query = 'SELECT 12 as col'

#get raw file data via export
d = mb_api.export_from_query(query, database_id=4)

json.loads(d.decode("utf-8"))

df = pd.DataFrame.from_records(d)


print(df)
#   col
#0   12
```


# Limits
The get_ methods are calling the same endpoints that are used by metabase for its own charting and are limited to 2k rows of results

The export method uses the file download functionality which is limited to 1m rows.
