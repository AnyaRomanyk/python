import pytest

class Order:
    def __init__(self, id, items):
        self.id = id
        self.items = items

    def total(self):
        return sum(item['price'] * item['quantity'] for item in self.items)

    def most_expensive(self):
        if not self.items:
            raise ValueError("No items in order")
        return max(self.items, key=lambda x: x['price'])

    def apply_discount(self, percent):
        if not 0 <= percent <= 100:
            raise ValueError("Invalid discount")
        for item in self.items:
            item['price'] -= item['price'] * (percent / 100)

    def __repr__(self):
        return f"<Order {self.id}: {len(self.items)} items>"


def test_total_basic():
    items = [
        {"price": 10, "quantity": 2},
        {"price": 5, "quantity": 3}
    ]
    order = Order(1, items)
    assert order.total() == 10 * 2 + 5 * 3


def test_total_empty():
    order = Order(2, [])
    assert order.total() == 0


def test_total_extrval():
    items = [
        {"price": 1000745, "quantity": 2},
        {"price": 0, "quantity": 100}
    ]
    order = Order(3, items)
    assert order.total() == 1000745 * 2 + 0 * 100


def test_mostexp_norm():
    items = [
        {"price": 5, "quantity": 1},
        {"price": 20, "quantity": 1},
        {"price": 10, "quantity": 1}
    ]
    order = Order(4, items)
    assert order.most_expensive() == {"price": 20, "quantity": 1}


def test_mostexp_single():
    item = {"price": 50, "quantity": 1}
    order = Order(5, [item])
    assert order.most_expensive() == item


def test_mostexp_empty():
    order = Order(6, [])
    with pytest.raises(ValueError):
        order.most_expensive()


def test_apdisc_valid():
    items = [
        {"price": 100, "quantity": 1},
        {"price": 200, "quantity": 1}
    ]
    order = Order(7, items)
    order.apply_discount(10)
    assert items[0]["price"] == pytest.approx(90)
    assert items[1]["price"] == pytest.approx(180)


def test_apdisc_zpercent():
    items = [{"price": 50, "quantity": 1}]
    order = Order(8, items)
    order.apply_discount(0)
    assert items[0]["price"] == 50


def test_apdisc_hpercent():
    items = [{"price": 50, "quantity": 1}]
    order = Order(9, items)
    order.apply_discount(100)
    assert items[0]["price"] == 0


def test_apdisc_negative():
    items = [{"price": 100, "quantity": 1}]
    order = Order(10, items)
    with pytest.raises(ValueError):
        order.apply_discount(-5)


def test_apdisc_invalid():
    items = [{"price": 100, "quantity": 1}]
    order = Order(11, items)
    with pytest.raises(ValueError):
        order.apply_discount(150)


def test_repr_basic():
    items = [{"price": 10, "quantity": 2}]
    order = Order(12, items)
    assert repr(order) == "<Order 12: 1 items>"


def test_repr_empty():
    order = Order(13, [])
    assert repr(order) == "<Order 13: 0 items>"