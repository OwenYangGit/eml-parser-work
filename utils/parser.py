"""
轉換 eml 檔成 json
"""
from flanker import mime
from bs4 import BeautifulSoup
import re

def eml_to_textpart(eml_path: str) -> str:
    """將 multi-part 種類的 eml 擷取出 text/plain 並將格式做一個簡單清洗然後以 str 返回
    
    :type eml_path: str
    :param eml_path 傳入 lcoal 的 eml 單一檔案路徑

    :type str
    :return 回傳整個 eml 內的 text/plain 部分，這個 str 會有 multi-line 的特性

    :流程
    將 eml 讀取
    讀取 eml 的 part
    判斷為 text/plain part
    使用正則將所有的 space(空白) 取代成單一 space(空白)
    將多 empty lines 換成單一 empty line
    將 unicode \u3000(全形空白) 移除
    """
    with open(eml_path, "rb") as eml:
        raw_data = eml.read()
    email = mime.from_string(raw_data)
    for p in email.parts:
        if p.content_type == "text/plain":
            text_format = re.sub(" +"," ",p.body)
            result = re.sub(r'(\n\s*)+\n+', '\n', text_format).replace(u'\u3000',u'').replace(u' ▍',u'').replace(u'●',u'')
            return result
    
def textpart_split_by_candidate(multi_line_textpart: str) -> list:
    """eml 可能有多個人，將清洗過的 eml text/plain 字段傳入，拆分所有人放入 list 返回

    :type multi_line_textpart: str
    :param multi_line_textpart: 經過 eml_to_textpart 方法清洗過的多行 str
    
    :type: list
    :return 返回拆分 eml 不同人選過後的人選清單

    :流程
    先將多行的 str 以以 "最後修改" 關鍵字轉成 textpart_list
    遍歷這個 textpart_list , 將換行字符(\r\n)以 ',' 取代，並移除該字串最後 2 個 character(為了移除多的 ',')
    一個人做為一筆字串 , 塞入一個 persons , 理論上 eml 裡面有幾個人 , 這個 persons 就有幾個 element
    移除 persons 的第一個 element(1111 固定的資料，無用)
    返回 persons
    """
    textpart_list = multi_line_textpart.split("最後修改")
    persons = []
    for e in textpart_list:
        persons.append(e.replace("\r\n",",")[:-2])
    persons.pop(0)
    return persons

def erase_messy_data_from_candidate(candidate_text: str) -> list:
    """將獨立一段 str 的 candidate str 傳入，透過判斷字段，將所需資料保留並存入 list 返回
    
    :type candidate_text: str
    :param candidate_text: 傳入經過初步處理的單一個 candidate 字串，來源格式可以參考至 textpart_split_by_candidate 方法清洗出來後的 list 中任一 element
    
    :type list
    :return 返回 list，裡面存放該 candidate 的有效資訊，例如姓名、電話、學歷經歷等等

    :流程
    先將整個 str 透過 ',' 做為切割字符轉成 candidate_list
    遍歷整個 list 將有效資訊的資料作保留，存入一個 candidate_info_list
    返回 candidate_info_list
    """
    candidate_list = candidate_text.split(",")
    candidate_info_list = []
    for i in candidate_list:
        if "代碼" in i:
            candidate_info_list.append(i)
        elif "歲" in i:
            candidate_info_list.append(i)
        elif "電話" in i:
            candidate_info_list.append(i)
        elif "郵件" in i:
            candidate_info_list.append(i)
        elif "聯絡地址" in i:
            candidate_info_list.append(i)
        elif "教育程度" in i:
            candidate_info_list.append(i)
        elif "求職條件" in i:
            candidate_info_list.append(i)
        elif "期望產業" in i:
            candidate_info_list.append(i)
        elif "地點" in i:
            candidate_info_list.append(i)
        elif "工作經驗" in i:
            candidate_info_list.append(i)
        elif "年" in i:
            candidate_info_list.append(i)
        elif "月" in i:
            candidate_info_list.append(i)
        elif "專長" in i:
            candidate_info_list.append(i)
        elif "打字速度" in i:
            candidate_info_list.append(i)
    return candidate_info_list
        
    



def eml_to_html(eml_path: str) -> str:
    """
    判斷 eml 的 part 為 html 的字段取出 body 返回 , 型別是 str
    """
    with open(eml_path, "rb") as eml:
        raw_data = eml.read()
    email = mime.from_string(raw_data)
    for p in email.parts:
        if p.content_type == "text/html":
            return p.body

def html_to_json(body: str) -> list:
    soup = BeautifulSoup(body, "html.parser")
    tr_list = soup.table.table.find_all("tr")
    container = [] # 用來存放去除 html 標籤的中文字段 , 是由 list 組成
    
    # 測試轉 html
    # with open("test.html","w") as f:
    #     f.write(soup.prettify())

    for i in tr_list:
        # 將 html 標籤全部移除，留下中文字，並將這些中文字以 space(空格) 做切分轉為 list，並把特殊字元(符號)移除
        container.append(i.text.replace(" ","").replace('\u3000',"").replace('▍',"").splitlines())
    clear_list = list(filter(lambda x: x , container)) # 這邊輸出會變成 [[中文],[中文]] 的二維陣列，但每個 list in list 只會有 single element
    container.clear() # 清空 container，拿來放處理過的一維 list

    # 將二維陣列轉為一維，去除 list 0,1,-1 的 elem
    for n, i in enumerate(clear_list):
        if n > 1 and n != len(clear_list) - 1:
            container.append(i[0])

    # 以最後修改切割為 list
    container_cleaning_to_list = ",".join(container).split("最後修改")

    # 判斷字串過長的(超過 100)的移除 -> 可以保留我們要的資訊
    for i in container_cleaning_to_list:
        if(len(i) < 100):
            container_cleaning_to_list.remove(i)
    
    cv_data = [] # 存放每個人的資訊，都是一段字串
    
    # 有 "代碼" 在字串的裡面才保留
    for i in container_cleaning_to_list:
        if "代碼" in i:
            cv_data.append(i)
    
    container.clear() # 再次清空 conainer，要拿來存最後每個 person 的 list of dict
    # 解析 cv_data 的字串，每段字串都是一個人的完整 cv
    for i in cv_data:
        # 先將字串以 "," 做分割 -> 返回該字串 list
        person = i.split(",")
        d = {}
        # 整理要的欄位，對應塞入 d 字典
        for count , record in enumerate(person):  # 每一個元素給予標號
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
                    past_jobs = ",".join(person[count+1:]).split(",專長")[0]
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


        container.append(d)  # 將字典 d 放到 coll清單
    return container