import requests

def line_notify_send_message(message):
    requests.post("https://notify-api.line.me/api/notify",
        headers = { "Authorization": "Bearer " + 'DxbxW1ixTK7UgdSUdQyYMy8DRl2W1yMlvCIK0rQtjuC' }, 
        data = { 'message': message })