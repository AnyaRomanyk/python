medicines = [
    {"name": "Парацетамол", "category": "antibiotic", "quantity": 20, "temperature": 18},
    {"name": "Вітамін D", "category": "vitamin", "quantity": 60, "temperature": 4},
    {"name": "Грипозна вакцина", "category": "vaccine", "quantity": 200, "temperature": 26},
    {"name": "Трав’яний збір", "category": "herbal", "quantity": 10, "temperature": 19},
]

for med in medicines:
    name = med.get("name")
    category = med.get("category")
    quantity = med.get("quantity")
    temperature = med.get("temperature")

    if type(quantity) != int:
        print(f"{name}: Помилка даних")
        continue

    if type(temperature) not in (int, float):
        print(f"{name}: Помилка даних")
        continue

 
    if temperature < 5:
        t_status = "Надто холодно"
    elif temperature > 25:
        t_status = "Надто жарко"
    else:
        t_status = "Норма"


    match category:
        case "antibiotic":
            cat_status = "Рецептурний препарат"
        case "vitamin":
            cat_status = "Вільний продаж"
        case "vaccine":
            cat_status = "Потребує спецзберігання"
        case _:
            cat_status = "Невідома категорія"

    print(f"{name}: {cat_status}, {t_status}")
