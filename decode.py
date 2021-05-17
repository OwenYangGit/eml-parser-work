from flanker import mime
from bs4 import BeautifulSoup
from os import listdir
import csv

def eml_to_list(my_eml):
    with open(my_eml, 'rb') as fhdl:
        raw_email = fhdl.read()
    msg = mime.from_string(raw_email)
    for part in msg.parts:
        container = []
        container2 = []
        if(part.content_type == "text/html"):
            soup = BeautifulSoup(part.body, "html.parser")
            res = soup.table.table
            x = res.find_all("tr")
            print(type(x))
            for item in x:
                q = item.text.replace(" ","").replace('\u3000',"").replace('▍',"").splitlines()
                container.append(q)
            v = list(filter(lambda x: x, container))
            v.pop()
            resumes = []
            split_resumes = []
            coll = []
            for i in v:
                container2.append(i[0])
            container2.pop(0)
            container2.pop(0)
            container2.pop()
            result = ','.join(container2)
            info = result.split("最後修改")
            for s in info:
                if(len(s) < 100):
                    info.remove(s)
            for i in info:
                resumes.append(i.split("專長")[0])
            for x in resumes:
                record = x.split(",")
                record.pop(0)
                record.pop(0)
                split_resumes.append(record)
            mytest = list(filter(lambda y: y ,split_resumes))
            for sub_list in mytest:
                d = {}
                if(len(sub_list[-1]) <= 5):
                    sub_list.pop()
                for count , record in enumerate(sub_list):
                    if "代碼" in record:
                        d["姓名"] = record.split("代碼")[0]
                    if("男" in record) or ("女" in record):
                        d["性別"] = record.split("|")[0]
                        d["年齡"] = record.split("|")[1]
                    if "聯絡電話" in record:
                        d["聯絡電話"] = record.split("聯絡電話")[1]
                    if "電子郵件" in record:
                        d["電子郵件"] = record.split("電子郵件")[1]
                    if "聯絡地址" in record:
                        d["聯絡地址"] = record.split("聯絡地址")[1]
                    if "教育程度" in record:
                        d["教育程度"] = record.split("教育程度")[1]
                    if "職務類別" in record:
                        d["求職類別"] = record.split("職務類別")[1]
                    if "工作經驗累計年資" in record:
                        d["累計年資"] = record.split("工作經驗累計年資")[1]
                    if "累計經驗" in record:
                        d["累計經驗"] = record.split("累計經驗")[1]
                        d["過往公司"] = ",".join(sub_list[count+1:])
                coll.append(d)
            return coll

# 開啟即將寫入的 csv
with open('output.csv', 'w', newline='') as csvfile:
  # 定義欄位
  fieldnames = ['姓名', '性別', '年齡','聯絡電話','教育程度','職務類別','工作經驗累計年資','累計經驗','過往公司']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

# eml 擋存放目錄
mypath = "emls"

# 取的目錄下所有 eml 擋存入 list
files = listdir(mypath)

# 讀擋並處理轉換 csv
for file in files:
    result = eml_to_list(file)
    for i in result:
        writer.writerow(i)