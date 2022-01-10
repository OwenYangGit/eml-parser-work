"""
轉換 eml 檔成 json
"""
from flanker import mime
import re

def eml_to_textpart(eml_path: str) -> str:
    """將 multi-part 種類的 eml 擷取出 text/plain 並將格式做一個簡單清洗然後以 str 返回
    
    :參數
        :type eml_path: str
        :param eml_path 傳入 lcoal 的 eml 單一檔案路徑

    :返回
        :type str
        :return 回傳整個 eml 內的 text/plain 部分，這個 str 會有 multi-line 的特性

    :流程
        將副檔名結尾為 .eml 檔案做讀取，非正規返回 "非合規的 EML" (避免接下來流程出錯)
        讀取 eml 的 part
        判斷為 text/plain part
        使用正則將所有的 space(空白) 取代成單一 space(空白)
        將多 empty lines 換成單一 empty line
        將 unicode \u3000(全形空白) 移除
    """
    if not eml_path.endswith(".eml"):
        print(eml_path + " 非合規的 EML 檔")
        return "非合規的 EML 檔"
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

    :參數
        :type multi_line_textpart: str
        :param multi_line_textpart: 經過 eml_to_textpart 方法清洗過的多行 str
    
    :返回
        :type: list
        :return 返回拆分 eml 不同人選過後的人選清單

    :流程
        先將多行的 str 以 "最後修改" 關鍵字轉成 textpart_list
        宣告一個 candidates 的 list
        遍歷這個 textpart_list , 將換行字符(\r\n)以 ',' 取代，並移除該字串最後 2 個 character(為了移除多的 ',')
        一個人做為一筆字串 , 塞入 persons 這個 list, 理論上 eml 裡面有幾個人 , 這個 persons 就有幾個 element
        移除 persons 的第一個 element(1111 固定的資料，無用)
        返回 persons
    """
    textpart_list = multi_line_textpart.split("最後修改")
    candidates = []
    for e in textpart_list:
        candidates.append(e.replace("\r\n",",")[:-2])
    candidates.pop(0)
    return candidates

def erase_messy_data_from_candidate_text(candidate_text: str) -> list:
    """將獨立一段 str 的 candidate str 傳入，透過判斷字段，將所需資料保留並存入 list 返回
    
    :參數
        :type candidate_text: str
        :param candidate_text: 傳入經過初步處理的單一個 candidate 字串，來源格式可以參考至 textpart_split_by_candidate 方法清洗出來後的 list 中任一 element
    
    :返回
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
        s = i.strip() # 確保先去除 str 中開頭和結尾的空白字符
        if "代碼" in i:
            candidate_info_list.append(s)
        elif "歲" in i:
            candidate_info_list.append(s)
        elif "聯絡電話" in i:
            candidate_info_list.append(s)
        elif "郵件" in i:
            candidate_info_list.append(s)
        elif "聯絡地址" in i:
            candidate_info_list.append(s)
        elif "教育程度" in i:
            candidate_info_list.append(s)
        elif "求職條件" in i:
            candidate_info_list.append(s)
        elif "期望產業" in i:
            candidate_info_list.append(s)
        elif "地點" in i:
            candidate_info_list.append(s)
        elif "工作經驗" in i:
            candidate_info_list.append(s)
        elif "累計經驗" in i:
            candidate_info_list.append(s)
        elif "期望薪資" not in i and  "可上班日" not in i and "年" in i:
            candidate_info_list.append(s)
        elif "期望薪資" not in i and "可上班日" not in i and "月" in i:
            candidate_info_list.append(s)
        elif "打字速度" not in i and "專長" in i:
            candidate_info_list.append(i)
        #elif "語言專長" in i:
            #candidate_info_list.append(s)
        #elif "打字速度" in i:
            #candidate_info_list.append(i)
    return candidate_info_list

def candidate_dict_from_list(candidate_list: list) -> dict:
    """將 erase_messy_data_from_candidate 輸出的單一 candidate list 洗成 dict，並給予對應欄位名稱
    
    :參數
        :type candidate_list: list
        :param candidate_list 從 erase_messy_data_from_candidate 清洗過後出來的資料，是一個 list , 裡面僅有單一 candidate 的資訊

    :返回
        :type dict
        :return 返回單一 candidate_dict，內容為一位 candidate 對應的 key:value，該欄位參考 雲育鏈實習生/002/002_Model

    :流程
        創建一個空 candidate_dict 的 dict
        創建一個空的 work_experience_data 的 list
        遍歷整個傳入的 candidate_list
        依照資料特殊關鍵字做判斷，處理對應的資料後，存入 candidate_dict 呼應的 key:value
        將對應的 key 與字段結合生成該 candidate 的 candidate_dict
        判斷過程中，若資料內不包含特定關鍵字(理論上是把只有 "年" or "月" 這兩個關鍵字)，視為工作經歷，將這些資料塞進 work_experience_data 的 list
        遍歷整個 work_experience_data，處理每個 element 的資料，並塞入對應的 candidate_dict["work_experience_list"] 的 list 內
        判斷所有 candidate_dict 每個欄位的 key 都有 value，若沒有，則塞入預設值
        返回 candidate_dict
    """
    candidate_dict = {}
    work_experience_data = []
    try:
        for e in candidate_list:
            if "代碼" in e:
                candidate_dict["id"] = e.split(" ")[2]
                candidate_dict["name"] = e.split(" ")[0]
            elif "歲" in e:
                if "男" in e:
                    candidate_dict["gender"] = "男"
                elif "女" in e:
                    candidate_dict["gender"] = "女"
                else:
                    candidate_dict["gender"] = "多元性別"
                age = int(e.split("|")[1].strip().split("歲")[0])
                candidate_dict["age"] = age
            elif "聯絡電話" in e:
                cell_phone_list = e.replace("聯絡電話","").replace(" ","").split("|")
                #candidate_dict["cell_phone"] = []
                for phone in cell_phone_list:
                    if phone.startswith("09"):
                        candidate_dict["cell_phone"] = phone
                        #candidate_dict["cell_phone"].append(phone)
            elif "電子郵件" in e:
                candidate_dict["email"] = e.split("電子郵件")[1].strip()
            elif "聯絡地址" in e:
                candidate_dict["address"] = e.split("聯絡地址")[1].strip()
            elif "教育程度" in e:
                edu_list = e.split(" ")
                candidate_dict["edu_level"] = edu_list[0][4:-2]
                candidate_dict["edu_status"] = edu_list[0][-2:]
                candidate_dict["edu_school"] = edu_list[1] + edu_list[2]
                candidate_dict["edu_department"] = edu_list[3].replace("(","").replace(")","")
            elif "職務類別" in e:
                wanted_job_title_list = e.replace("，","").strip().split(" ")
                candidate_dict["wanted_job_titles"] = []
                for i, title in enumerate(wanted_job_title_list):
                    if i >= 1:
                        candidate_dict["wanted_job_titles"].append(title)
            elif "期望產業" in e:
                wanted_job_type_list = e.replace("，","").strip().split(" ")
                candidate_dict["wanted_job_types"] = []
                for i, job_type in enumerate(wanted_job_type_list):
                    if i >= 1:
                        candidate_dict["wanted_job_types"].append(job_type)
            elif "上班地點" in e:
                wanted_job_locations_list = e.replace("，","").strip().split(" ")
                candidate_dict["wanted_job_locations"] = []
                for i, location in enumerate(wanted_job_locations_list):
                    if i >= 1:
                        candidate_dict["wanted_job_locations"].append(location)
            elif "工作經驗" in e:
                work_range = re.search("[0-9]+\~[0-9]+",e).group(0)
                # print(work_range)
                work_min_year = int(work_range.split("~")[0]) # 取得最小年份
                candidate_dict["working_months"] = work_min_year * 12
            elif "累計經驗" in e or "累計經驗" in e:
                work_exp_list = e.replace("累計經驗","").strip().split("|")
                candidate_dict["work_experiences"] = []
                for i in work_exp_list:
                    work_range = re.search("[0-9]+\~[0-9]+",i)
                    if work_range:
                        data = i.strip().split(" ")
                        candidate_dict["work_experiences"].append({
                            "title": data[0].strip(),
                            "duration": data[1].strip()
                        })
                    else:
                        candidate_dict["work_experiences"].append({
                            "title": i.strip(),
                            "duration": "無"
                        })
            elif "語文專長" in e:                
                langs_list = e.replace(" ","").split("[") # 將空白字符刪除，以 [ 作為切割字符
                langs_list.pop(0) # 去除第一個無用的 element
                candidate_dict["languages"] = []
                for i in langs_list:
                    lang = i.split("]")[0]
                    listen = i.split("|")[0][5:]
                    speak = i.split("|")[1][2:]
                    read = i.split("|")[2][2:]
                    write = i.split("|")[3][2:]
                    candidate_dict["languages"].append(
                        {
                            "language": lang,
                            "listen": listen,
                            "speak": speak,
                            "read": read,
                            "write": write
                        }
                    )
            elif "電腦專長" in e:
                candidate_dict["computer_expertises"] = []
                computer_expertise_list = e.replace("、","").strip().split(" ")
                computer_expertise_list.pop(0) # 去除第一個無用的 element
                for i in computer_expertise_list:
                    candidate_dict["computer_expertises"].append(i)
            else:
                work_experience_data.append(e.strip())
    except Exception as err:
        print(err)
            
        # 處理 work_experience_list 欄位
        try:
            if work_experience_data != []:
                candidate_dict["work_experience_list"] = []
                for i in work_experience_data:
                    work_experience_dict = {}
                    work_exp_company = i.split(" ",1)[0] # 以 str 中第一個空白字符切割，第 0 個 element 必定是公司名稱
                    work_exp_text = i.split(" ",1)[1].replace("（",",").replace("）","").replace("(",",").replace(" ","") # 以 str 中第一個空白字符切割後，取第 1 個 element，並將全形與半形的左括號 "(" 改為 "," 且移除空白字符
                    work_exp_list = work_exp_text.split(",") # 以 "," 作為切割符轉換成 list
                    work_experience_dict["title"] = work_exp_company + work_exp_list[0] # 公司名稱 + 職位 = title
                    work_experience_dict["duration"] = work_exp_list[1] # 第二個 element 必定為 duration
                    check_location = True
                    if len(work_exp_list[2].split(")")) == 1:
                        check_location = False
                    if check_location:
                        work_experience_dict["location"] = work_exp_list[2].split(")")[0]
                        work_experience_dict["date"] = work_exp_list[2].split(")")[1]
                    else:
                        work_experience_dict["date"] = work_exp_list[2].split(")")[0]
                    candidate_dict["work_experience_list"].append(work_experience_dict)
        except Exception as err:
            print(err)
        
    # 最後要判斷哪些 key 不存在，不存在要給預設值，暫時根據提供的文件非必填值做參考 -> "學歷/工作經歷/語言專長/電腦專長"都可能為空

    # 平台
    candidate_dict.setdefault("platform","1111")
    
    # 學歷
    candidate_dict.setdefault("edu_level","無")
    candidate_dict.setdefault("edu_status","無")
    candidate_dict.setdefault("edu_school","無")
    candidate_dict.setdefault("edu_department","無")

    # 工作月數
    candidate_dict.setdefault("working_months",999)

    # 工作年資
    candidate_dict.setdefault("work_experiences",[
        {
            "title": "無",
            "duration": "無"
        }
    ])
    
    # 工作經歷
    candidate_dict.setdefault("work_experience_list",[
        {
            "title": "無",
            "duration": "無",
            "location": "無",
            "date": "無"
        }
    ])
    
    # 語言專長
    candidate_dict.setdefault("languages",[
        {
            "language": "無",
            "listen": "無",
            "speak": "無",
            "read": "無",
            "write": "無"
        }
    ])
    
    # 電腦專長
    candidate_dict.setdefault("computer_expertises",["無"])

    return candidate_dict