from dataclasses import dataclass, field
from datetime import datetime
import csv

@dataclass(order=True)
class Item:
    category: str
    value: float
    name: str
    quantity: int
    condition: str
    location: str
    added_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def total_value(self):
        return self.quantity * self.value

    def __str__(self):
        return f"[{self.category}] {self.name} ({self.quantity} шт.) — {self.value} грн/шт, стан: {self.condition}"


@dataclass
class Inventory:
    items: list = field(default_factory=list)

    def add_item(self, item: Item):
        self.items.append(item)

    def remove_item(self, name: str):
        self.items = [i for i in self.items if i.name != name]

    def find_by_category(self, category: str):
        return [i for i in self.items if i.category == category]

    def total_inventory_value(self):
        return sum(i.total_value() for i in self.items)

    def save_to_csv(self, filename):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "category", "quantity", "value", "condition", "location", "added_at"])
            for i in self.items:
                writer.writerow([i.name, i.category, i.quantity, i.value, i.condition, i.location, i.added_at])

    def load_from_csv(self, filename):
        self.items.clear()
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = Item(
                    name=row["name"],
                    category=row["category"],
                    quantity=int(row["quantity"]),
                    value=float(row["value"]),
                    condition=row["condition"],
                    location=row["location"],
                    added_at=row["added_at"]
                )
                self.items.append(item)

    def export_summary(self):
        summary = {}
        for i in self.items:
            summary[i.category] = summary.get(i.category, 0) + 1
        return summary

    def filter_items(self, **kwargs):
        result = self.items
        for key, value in kwargs.items():
            result = [i for i in result if str(getattr(i, key)) == str(value)]
        return result

    def sort_items(self, field_name: str):
        return sorted(self.items, key=lambda i: getattr(i, field_name))


if __name__ == "__main__":
    inv = Inventory()

    inv.add_item(Item(
        name="Гаечний ключ",
        category="інструменти",
        quantity=3,
        value=5.0,
        condition="уживаний",
        location="гараж"
    ))

    inv.add_item(Item(
        name="Дриль",
        category="інструменти",
        quantity=1,
        value=120.0,
        condition="новий",
        location="комора"
    ))

    print("Усього предметів:", len(inv.items))
    print("Загальна вартість:", inv.total_inventory_value())
    print("Категорії:", inv.export_summary())

    print("Знайдено в категорії 'інструменти':")
    for item in inv.find_by_category("інструменти"):
        print(item)
