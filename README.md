# AUO 面試專案解決方案說明


使用:
```
git clone https://github.com/wentingliao1996/AUOinterview.git  
cd AUOinterview  
docker pull wentingla/auotest:1.1.0
docker-compose up -d
```


確認docker container 皆有成功啟動後可在  
http://localhost:5000/docs  

可看到api文件  

測試帳號密碼:
> 帳號:testuser  
> 密碼:testpassword  
### 1. 簡介

本文檔說明supplier testing data API系統的技術實現。此系統旨在處理testing data提供的ZIP格式進行驗證、加密和存儲，以及提供查詢上傳記錄功能。  
#### 1.1 目的

開發一個API服務，用於supplier testing data ，並將資料與記錄進行儲存。  
#### 1.2 主要需求

1. 處理ZIP格式的測試數據文件（平均50MB大小）  
2. 支持每分鐘10個文件的上傳頻率  
3. 驗證上傳的文件內容  
4. 加密存儲文件  
5. 提供上傳記錄查詢功能  
6. 實現JWT身份驗證  

#### 1.3 條件

- ZIP文件中必須包含A.txt和B.txt（必需），C.txt（可選）  
- 上傳的文件需要長期保存  



### 2. 系統架構
![AUOworkflow drawio (1)](https://github.com/user-attachments/assets/2f6f20e1-8dad-4238-a1be-24dda85ffdfc)

本系統主要包括以下組件：

#### 2.1登入
* JWT驗證：系統使用JWT進行身份驗證。  
* 驗證用戶：系統會從user數據庫中驗證用戶的憑證是否正確。  

#### 2.2.主要功能：驗證成功後，用戶可以選擇兩個主要功能：上傳或查詢紀錄。

##### 2.2.1.上傳流程：
* 上傳ZIP文件 :會初步驗證是否為Zip格式  
* 解壓縮並驗證必要文件:A.txt和B.txt是必需的C.txt是選擇性上傳，但除了此三種文件外的檔案的會返回錯誤提示  
* 重新壓縮為ZIP檔案 : 壓縮並使用UUID命名，降低文件辨識度  
* 將上傳的資料儲存到資料庫  
##### 2.2.2.查詢紀錄流程：
* 從資料庫檢索用戶的上傳紀錄
* 根據需求獲取ZIP檔案的紀錄: 藉由資料庫的UUID找到對應的zip檔案，解壓縮後將各個txt檔解密 
* 顯示上傳的原始檔案、時間以及上傳者等信息  
#### 2.3.數據存儲：
* 用戶信息存儲在user數據庫中
* 上傳紀錄存儲在upload_records數據庫中



### 3.資料庫架構
本系統使用關係型數據庫來存儲用戶信息和上傳記錄。數據庫架構包含兩個主要表：USER 和 UploadRecord。  

![螢幕擷取畫面 2024-09-12 155039](https://github.com/user-attachments/assets/c38ad78d-e6fd-443b-a5b9-c0ce188be76e)

* id: 自動生成編號。
* username: 用戶登錄時使用的唯一名稱。
* hashed_password: 存儲經過加密的密碼，增加安全性。
* created_at: 記錄用戶帳戶的創建時間，有助於用戶管理。



---
![螢幕擷取畫面 2024-09-12 161324](https://github.com/user-attachments/assets/4daa6e0f-c8de-4b74-b790-fb36b0b59eec)

* id: 每條上傳記錄的唯一標識符。
* username: 關聯到 USER 表，辨識哪位使用者上傳資料。
* uuid: 為每個上傳的文件生成的唯一標識符，便於文件管理和檢索。
* created_at: 記錄文件上傳的確切時間。


---
![螢幕擷取畫面 2024-09-12 161339](https://github.com/user-attachments/assets/ada82d1f-decc-452e-a386-c13741e7abdb)

* id: 每條上傳記錄的唯一標識符。
* uuid: 關聯到 UploadRecord表，辨識上傳的資料夾。
* A: A.txt內容
* B: B.txt內容
* C: C.txt內容

### 4. 技術

- 後端框架：FastAPI
- 數據庫：MySQL
- ORM：SQLAlchemy
- 文件加密：Fernet（來自cryptography庫）
- 容器化：Docker
- API文檔：Swagger UI（由FastAPI自動生成）
