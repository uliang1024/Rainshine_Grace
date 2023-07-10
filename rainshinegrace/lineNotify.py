import requests

def line_notify_send_message(message):
    requests.post("https://notify-api.line.me/api/notify",
        headers = { "Authorization": "Bearer " + '5hnkeQ93ic51Y2nVQTy1u3HtoNGEhVNtOolVq8TtXdA' }, 
        data = { 'message': message })