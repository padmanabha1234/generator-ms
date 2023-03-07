import pandas as pd
from db_connection import *
import glob
file_list=glob.glob(os.path.dirname(root_path) + "processing_data/{KeyFile}")
con,cur=db_connection()

def aggTransformer(valueCols={ValueCols}):
    df_event = pd.concat(pd.read_csv(file) for file in file_list)
    {DateList}
    {YearList}
    df_dataset = pd.read_sql('select * from {Table};', con=con)
    dataset_string_cols = df_dataset.select_dtypes(include=['object']).columns
    df_dataset.update(df_dataset[dataset_string_cols].applymap("'{Values}'".format))
    {DateFilter}
    {YearFilter}
    df_dimension = pd.read_sql('select {DimensionCols} from {DimensionTable}', con=con).drop_duplicates()
    dimension_string_cols = df_dimension.select_dtypes(include=['object']).columns
    df_dimension.update(df_dimension[dimension_string_cols].applymap("'{Values}'".format))
    event_dimension_merge = df_event.merge(df_dimension, on=['{MergeOnCol}'], how='inner')
    event_dimension_merge = event_dimension_merge.groupby({GroupBy}, as_index=False).agg({AggCols})
    event_dimension_merge['{RenameCol}'] = event_dimension_merge['{eventCol}']
    merge_col_list = []
    for i in event_dimension_merge.columns.to_list():
        if i in df_dataset.columns.to_list():
            merge_col_list.append(i)
    df_agg = event_dimension_merge.merge(df_dataset, on=merge_col_list, how='inner')
    df_agg['percentage'] = ((df_agg['count_category_wise_schools'] / df_agg['count_school_statistics_total_schools']) * 100)  ### Calculating Percentage
    df_snap = df_agg[valueCols]
    print(df_snap)
    try:
         for index,row in df_snap.iterrows():
            values = []
            for i in valueCols:
              values.append(row[i])
            query = ''' INSERT INTO {TargetTable}({InputCols}) VALUES ({Values}) ON CONFLICT ({ConflictCols}) DO UPDATE SET {ReplaceFormat};'''\
            .format(','.join(map(str,values)))
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
