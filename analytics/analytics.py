import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def main():
    parser = argparse.ArgumentParser(description="аналіз даних про поставки")
    parser.add_argument("csv_file", help="шлях до CSV-файлу з даними про поставки")
    args = parser.parse_args()

    df = pd.read_csv(args.csv_file)

    avg_price = np.mean(df["price_per_unit"])
    median_quantity = np.median(df["quantity"])
    std_price = np.std(df["price_per_unit"])

    df["total_price"] = df["quantity"] * df["price_per_unit"]

    supplier_profit = df.groupby("supplier")["total_price"].sum()
    top_supplier = supplier_profit.idxmax()
    top_profit = supplier_profit.max()

    category_sum = df.groupby("category")["quantity"].sum()

    low_supply = df[df["quantity"] < 100]
    low_supply.to_csv("low_supply.csv", index=False)

    top3 = df.sort_values(by="total_price", ascending=False).head(3)

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(f"середня ціна: {avg_price:.2f}\n")
        f.write(f"медіана кількості: {median_quantity:.2f}\n")
        f.write(f"стандартне відхилення ціни: {std_price:.2f}\n\n")
        f.write(f"найприбутковіший постачальник: {top_supplier}\n")
        f.write(f"його прибуток: {top_profit:.2f}\n\n")

    category_sum.plot(kind="bar", title="кількість препаратів за категоріями")
    plt.xlabel("категорія")
    plt.ylabel("кількість")
    plt.tight_layout()
    plt.savefig("categories_distribution.png")
    plt.show()

    print("---- аналіз поставок ----")
    print(f"середня ціна: {avg_price:.2f}")
    print(f"медіана кількості: {median_quantity:.2f}")
    print(f"стандартне відхилення ціни: {std_price:.2f}")
    print()
    print(f"найприбутковіший постачальник: {top_supplier} ({top_profit:.2f})")
    print()
    print("перші 3 записи з найбільшою загальною вартістю:")
    print(top3)

if __name__ == "__main__":
    main()