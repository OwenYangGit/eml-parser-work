from os import listdir
from google.cloud import storage , bigquery
from utils import parser, unzip
from datetime import datetime
import sys , json

def eml_processor_func(event, context):

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

    # 建立 client
    storage_client = storage.Client()
    bigquery_client = bigquery.Client()

    # cloud storage bucket name
    cloud_storage_bucket = "user-bi-data-bucket"
    bucket = storage_client.bucket(cloud_storage_bucket)

    # 定義 cloud storage 物件的 prefix
    src_prefix = "candidates-zip-data/"
    cloud_storage_dest = "candidates-jsonl-data/"
    
    # 定義 bigquery 的 dataset 與 table
    bq_dataset = "user_bi_ds"
    bq_table = "user_bi_table"

    # 判斷是否 event type 是否為 google.storage.object.finalize，否則退出，代表檔案非完整上傳種類
    if context.event_type != "google.storage.object.finalize":
        print("來源資料非 google.storage.object.finalize type")
        sys.exit(0)

    # 判斷檔名是否為 .zip 結尾與 prefix 是否符合 src_prefix
    if event["name"].endswith('.zip') and src_prefix in event["name"]:
        src_blob = event["name"]
    else:
        print("來源資料不合規")
        sys.exit(0)

    # 宣告輸出檔名 - 以 年月日-時分秒.json 格式輸出
    t = datetime.now()
    dest_file = t.strftime("%Y%m%d-%H%M%S") + ".jsonl"

    # 下載 zip 檔，解壓縮至 /tmp/emls
    src_zipfile = bucket.blob(src_blob)
    src_zipfile.download_to_filename("/tmp/source.zip")
    unzip.decompress("/tmp/source.zip")

    # 讀取 /tmp/emls 目錄內的 eml 檔案，轉換成 jsonl，輸出到 /tmp 下，輸出路徑範例: /tmp/20220110-130101.json
    emls = listdir("/tmp/emls")
    tmp_output = "/tmp/" + dest_file
    with open(tmp_output,'a',encoding='utf-8') as fout:
        for eml in emls:
            # 解析 eml 轉成 str
            eml_textpart = parser.eml_to_textpart("/tmp/emls/" + eml)

            # 將解析完的 str 轉成 list，並依照 candidate 切分
            eml_candidate_list = parser.textpart_split_by_candidate(eml_textpart)

            # 處理每個 candidate，定義 candidate 欄位，使其最後的格式可以寫入 jsonl
            for candidate in eml_candidate_list:
                candidate_dict = {}
                candidate_list = parser.erase_messy_data_from_candidate_text(candidate)
                candidate_dict["id"] = parser.get_candidate_id(candidate_list)
                candidate_dict["name"] = parser.get_candidate_name(candidate_list)
                candidate_dict["gender"] = parser.get_candidate_gender(candidate_list)
                candidate_dict["age"] = parser.get_candidate_age(candidate_list)
                candidate_dict["cell_phone"] = parser.get_candidate_cellphone(candidate_list)
                candidate_dict["email"] = parser.get_candidate_email(candidate_list)
                candidate_dict["address"] = parser.get_candidate_address(candidate_list)
                edu = parser.get_candidate_edu(candidate_list)
                if edu:
                    candidate_dict["edu_level"] = edu["edu_level"]
                    candidate_dict["edu_status"] = edu["edu_status"]
                    candidate_dict["edu_school"] = edu["edu_school"]
                    candidate_dict["edu_department"] = edu["edu_department"]
                candidate_dict["wanted_job_titles"] = parser.get_candidate_wanted_job_titles(candidate_list)
                candidate_dict["wanted_job_types"] = parser.get_candidate_wanted_job_types(candidate_list)
                candidate_dict["wanted_job_locations"] = parser.get_candidate_wanted_job_locations(candidate_list)
                candidate_dict["working_months"] = parser.get_candidate_working_months(candidate_list)
                candidate_dict["work_experiences"] = parser.get_candidate_work_experiences(candidate_list)
                candidate_dict["languages"] = parser.get_candidate_languages(candidate_list)
                candidate_dict["computer_expertises"] = parser.get_candidate_computer_expertises(candidate_list)
                candidate_dict["work_experience_list"] = parser.get_candidate_work_experience_list(candidate_list)

                #if candidate_dict["computer_expertises"] == None or candidate_dict["computer_expertises"] == []:
                #    print(candidate)

                # 最後要判斷哪些 key 不存在，不存在要給預設值，暫時根據提供的文件非必填值做參考 -> "學歷/工作經歷/語言專長/電腦專長"都可能為空，電話號碼可能不是手機
                # 平台
                candidate_dict.setdefault("platform","1111")

                # 手機
                if not candidate_dict["cell_phone"]:
                    candidate_dict["cell_phone"] = "無"

                # 學歷
                candidate_dict.setdefault("edu_level","無")
                candidate_dict.setdefault("edu_status","無")
                candidate_dict.setdefault("edu_school","無")
                candidate_dict.setdefault("edu_department","無")

                # 工作月數
                candidate_dict.setdefault("working_months",999)

                # 工作年資
                if not candidate_dict["work_experiences"] or candidate_dict["work_experiences"] == []:
                    candidate_dict["work_experiences"] = [
                        {
                            "title": "無",
                            "duration": "無"
                        }
                    ]
                
                # 工作經歷
                if not candidate_dict["work_experience_list"] or candidate_dict["work_experience_list"] == []:
                    candidate_dict["work_experience_list"] = [
                        {
                            "title": "無",
                            "duration": "無",
                            "location": "無",
                            "date": "無"
                        }
                    ]
                
                # 語言專長
                if not candidate_dict["languages"] or candidate_dict["languages"] == []:
                    candidate_dict["languages"] = [
                        {
                            "language": "無",
                            "listen": "無",
                            "speak": "無",
                            "read": "無",
                            "write": "無"
                        }
                    ]
                
                # 電腦專長
                if not candidate_dict["computer_expertises"] or candidate_dict["computer_expertises"] == []:
                    candidate_dict["computer_expertises"] = ["無"]

                # 將整理好的單個 candidate 寫入 jsonl
                json.dump(candidate_dict, fout , ensure_ascii=False)
                fout.write("\n")

    # 上傳處理完成的 jsonl 檔案: tmp_output
    dest_blob = bucket.blob(cloud_storage_dest + dest_file)
    dest_blob.upload_from_filename(tmp_output)

    # 設定 bigquery 相關設定
    dataset_ref = bigquery_client.dataset(bq_dataset)
    table_ref = dataset_ref.table(bq_table)
    bq_job_config = bigquery.LoadJobConfig()
    bq_job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON

    # 載入 bigquery 需要的資料結構、建 view 的 query
    from schema import schema
    bq_job_config.schema = schema.bq_schema


    # 讀取 tmp_output 的 jsonl 檔案，將 data insert 到 bigquery table，並等待資料 insert 完成。
    with open(tmp_output, "rb") as source_file:
        job = bigquery_client.load_table_from_file(
            source_file,
            table_ref,
            job_config=bq_job_config,
        )
    job.result()

    # 建立 view 表，並等待建立完成
    bq_create_view = bigquery_client.query(schema.bq_view_query)
    bq_create_view.result()
    print("工作完成")