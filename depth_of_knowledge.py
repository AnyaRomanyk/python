from abc import ABC, abstractmethod

class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        self.name = name
        self.speed = speed
        self.capacity = capacity

    @abstractmethod
    def move(self, distance: int) -> float:
        pass

    @abstractmethod
    def fuel_consumption(self, distance: int) -> float:
        pass

    @abstractmethod
    def info(self) -> str:
        pass

    def calculate_cost(self, distance: int, price_per_unit: float) -> float:
        return self.fuel_consumption(distance) * price_per_unit
    

class Car(Transport):
    def move(self, distance: int) -> float:
        return distance / self.speed
    def fuel_consumption(self, distance: int) -> float:
        return distance * 0.07
    def info(self) -> str:
        return f"Автомобіль: {self.name}, швидкість: {self.speed} км/год, вміщає в собі: {self.capacity} осіб"
    

class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int):
        super().__init__(name, speed, capacity)
        self.passengers = passengers

    def move(self, distance: int) -> float:
        return distance / self.speed
    def fuel_consumption(self, distance: int) -> float:
        if self.passengers > self.capacity:
            print("Перевантажено!")
        return distance * 0.15
    def info(self) -> str:
        return f"Автобус: {self.name}, швидкість: {self.speed} км/год, вміщає в собі: {self.capacity} осіб"
    

class Bicycle(Transport):
    def __init__(self, name: str, capacity = 1):
        super().__init__(name,20,  capacity)

    def move(self, distance: int) -> float:
        return distance / self.speed
    def fuel_consumption(self, distance: int) -> float:
        return 0
    def info(self) -> str:
        return f"Велосипед: {self.name}, швидкість: {self.speed} км/год"
    

class ElectroCar(Car):
    def fuel_consumption(self, distance: int) -> float:
        return 0
    def battery_usage(seld, distance: int) -> float:
        return distance * 0.2
    def info(self) -> str:
        return f"Електромобіль: {self.name}, швидкість: {self.speed} км/год, вміщає в собі: {self.capacity} осіб"
    


if __name__ == "__main__":
    car = Car("Audi", 100, 5)
    bus = Bus("Mercedes", 80, 60, 75)
    bicycle = Bicycle("Sport")
    electroCar = ElectroCar("Jaguar", 120, 5)

    transports = [car, bus, bicycle, electroCar]

    distance = 100
    price = 2.0

    for t in transports:
        print("-" * 40)
        print(t.info())
        print(f"Час у дорозі на {distance} км: {t.move(distance):.2f} год")
        print(f"Витрати пального: {t.fuel_consumption(distance)}")
        print(f"Вартість поїздки: {t.calculate_cost(distance,price)} грн")

        if isinstance(t, ElectroCar):
            print(f"Витрати заряду: {t.battery_usage(distance)}")
