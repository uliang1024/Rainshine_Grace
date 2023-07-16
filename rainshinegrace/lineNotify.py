import requests

def line_notify_send_message(message):
    requests.post("https://notify-api.line.me/api/notify",
        headers = { "Authorization": "Bearer " + '2d7CvMEEjHf8bzVoYgoZhUT7yzQP1FRKytOfCtVMmgd' }, 
        data = { 'message': message })
    
    requests.post("https://notify-api.line.me/api/notify",
        headers = { "Authorization": "Bearer " + 'TBDVrVnrbZrHaJcvzheCg2mHOy57XlYxMT4JE5nEKpG' }, 
        data = { 'message': message })