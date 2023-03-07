import pandas as pd
from db_connection import *
import glob
file_list=glob.glob(os.path.dirname(root_path) + "processing_data/{KeyFile}")

con,cur=db_connection()

def aggTransformer(valueCols={ValueCols}):
    df_event = pd.concat(pd.read_csv(file) for file in file_list)
    df_dimension = pd.read_sql('select {DimensionCols} from {DimensionTable}', con=con).drop_duplicates()
    string_cols = df_dimension.select_dtypes(include=['object']).columns
    df_dimension.update(df_dimension[string_cols].applymap("'{Values}'".format))
    event_dimension_merge = df_event.merge(df_dimension, on=['{MergeOnCol}'], how='inner')
    df_agg = event_dimension_merge.groupby({GroupBy}, as_index=False).agg({AggCols})
    col_list = df_agg.columns.to_list()
    df_snap = df_agg[col_list]
    df_snap.columns=valueCols
    print(df_snap)
    try:
         for index,row in df_snap.iterrows():
            values = []
            for i in valueCols:
              values.append(row[i])
            query = ''' INSERT INTO {TargetTable} As main_table({InputCols}) VALUES ({Values}) ON CONFLICT ({ConflictCols}) DO UPDATE SET {IncrementFormat};'''\
            .format(','.join(map(str,values)),{UpdateCol})
            print(query)
            cur.execute(query)
            con.commit()
    except Exception as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()

aggTransformer()

















