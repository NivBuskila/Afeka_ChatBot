import requests
import json

url = 'http://localhost:5000/api/chat'
headers = {'Content-Type': 'application/json'}
data = {
  'message': 'מתי סטודנט ששירת במילואים זכאי למועד מיוחד בבחינות?',
  'include_sources': True
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.text) 