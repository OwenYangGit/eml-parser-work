"""
轉換 eml 檔成 json
"""
from flanker import mime
import re
from bs4 import BeautifulSoup

def eml_to_html(eml_path: str):
    """將單一個 eml 檔轉換成 html

    Args:
        eml_path (str): 單一的 eml 檔案路徑

    Returns:
        void: 無返回，但在當前目錄下會生成一個 html 檔
        
    :流程
        1. 判斷是否為合規的 eml 檔，檔名必須為 .eml 結尾
        2. 解析 eml，擷取 part 為 text/html 的部分
        3. 生成 beautiful 物件解析該部分的 body
        4. 以 pretty 方式將 html 字段寫入 output.html 檔案
    """
    if not eml_path.endswith(".eml"):
        print(eml_path + " 非合規的 EML 檔")
        return "非合規的 EML 檔"
    with open(eml_path, "rb") as eml:
        raw_data = eml.read()
    email = mime.from_string(raw_data)
    for p in email.parts:
        if p.content_type == "text/html":
            html_format = BeautifulSoup(p.body, "html.parser")
            with open("output.html","w",encoding='utf-8') as fw:
                fw.write(str(html_format.prettify()))

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
        一個人做為一筆字串 , 塞入 persons 這個 list, 理論上 eml 裡面有幾個人 , persons(list) 就有幾個 element
        移除 persons 的第一個 element(1111 固定的資料，無用)
        返回 persons
    """
    textpart_list = multi_line_textpart.split("最後修改")
    candidates = []
    for e in textpart_list:
        candidates.append(e.replace(",","").replace("\r\n",",")[:-2])
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
        elif "郵件" in i and "聯絡時間" not in i:
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
        elif "語文專長" in i:
            candidate_info_list.append(s)
        elif "電腦專長" in i:
            candidate_info_list.append(s)
        #elif "打字速度" in i:
            #candidate_info_list.append(i)
    return candidate_info_list

def get_candidate_id(candidate_list: list) -> str:
    """取得 candidate 的 id 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        str: 平台產生出來的 id 字串
        
    :流程
        1. 遞迴整個 candidate_list，找到 element 裡含有 "代碼" 的
        2. 以 "代碼" 做切割，取第 1 個 element，將資料清洗成僅含有完整 id 的字段作返回
    """
    for i in candidate_list:
        if "代碼 " in i:
            candidate_id = i.split("代碼")[1].replace("(９大職能星測評)","").strip()
            return candidate_id

def get_candidate_name(candidate_list: list) -> str:
    """取得 candidate 的 name 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        str: canidate 的姓名
        
    :流程
        1. 遞迴整個 candidate_list，找到 element 裡含有 "代碼" 的
        2. 以 "代碼" 做切割，取第 0 個 element，將資料清洗成僅含有完整姓名的字段作返回
    """
    for i in candidate_list:
        if "代碼 " in i:
            candidate_name = i.split("代碼")[0].strip()
            return candidate_name

def get_candidate_gender(candidate_list: list) -> str:
    """取得 candidate 的 gender 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        str: canidate 的性別
        
    :流程
        1. 遞迴整個 candidate_list，找到 element 裡含有 "歲 " 的(注意有個空白，這是為了其它字段也含有"歲"這個字元時會造成判斷問題的一種避免方式)
        2. 判斷字段有 "男" 或 "女"，依照其結果做返回，若都不包含，返回多元性別
    """
    for i in candidate_list:
        if "歲 " in i:
            if "男" in i:
                return "男"
            elif "女" in i:
                return "女"
            else:
                return "多元性別"

def get_candidate_age(candidate_list: list) -> int:
    """取得 candidate 的 age 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        int: canidate 的年齡
        
    :流程
        1. 遞迴整個 candidate_list，找到 element 裡含有 "歲 " 的(注意有個空白，這是為了其它字段也含有"歲"這個字元時會造成判斷問題的一種避免方式)
        2. 依照其欄位特性，以 "|" 符號做切割，再以 "歲" 做切割，取第 0 個 element 並轉換成 int 型別返回
    """
    for i in candidate_list:
        if "歲 " in i:
            age = int(i.split("|")[1].strip().split("歲")[0])
            return age

def get_candidate_cellphone(candidate_list: list) -> str:
    """取得 candidate 的 cell_phone 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        str: candidate 的手機號碼
    
    :流程
        1. 遞迴整個 candidate_list，找到 "連絡電話 " 字段有在 element 的
        2. 將該 element 移除 "聯絡電話"，移除 " "(空格符號)，最後以 "|" 符號切割成 list
        3. 遞迴該 list，找到第一個 "09" 開頭的字段，將字段內的 "-" 符號移除，再返回
    """
    for i in candidate_list:
        if "聯絡電話 " in i:
            cell_phone_list = i.replace("聯絡電話","").replace(" ","").split("|")
            for phone in cell_phone_list:
                if phone.startswith("09"):
                    cell_phone = phone.replace("-","")
                    return cell_phone
    
def get_candidate_email(candidate_list: list) -> str:
    """取得 candidate 的 email 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        str: candidate 的電子郵件信箱帳號
        
    :流程
        1. 遞迴整個 candidate_list 找到 "電子郵件 " 有在 element 的
        2. 將該 element 以 "電子郵件" 切割成 list 取第 1 個 element，並移除字串的前後空白字元做返回
    """
    for i in candidate_list:
        if "電子郵件 " in i:
            email = i.split("電子郵件")[1].strip()
            return email

def get_candidate_address(candidate_list: list) -> str:
    """取得 candidate 的 address 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        str: candidate 的聯絡地址
        
    :流程
        1. 遞迴整個 candidate_list 找到 "聯絡地址 " 有在 element 的
        2. 將該 element 以 "聯絡地址" 切割成 list 取第 1 個 element，並移除字串的前後空白字元做返回
    """
    for i in candidate_list:
        if "聯絡地址 " in i:
            address = i.split("聯絡地址")[1].strip()
            return address

def get_candidate_edu(candidate_list: list) -> dict:
    """取得 candidate 的 edu_level、edu_status、edu_school、edu_department 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        dict: 返回包含有 edu_level/edu_status/edu_school/edu_department 欄位的字典
        
    :流程
        1. 遞迴整個 candidate_list 找到 "教育程度"(注意沒有空白) 有在 element 的
        2. 先將整個 element 以 " "(空白字元) 做切割轉成 list
        3. 依照每個 element 欄位特性，以字元段作判斷，抓出 edu_level/edu_status/edu_school/edu_department 的值
        4. 將上述抓取的值存放至 edu 字典做返回
    """
    for i in candidate_list:
        if "教育程度" in i:
            edu = {}
            edu_list = i.split(" ")
            edu["edu_level"] = edu_list[0][4:-2]
            edu["edu_status"] = edu_list[0][-2:]
            edu["edu_school"] = edu_list[1] + edu_list[2]
            edu["edu_department"] = edu_list[-1].replace("(","").replace(")","")
            return edu

def get_candidate_wanted_job_titles(candidate_list: list) -> list:
    """取得 candidate 的 wanted_job_titles 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        list: 返回 candidate 期望的職務類別清單
        
    :流程
        1. 遞迴整個 candidate_list 找到 "職務類別 " 有在 element 的
        2. 將 element 的空白字元/職務類別/求職條件字元做移除，在以 "，" 全形逗號做切割轉成 list
        3. 遞迴該 list，忽略第 0 個 element，以第 1 個 element(包含) 開始累加到一個空白 list
        4. 返回加總後的 list
    """
    for i in candidate_list:
        if "職務類別 " in i:
            wanted_job_title_list = i.replace(" ","").replace("職務類別","").replace("求職條件","").strip().split("，")
            wanted_job_titles = []
            for count, title in enumerate(wanted_job_title_list):
                if count >= 1:
                    wanted_job_titles.append(title)
            return wanted_job_titles

def get_candidate_wanted_job_types(candidate_list: list) -> list:
    """取得 candidate 的 wanted_job_types 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        list: 返回 candidate 的期望產業清單
        
    :流程
        1. 遞迴整個 candidate_list 找到 "期望產業 " 有在 element 的
        2. 將 element 的 "，" 移除，並移除前後空白字元，在以 " " 做切割轉成 list
        3. 遞迴該 list，忽略第 0 個 element，以第一個 element 開始累加到一個空白 list
        4. 返回加總後的 list
    """
    for i in candidate_list:
        if "期望產業 " in i:
            wanted_job_type_list = i.replace("，","").strip().split(" ")
            wanted_job_types = []
            for count, job_type in enumerate(wanted_job_type_list):
                if count >= 1:
                    wanted_job_types.append(job_type)
            return wanted_job_types
    
def get_candidate_wanted_job_locations(candidate_list: list) -> list:
    """取得 candidate 的 wanted_job_locations 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        list: 返回 candidate 的期望工作地
    
    :流程
        1. 遞迴整個 candidate_list 找到 "上班地點 " 有在 element 的
        2. 將 element 的 "，" 移除，並移除前後空白字元，在以 " " 做切割轉成 list
        3. 遞迴該 list，忽略第 0 個 element，以第一個 element 開始累加到一個空白 list
        4. 返回加總後的 list
    """
    for i in candidate_list:
        if "上班地點 " in i:
            wanted_job_locations_list = i.replace("，","").strip().split(" ")
            wanted_job_locations = []
            for count, location in enumerate(wanted_job_locations_list):
                if count >= 1:
                    wanted_job_locations.append(location)
            return wanted_job_locations

def get_candidate_working_months(candidate_list: list) -> int:
    """取得 candidate 的 working_months 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        int: 返回 candidate 的總工作月數
    
    :流程
        1. 遞迴整個 candidate_list 找到 "工作經驗 " 有在 element 的
        2. 以正則方式判斷字段中 [0-9]+~ 的規則字段，取出該字段，移除 "~" 符號並轉換成整數型別，此數字為年份，因此再將此數字 * 12 作為總工作月數
        3. 若不符合 2 中的規則，判斷 [0-9]+ 的規則字段，取出該字段，轉換成整數型別，在 * 12 作為總工作月數
        4. 若 2 與 3 的正則方式判斷規則皆不成立，則視為無工作經驗，因此總工作月數為 999
        5. 返回總工作月數變數 working_months
    """
    for i in candidate_list:
        if "工作經驗 " in i:
            if re.search(r'[0-9]+~',i):
                working_months = int(re.search(r'[0-9]+~',i).group(0).replace("~","")) * 12
            elif re.search(r'[0-9]+',i):
                working_months = int(re.search(r'[0-9]+',i).group(0)) * 12
            else:
                working_months = 999
            return working_months

def get_candidate_work_experiences(candidate_list: list) -> list:
    """取得 candidate 的 work_experiences 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        list: 返回 candidate 的累計經驗，會像 -> [{"title": "example", "duration": "1~2月"}, ...]
        
    :流程
        1. 遞迴整個 candidate_list 找到 "累計經驗 " 有在 element 的
        2. 將 element "累積經驗" 移除，移除前後空白字元，以 "|" 做切割轉成 list
        3. 遞迴該 list，以正則方式判斷符合 "[0-9]+\~[0-9]+" 規則的字段取出
        4. 創建空白 dict
        4. 判斷是否有符合規則的字段，若有則將其字段移除前後空白字元，在以 " " 做切割轉成 list 然後判斷該 list 是否有兩個欄位()，若有則代表可以洗出 title 和 duration，否則無 duration，塞入 dict
        5. 將 dict 累加到一個空白 list
        6. 返回加總完所有 dict 的 list
    """
    for i in candidate_list:
        if "累計經驗 " in i:
            work_exp_list = i.replace("累計經驗","").strip().split("|")
            work_experiences = []
            for work in work_exp_list:
                work_dict = {}
                work_range = re.search("[0-9]+\~[0-9]+",work)
                if work_range:
                    data = work.strip().split(" ")
                    if len(data) == 2:
                        work_dict = {
                            "title": data[0].strip(),
                            "duration": data[1].strip()
                        }
                    else:
                        continue
                else:
                    if work.strip() != "":
                        work_dict = {
                            "title": work.strip(),
                            "duration": "無"
                        }
                work_experiences.append(work_dict)
            return work_experiences

def get_candidate_languages(candidate_list: list) -> list:
    """取得 candidate 的 languages 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        list: 返回 candidate 的語文專長清單
        
    :流程
        1. 遞迴整個 candidate_list 找到 "語文專長"(注意沒有空白) 有在 element 的
        2. 移除 element 的空白字元，以 "[" 符號做切割轉成 list
        3. 移除該 list 的第 0 個 element(不會用到的)
        4. 生成一個空白 list
        4. 遞迴該 list，依照欄位特型，將 "]" 和 "|" 作為切割字，轉成 list 後取出對應的 element 並擷取字段中的字元，將其放入 dict(含有 language/listen/speak/read/write 的 key)
        5. 將 dict 累加到空白 list
        6. 返回加總所有 dict 後的 list
    """
    for i in candidate_list:
        if "語文專長" in i:
            langs_list = i.replace(" ","").split("[") # 將空白字符刪除，以 [ 作為切割字符
            langs_list.pop(0) # 去除第一個無用的 element
            languages = []
            for language in langs_list:
                lang = language.split("]")[0]
                listen = language.split("|")[0][5:]
                speak = language.split("|")[1][2:]
                read = language.split("|")[2][2:]
                write = language.split("|")[3][2:]
                languages.append(
                    {
                        "language": lang,
                        "listen": listen,
                        "speak": speak,
                        "read": read,
                        "write": write
                    }
                )
            return languages

def get_candidate_computer_expertises(candidate_list: list) -> list:
    """取得 candidate 的 computer_expertises 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        list: 返回 candidate 的電腦專長清單
        
    :流程
        1. 遞迴整個 candidate_list 找到 "電腦專長"(注意沒有空白) 有在 element 的
        2. 依序移除 element 中 "電腦專長" "專長" " "(空白字元)，並將 "、"(全形頓號)轉成 "，"(全形逗號)，在以 "，"(全形逗號) 做切割轉成 list
        3. 返回該 list
    """
    for i in candidate_list:
        if "電腦專長" in i:
            computer_expertises = i.replace("電腦專長","").replace("專長","").replace(" ","").replace("、","，").strip().split("，")
            computer_expertises = [x for x in computer_expertises if x]
            return computer_expertises

def get_candidate_work_experience_list(candidate_list: list) -> list:
    """取得 candidate 的 work_experience_list 欄位

    Args:
        candidate_list (list): 執行 erase_messy_data_from_candidate_text 方法後回傳的 list，每個 element 內容都為同一位 candidate 所有資訊

    Returns:
        list: 返回 candidate 的所有工作經歷清單
        
    :流程
        1. 宣告一個無用的關鍵字 list
        2. 判斷 candidate_list，將不含有無用關鍵字清單內的 element 累加到 work_experience_data(空白清單)
        3. 遞迴 work_experience_data 清單，建立一個 work_d 的空白字典
        4. 依照欄位特性，判斷若無 "（"(全形左括號) 的 element 就跳過該次迴圈執行
        5. 若有 "（"(全形左括號)，則依照欄位特型將 title/duration/location/date 欄位清洗出來並放入 work_d 字典
        6. 累加 work_d 字典到 work_experience_list(空白清單)
        7. 將累加完所有 work_d 字典的 work_experience_list 清單返回
    """
    unused_column = ["代碼 ","歲 ","聯絡電話 ","電子郵件 ","聯絡地址 ","教育程度","職務類別 ","期望產業 ","上班地點 ","工作經驗 ","聯絡時間","累計經驗 ","語文專長","電腦專長","打字速度"]
    work_experience_data = []
    work_experience_list = []
    for i in candidate_list:
        if i not in unused_column:
            work_experience_data.append(i)
    try:
        for work in work_experience_data:
            work_d = {}
            if "（" not in work:
                continue
            work_part1 = work.split("（")[0].strip()
            work_part2 = work.split("（")[1].strip()
            work_d["title"] = work_part1
            if '~' in work_part2:
                da = work_part2.replace("）","").split("(")[0].replace(" ","")
                lo = work_part2.replace("）","").split("(")[1].split(")")[0].strip()
                du = work_part2.replace("）","").split("(")[1].split(")")[1].replace(" ","").strip()
                work_d["duration"] = du
                if lo != "":
                    work_d["location"] = lo
                else:
                    work_d["location"] = "無"
                work_d["date"] = da
            else:
                da = work_part2.replace("）","").replace(" ","")
                lo = "無"
                du = "無"
                work_d["duration"] = du
                work_d["date"] = da
                work_d["location"] = lo
            work_experience_list.append(work_d)
        return work_experience_list
    except Exception as err:
        print(err)
        #print(err.with_traceback())