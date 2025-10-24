def shadow(limit=200):
    def decorator(func):
        def wrapper(*args, **kwargs):
            total = 0
            for item in func(*args, **kwargs):
                print(item)
                parts = item.split()
                if len(parts) != 2:
                    print(f"Неправильний формат: {item}")
                    continue

                type_, amount_str = parts
                try:
                    amount = float(amount_str)
                except ValueError:
                    print(f"Сума не число: {amount_str}")
                    continue

                if type_.lower() == "refund":
                    total -= amount
                elif type_.lower() in ("payment", "transfer"):
                    total += amount
                else:
                    print(f"Невідомий тип транзакції: {type_}")
                    continue

                if total > limit:
                    print("Тіньовий ліміт перевищено. Активую схему")

            return total
        return wrapper
    return decorator


def transaction_generator():
    transactions = [
        "payment 120",
        "refund 50",
        "transfer 300",
        "donation 40",
        "payment twenty",
        "payment 30"
    ]
    for t in transactions:
        yield t


@shadow(limit=200)
def run_transactions():
    yield from transaction_generator()


if __name__ == "__main__":
    final_sum = run_transactions()
    print(f"\nФінальна сума всіх транзакцій: {final_sum}")
