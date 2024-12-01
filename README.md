# Rainshine_Grace

## 創建虛擬環境

```sh
python -m venv venv
```

## 進入虛擬環境

```sh
venv\Scripts\activate
```

## 退出虛擬環境

```sh
deactivate
```

## 安裝套件

```sh
pip install -r requirements.txt
```

## 運行伺服器

1. 執行伺服器

    ```sh
    python manage.py runserver
    ```

2. 開啟 ngrok

    ```sh
    ngrok http 8000
    ```

    ngrok download: [https://dashboard.ngrok.com/get-started/setup/windows](https://dashboard.ngrok.com/get-started/setup/windows)  
    下載後放在根目錄並執行

3. 複製 ngrok 的 URL

4. 到 Line Developers 設定 Webhook URL (ngrok 的 URL + /callback)

5. 成功後開啟 LINE 好友測試

## 另一個方案，快速啟動開發環境

```sh
python start_dev_env.py
```

- 確保有設定好 LINE_CHANNEL_ACCESS_TOKEN 環境變數
- 確保有安裝 ngrok
- 確保有安裝 python 套件
