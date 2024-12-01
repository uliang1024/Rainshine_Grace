import os
import subprocess
import requests
import signal


def start_server():
    # 啟動 Django 伺服器
    server_process = subprocess.Popen(
        ["venv\\Scripts\\activate", "&&", "python", "manage.py", "runserver"],
        shell=True,
    )
    return server_process


def start_ngrok():
    # 啟動 ngrok
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", "8000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return ngrok_process


def get_ngrok_url():
    # 獲取 ngrok 公開 URL
    response = requests.get("http://localhost:4040/api/tunnels")
    data = response.json()
    return data["tunnels"][0]["public_url"]


def update_line_webhook(url):
    # 更新 LINE Developer Console 中的 webhook URL
    headers = {
        "Authorization": f"Bearer {os.getenv('NEW_LINE_CHANNEL_ACCESS_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {"endpoint": f"{url}/callback"}
    response = requests.put(
        "https://api.line.me/v2/bot/channel/webhook/endpoint",
        headers=headers,
        json=data,
    )
    print(response.json())


def stop_process(process):
    # 停止進程
    if process:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    server_process = start_server()
    ngrok_process = start_ngrok()
    try:
        ngrok_url = get_ngrok_url()
        print(f"Ngrok URL: {ngrok_url}")
        update_line_webhook(ngrok_url)
        input("Press Enter to stop the server and ngrok...")
    finally:
        stop_process(server_process)
        stop_process(ngrok_process)
