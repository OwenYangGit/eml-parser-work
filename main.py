from google.cloud import storage , bigquery
from utils import parser , unzip

def candidate_processor_func(event, context):
    
    """將人才資料檔案 eml 轉換成 jsonl 檔案存入 cloud storage 並且將對應 data 塞入 bigquery 且建立 view 表

    Args:
        event (dict):  來自 cloud storage pub/sub notification 觸發的 event 資料，主要用來取出多個 eml 的 zip 壓縮檔作為資料來源
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Stackdriver Logging
    """
    print('Event ID: {}'.format(context.event_id))
    print('Event type: {}'.format(context.event_type))
    print('Bucket: {}'.format(event['bucket']))
    print('File: {}'.format(event['name']))
    print('Updated: {}'.format(event['updated']))

    storage_client = storage.Client()
    bigquery_client = bigquery.Client()

    # 定義 cloud storage 來源與輸出
    cloud_storage_src = "user-bi-data-bucket/candidates-zip_data"
    cloud_storage_dest = "user-bi-data-bucket/candidates-jsonl_data"
    
    # 定義 bigquery 的 dataset 與 table
    bq_dataset = "user_bi_ds"
    bq_table = "user_bi_table"

    # 定義來源檔名限制，定義輸出檔名
    if event["name"].endswith('.zip'):
        src_file = event["name"]
    dest_file = datetime.fromisoformat(event["updated"]).strftime("%Y%m%d-%H%M%S") + ".json"
    
    
# [END functions_helloworld_storage]

# Must export GOOGLE_APPLICATION_CREDENTIALS
# gcs_client = storage.Client()
# result = gcs_client.list_buckets()
# for b in result:
#     print(b)
#     print(type(b))

#from utils import unzip

#unzip.unzip("test.zip")
from datetime import datetime
t = "2021-12-28T09:45:28.410Z"
print(datetime.now())
print(datetime.fromisoformat(t[:-1]))
x = datetime.fromisoformat(t[:-1])
z = x.strftime("%Y%m%d-%H%M%S")
print(z)
print(type(z))

from utils import parser
"""
讀取單檔 eml
"""
result = parser.eml_to_textpart("eml_output/6.eml")
result2 = parser.textpart_split_by_candidate(result)
for person in result2:
    print("-----")
    candidate_list = parser.erase_messy_data_from_candidate_text(person)
    print(parser.candidate_dict_from_list(parser.erase_messy_data_from_candidate_text(person)))

#a = parser.erase_messy_data_from_candidate_text(result2[0])
#print(a)