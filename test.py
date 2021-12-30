from flanker import mime
from bs4 import BeautifulSoup
from os import listdir
import json

def eml_to_json(my_eml):  # my_eml 是要讀取 (解析) 的 .eml 檔案
    with open(my_eml, 'rb') as fhdl:  # 開啟 eml 檔案
        raw_email = fhdl.read()  # 讀取 eml 檔案
    msg = mime.from_string(raw_email)  # mime.from_string 是用來解析 MIME 訊息的，eml 就是遵從 MIME  # 信件內容是屬於 multi-parts 多部份組成
    for part in msg.parts:  # 因為信件內容有分很多個 part，所以需一個一個部分取出
        container = []
        container2 = []
        if(part.content_type == "text/html"):   # 若有 part 的 content_type 是屬於 text/html 格式的 
            soup = BeautifulSoup(part.body, "html.parser")  # 使用 beautifilsoup 解析，跟爬蟲一樣
            res = soup.table.table  # 選出 table 標籤
            x = res.find_all("tr")  # 找出所有 tr 標籤，return ResultSet 是一種 list 的子類，可以遍歷  
            # print(type(x))
            for item in x:  # 遍歷 tr 標籤
                q = item.text.replace(" ","").replace('\u3000',"").replace('▍',"").splitlines()  # 取出 <tr>標籤 裡面的text 並將空格等的地方去掉，splitlines 的功能是 將有換行的以 list 格式列出
                container.append(q)  # 將每個 tr 清洗的結果放到 container
            v = list(filter(lambda x: x, container))  # 將列表為空的篩選掉，不知道怎麼做的
            v.pop()  # 移除 清單最後一個元素

            split_resumes = []
            coll = []
            for i in v:
                container2.append(i[0])   # 取出 v清單 每個元素去掉清單[]留下字串 並放到 container2 
            container2.pop(0) 
            container2.pop(0)  # 去掉 container2 清單前兩個元素
            container2.pop()  # 去掉 containe2 清單最後一個元素
            result = ','.join(container2)  # 將清單轉成字串，並用逗號隔開
            info = result.split("最後修改")  # 將字串轉成清單，並用 "最後修改"為分隔

            for s in info:
                if(len(s) < 100):  # 將 info 清單裡面的每個元素遍歷，字串超過100字的留下，少於100字的刪除  => 僅留下要取資料的字串 (裡面有我們要的姓名、性別、年齡...的資料)
                    info.remove(s)
            
            for x in info:
                record = x.split(",")  # 將清單中每個元素(都是字串)轉換成以","分隔的清單
                record.pop(0)  
                record.pop(0)  # 去掉前兩個元素
                split_resumes.append(record)
            mytest = list(filter(lambda y: y ,split_resumes))  # 再次移除掉空的清單，移除後剩兩個元素，都是清單
            for sub_list in mytest:
                d = {}
                if(len(sub_list[-1]) <= 5):
                    sub_list.pop()  # 移除掉清單中的最後一個元素 ''
                for count , record in enumerate(sub_list):  # 每一個元素給予標號
                    print(count, record)
                    d["platform"] = "1111"
                    if "代碼" in record:   # 以下皆為將資料放到 d 字典裏面                        
                        if "(９大職能星測評)" in record:
                            d["id"] = record.split("代碼")[1].split("(９大職能星測評)")[0]
                        else:
                            d["id"] = record.split("代碼")[1].split("完整履歷")[0]
                        d["name"] = record.split("代碼")[0]
                        if d["name"] == "":  # 如果姓名是空值，捨棄這個人的資料
                            break


                    if("男性" in record) or ("女性" in record):
                        d["gender"] = record.split("|")[0]
                    if "gender" not in d.keys():    # 如果字典裡沒有性別，代表沒有檢測到男性或女性，則為多元性別
                        d["gender"] = "多元性別"

                    if "歲" in record and "|" in record:  
                        d["age"] = int(record.split("|")[1].replace("歲", ""))
                        if d["age"] == "":  # 若年齡為空值...
                            d["age"] = 999
                    if "age" not in d.keys():  # 如果字典裡沒有年齡，代表沒有檢測到"歲"，則為"999歲"異常
                        d["age"] = 999

                    if "聯絡電話" in record:
                        cell_phones = []
                        phones = record.split("聯絡電話")[1].split("|")[:]                        
                        for cell_phone in phones:
                            if cell_phone.startswith("09"):
                                cell_phones.append(cell_phone)
                                d["cell_phone"] = cell_phones
                        if d["cell_phone"] == []:
                            d["cell_phone"] = "無"
                    if "cell_phone" not in d.keys():
                        d["cell_phone"] = "無"

                    if "電子郵件" in record:
                        d["email"] = record.split("電子郵件")[1]
                        if d["email"] == "":
                            d["email"] = "無"
                    if "email" not in d.keys():
                        d["email"] = "無"

                    if "聯絡地址" in record:
                        d["address"] = record.split("聯絡地址")[1]
                        if d["address"] == "":
                            d["address"] = "無"
                    if "address" not in d.keys():
                        d["address"] = "無"

                    if "教育程度" in record:
                        try:
                            department = record.split("(")[1]
                            d["edu_level"] = record.split("教育程度")[1][:2]
                            d["edu_status"] = record.split("教育程度")[1][2:4]
                            d["edu_school"] = record.split("教育程度")[1][4:].replace("("+department, "")
                            d["edu_department"] = department.replace(")", "")
                        except:
                            d["edu_level"] = "無"
                            d["edu_status"] = "無"
                            d["edu_school"] = "無"
                            d["edu_department"] = "無"

                    if "職務類別" in record:
                        d["wanted_job_title"] = record.split("職務類別")[1].split("，")[:]
                        if d["wanted_job_title"] == "" or d["wanted_job_title"] == []:
                            d["wanted_job_title"] = "無"
                    if "wanted_job_title" not in d.keys():
                        d["wanted_job_title"] = "無"

                    if "期望產業" in record:
                        d["wanted_jot_type"] = record.split("期望產業")[1].split("，")[:]
                        if d["wanted_jot_type"] == "" or d["wanted_jot_type"] == []:
                            d["wanted_jot_type"] = "無"
                    if "wanted_jot_type" not in d.keys():
                        d["wanted_jot_type"] = "無"

                    if "上班地點" in record:
                        d["wanted_job_location"] = record.split("上班地點")[1].split("，")[:]
                        if d["wanted_job_location"] == "" or d["wanted_job_location"] == []:
                            d["wanted_job_location"] = "無"
                    if "wanted_job_location" not in d.keys():
                        d["wanted_job_location"] = "無"


                    if "工作經驗累計年資" in record:
                        if "無工作經驗" not in record:
                            try:
                                work_min_year = int(record.split("工作經驗累計年資")[1].split("~")[0])
                                d["working_years"] = str(work_min_year * 12) + "月"
                                if d["working_years"] == "":
                                    d["working_years"] = "無"
                            except:
                                d["working_years"] = "待業中"
                        else:
                            d["working_years"] = "無工作經驗"
                    if "working_years" not in d.keys():
                        d["working_years"] = "無"

                    if "累計經驗" in record:
                        experiences = record.split("累計經驗")[1].split("|")
                        exp_l = []
                        job_list = []
                        for experience in experiences:
                            exp_d = {}
                            try:
                                exp_d["title"] = "".join([title for title in experience if not title.isdigit()]).replace("~", "").replace("年", "")
                                duration = [year for year in experience if year.isdigit()]
                                if len(duration) == 2:
                                    exp_d["duration"] = "~".join([year for year in experience if year.isdigit()]) + "年"
                                elif len(duration) == 3:
                                    exp_d["duration"] = duration[0] + duration[1] + "~" + duration[2] + "年"
                                else:
                                    exp_d["duration"] = duration[0] + duration[1] + "~" + duration[2] + duration[3] + "年"
                                exp_l.append(exp_d)
                            except:
                                exp_d["title"] = "".join([title for title in experience if not title.isdigit()]).replace("~", "").replace("年", "")
                                exp_d["duration"] = "無"
                                exp_l.append(exp_d)
                            d["work_experience"] = exp_l
                        if d["work_experience"] == "" or d["work_experience"] == [] or "work_experience" not in d.keys():
                            d["work_experience"] = "無"                        
                        
                        try:
                            past_jobs = ",".join(sub_list[count+1:]).split(",專長")[0]
                            past_jobs_list = past_jobs.split(",")
                            for job in past_jobs_list:
                                job_dict = {}
                                job_dict["title"] = job.split("（")[0] 
                                job_dict["duration"] = job.split("（")[1].split("）")[0]
                                job_dict["location"] = job.split("(")[1].split(")")[0]
                                job_dict["date"] = job.split(")")[1]
                                job_list.append(job_dict)
                            d["work_experience_list"] = job_list
                        except:
                            d["work_experience_list"] = "無"

                    if "語文專長" in record:
                        lang_list = []
                        for i in record.split("[")[1:]:
                            lan_dict = {}
                            lan_dict["language"] = i.split("]")[0]
                            lan_dict["listen"] = i.split("聽-")[1].split("|")[0]
                            lan_dict["speak"] = i.split("說-")[1].split("|")[0]
                            lan_dict["read"] = i.split("讀-")[1].split("|")[0]
                            lan_dict["write"] = i.split("寫-")[1]
                            lang_list.append(lan_dict)
                        d["languages"] = lang_list
                        if d["languages"] == "" or d["languages"] == []:
                            d["languages"] = "無"
                    if "languages" not in d.keys():
                        d["languages"] = "無"

                    if "電腦專長" in record:
                        d["computer_expertise"] = record.split("電腦專長")[1].split("、")
                        if d["computer_expertise"] == "" or d["computer_expertise"] == []:
                            d["computer_expertise"] = "無"
                    if "computer_expertise" not in d.keys():
                        d["computer_expertise"] = "無"


                coll.append(d)  # 將字典 d 放到 coll清單
            return coll  # coll 長相 [{...}]
        
# eml 擋存放目錄
mypath = "emls"
myoutput = "output.json"
# fieldnames = ['id', 'name', 'gender', 'age','cell_phone','email','address','教育程度','wanted_job_title', "wanted_jot_type", "wanted_job_location",'working_years','累計經驗','過往公司', "語文專長", "電腦專長"]

# 取的目錄下所有 eml 擋存入 list
files = listdir(mypath)  # 列出資料夾每個檔案的名字與檔案類型

# 讀擋並處理轉換 csv
for count , file in enumerate(files):
    print(file)
    result = eml_to_json(mypath + "/" + file)
    with open(myoutput, 'a', encoding="utf-8") as fout:
        json.dump(result, fout, ensure_ascii=False, indent=4)
    
    
    
    
    #     
    # break
