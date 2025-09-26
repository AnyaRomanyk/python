from abc import ABC, abstractmethod

class Medicine(ABC):
    def __init__(self, name: str, quantity: int, price: float):
        if not isinstance(name, str):
            raise TypeError("Назва має бути рядком")
        if not isinstance(quantity, int):
            raise TypeError("Кількість має бути цілим числом")
        if not isinstance(price, (int, float)):
            raise TypeError("Ціна має бути числом")
        
        self.name = name
        self.quantity = quantity
        self.price = float(price)


    @abstractmethod
    def requires_prescription(self) -> bool:
        pass

    @abstractmethod
    def storage_requirements(self) -> str:
        pass

    def total_price(self) -> float:
        return self.quantity * self.price
    
    @abstractmethod
    def info(self) -> str:
        pass


class Antibiotic(Medicine):
    def requires_prescription(self) -> bool:
        return True
    
    def storage_requirements(self) -> str:
        return "8-15C, темне місце"
    
    def info(self) -> str:
        return f"Антибіотик: {self.name}, кількість: {self.quantity}, ціна: {self.total_price()} грн"
    

class Vitamin(Medicine):
    def requires_prescription(self) -> bool:
        return False
    
    def storage_requirements(self) -> str:
        return "15-20С, сухо"
    
    def info(self) -> str:
        return f"Вітамін: {self.name}, клькість: {self.quantity}, ціна: {self.total_price()} грн"
    
class Vaccine(Medicine):
    def requires_prescription(self) -> bool:
        return True
    
    def storage_requirements(self) -> str:
        return "2-8C, золодильник"
    
    def total_price(self) -> float:
        base = super().total_price()
        return base * 1.1

    
    def info(self) -> str:
        return f"Вакцина: {self.name}, кількість: {self.quantity}, ціна: {self.total_price()} грн"
