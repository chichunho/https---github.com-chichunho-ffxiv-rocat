import json

result = {}
with open("Item.csv", "r", encoding="utf-8") as f:
    for row in f.readlines():
        targets = row.split(",", maxsplit=2)
        try:
            item_id = int(targets[0])
            item_name = targets[1].strip('"')
            if len(item_name) > 0:
                result[item_id] = item_name
        except ValueError:
            continue

with open("Item.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)
