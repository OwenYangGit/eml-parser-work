"""
處理壓縮檔 zipfile 的工具
"""
import zipfile
import os

def unzip(filename: str) -> bool:
    """
    傳入 zip 檔路徑，解壓縮後，將所有 eml 檔案按順序重命名 -> 0.eml ,1.eml, 2.eml 以此類推，成功解壓縮返回 True，否則返回 False
    """
    try:
        output_dir = "eml_output"
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
