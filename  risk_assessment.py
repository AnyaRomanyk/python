import threading, random, time
from tqdm import tqdm

PRICE_PER_UNIT = 5  
TQDM_AVAILABLE = True


class Warehouse:
    def __init__(self, name: str, meds: int):
        self.name = name
        self.meds = meds
        self.lock = threading.Lock()

    def steal(self, amount: int):
        if self.meds <= 0:
            return 0, 'empty'

        r = random.random()
        if r < 0.10:
            return 0, 'caught'
        if r < 0.20:
            return 0, 'failed'

        factor = random.uniform(0.5, 1.0)
        desired = int(amount * factor)
        stolen = min(desired, self.meds)

        self.meds -= stolen
        if stolen == 0:
            return 0, 'empty'
        if stolen < amount:
            return stolen, 'partial'
        return stolen, 'ok'


class Runner(threading.Thread):
    def __init__(self, name: str, warehouses: list, attempts: int = 10, progress_bar=None):
        super().__init__()
        self.name = name
        self.warehouses = warehouses
        self.attempts = attempts
        self.profit = 0
        self.caught_count = 0
        self.failed_count = 0
        self.partial_count = 0
        self.ok_count = 0
        self.progress_bar = progress_bar 
    def run(self):
        for i in range(self.attempts):
            wh = random.choice(self.warehouses)
            amount = random.randint(10, 30)

            wh.lock.acquire()
            try:
                stolen, status = wh.steal(amount)
            finally:
                wh.lock.release()

            if status == 'caught':
                self.caught_count += 1
            elif status == 'failed' or status == 'empty':
                self.failed_count += 1
            elif status == 'partial':
                self.partial_count += 1
                self.profit += stolen * PRICE_PER_UNIT
            elif status == 'ok':
                self.ok_count += 1
                self.profit += stolen * PRICE_PER_UNIT

            if self.progress_bar is not None:
                self.progress_bar.update(1)
            else:
                print(f"[{self.name}] attempt {i+1}/{self.attempts} -> {status}, stolen={stolen}")

            time.sleep(random.uniform(0.1, 0.5))


def run_simulation(num_runners=5, num_warehouses=4, attempts_per_runner=10):
    warehouses = []
    for i in range(num_warehouses):
        w = Warehouse(name=f"WH-{i+1}", meds=random.randint(100, 300))
        warehouses.append(w)

    bars = []
    if TQDM_AVAILABLE:
        for r in range(num_runners):
            p = tqdm(total=attempts_per_runner, desc=f"Runner-{r+1}", position=r, leave=True)
            bars.append(p)
    else:
        bars = [None] * num_runners

    runners = []
    for i in range(num_runners):
        name = f"Runner-{i+1}"
        runner = Runner(name=name, warehouses=warehouses, attempts=attempts_per_runner, progress_bar=bars[i])
        runners.append(runner)
        runner.start()

    for r in runners:
        r.join()

    if TQDM_AVAILABLE:
        for b in bars:
            b.close()

    total_profit = sum(r.profit for r in runners)
    summary = {
        'warehouses': [(w.name, w.meds) for w in warehouses],
        'runners': [{
            'name': r.name,
            'profit': r.profit,
            'caught': r.caught_count,
            'failed': r.failed_count,
            'partial': r.partial_count,
            'ok': r.ok_count
        } for r in runners],
        'total_profit': total_profit
    }
    return summary


def pretty_report(summary):
    print("\n--- звіт по симуляції ---")
    print("залишки на складах:")
    for name, meds in summary['warehouses']:
        print(f" - {name}: {meds} одиниць")
    print("\nрезультати бігунів:")
    for r in summary['runners']:
        print(f" {r['name']}: прибуток={r['profit']}, зловили={r['caught']}, фейли={r['failed']}, часткові={r['partial']}, успіхи={r['ok']}")
    print(f"\nзагальний прибуток: {summary['total_profit']} умовних одиниць (ціна за одиницю = {PRICE_PER_UNIT})")


if __name__ == "__main__":
    random.seed(42)  
    runner_counts = [1, 3, 5, 8]  
    for cnt in runner_counts:
        print(f"\n\n--- запуск симуляції з {cnt} бігунами ---")
        summary = run_simulation(num_runners=cnt, num_warehouses=4, attempts_per_runner=10)
        pretty_report(summary)
        time.sleep(1)
