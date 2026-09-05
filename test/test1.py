import requests

response = requests.get("http://localhost:8000/api/history/add")
# assert response.status_code==200,f"Response Code:{response.status_code}"

message=response.json()
assert message['type']=="int",f"类型错误实际是{type(message['id'])}"