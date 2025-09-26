from models import Antibiotic, Vaccine, Vitamin

medicines = [
    Antibiotic("Cephalexin", 6, 127),
    Vitamin("Магній В6", 16, 220.50),
    Vaccine("Influvak", 2, 800)
]

for med in medicines:
    print("-" * 40)
    print(med.info())
    print("Потрібен рецепт: ", med.requires_prescription())
    print("Умови зберігання: ", med.storage_requirements())
