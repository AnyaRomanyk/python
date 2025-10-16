class JunkItem:
    def __init__(self, name, quantity, value):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __str__(self):
        return f"{self.name}|{self.quantity}|{str(self.value).replace('.', ',')}"


class JunkStorage:
    def serialize(self, items, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for item in items:
                f.write(str(item) + "\n")

    def parse(self, filename):
        items = []
        with open(filename, "r", encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                parts = line.strip().split("|")
                if len(parts) != 3:
                    print(f"Рядок {n} пропущено: неправильна кількість полів")
                    continue

                name, q_str, v_str = parts
                v_str = v_str.replace(",", ".")
                try:
                    q = int(q_str)
                    v = float(v_str)
                except ValueError:
                    print(f"Рядок {n} пропущено: кількість або ціна не число")
                    continue

                items.append(JunkItem(name, q, v))
        return items


items = [
    JunkItem("Бляшанка", 5, 2.5),
    JunkItem("Стара плата", 3, 7.8),
    JunkItem("Купка дротів", 10, 1.2)
]

store = JunkStorage()
store.serialize(items, "junk_store.txt")
print("Предмети записано у файл!")

read_items = store.parse("junk_store.txt")

print("\nПрочитані предмети:")
for i in read_items:
    print(f"{i.name} — кількість: {i.quantity}, ціна: {i.value}")