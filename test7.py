import requests


item_id = '180961283'
vol = item_id[:len(item_id)-5]
part = item_id[:len(item_id)-3]

i = 1
while True:
    basketNum = f'0{i}' if i // 10 == 0 else str(i)
    response = requests.get(f'https://basket-' + basketNum + '.wb.ru/vol' + vol + '/part' + part + '/' + item_id + '/info/ru/card.json')
    if response.status_code == 200:
        break
    i += 1

print(charsDict := response.json()["options"])

full_chars_dict = {}
for item in charsDict:
    full_chars_dict[item["name"]] = item["value"]
print(list(full_chars_dict.keys()))
