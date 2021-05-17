## 準備作業
1. 會針對名稱為 "emls" 的目錄做讀取
2. "emls" 目錄下僅能存放 eml 擋 , 若檔案格式有誤 , 會直接出錯 , 沒有做 error handling
3. 環境為 `Python 3.6.13` , 開發環境可參考 `.devcontainer/Dockerfile`

## decode.py
1. 修改 "mypath" 變數可以變更讀取的 folder
2. 修改 "myoutput" 變數可以修改輸出的 csv 檔案名稱
3. 欄位名稱是固定的 , 故請勿調整(新增或修改或刪除都不行) , 調整會出錯