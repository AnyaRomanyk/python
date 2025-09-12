clients = [
    {"name": "Аня", "amount": 1000, "status": "suspicious" },
    {"name": "Лесик", "amount": "чотириста п'ятдесят", "status": "clean"},
    {"name": "Влад", "amount": 350, "status": "fraud"},
    {"name": "Юліанна", "amount": 500, "status": "unknow"},
    {"name": "Євген", "amount": 600, "status": "clean"},

]

for client in clients:
    name = client.get("name")
    amount = client.get("amount")
    status = client.get("status")

    if type(amount) not in (int, float):
        print(f"{name}: Має фальшиві дані")
        continue

    if amount < 100:
        am_status = "Дрібнота"
    elif amount < 1000:
        am_status = "Середнячок"
    else:
        am_status = "Великий клієнт"

    
    match status:
        case "clean":
            decision = "Працювати без питань"
        case "suspicious":
            decision = "Перевірити документи"
        case "fraud":
            decision = "У чорний список"
        case _:
            decision = "Невідомий статус"

    print(f"{name}: {am_status}, {decision}")