import datetime

import requests
import json

# Get the JSON data
url = "https://edu-tpi.donstu.ru/api/Rasp?idGroup=2874"
response = requests.get(url)
# Parse the JSON data
data: dict = json.loads(response.content)
print(datetime.datetime.now().isoformat()[0:10])
# for d in data.get("data").get("rasp"):
#     if datetime.datetime.now().isoformat()[0:10] == d.get("дата")[0:10]:
#         print(d)
for d in data.get("data").get("rasp"):
    if "2022-09-13" == d.get("дата")[0:10]:
        print(d)