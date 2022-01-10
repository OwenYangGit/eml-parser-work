"""
處理壓縮檔 zipfile 的工具
"""
import zipfile
import os

def decompress(filename: str) -> bool:
    """傳入 zip 檔路徑，解壓縮後，將所有 eml 檔案按順序重命名 -> 0.eml ,1.eml, 2.eml 以此類推，成功解壓縮返回 True，否則返回 False

    :參數
        :type filename: str
        :prarm filename 來源資料 zip 檔的完整路徑
        
    :返回
        :type bool
        :return 返回是否成功解壓縮

    :流程
        定義輸出目錄
        判斷輸出目錄是否存在，否則創建
        判斷來源是否為 zip 檔，是的話開啟 zip 檔並解壓縮至輸出目錄
        重新將壓縮檔案內的檔名排序重新命名
        返回成功或失敗
    """
    try:
        output_dir = "/tmp/emls"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if zipfile.is_zipfile(filename):
            with zipfile.ZipFile(f"{filename}","r") as myzip:
                myzip.extractall(output_dir)
        # 將 eml 檔名統一格式
        for index, eml_file in enumerate(os.listdir(output_dir)):
            if eml_file.endswith(".eml"):
                os.rename(output_dir + "/" + eml_file, output_dir + "/" + str(index) + ".eml")
        return True
    except Exception:
        return False
