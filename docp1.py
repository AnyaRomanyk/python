from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class Report(Document):
    def render(self) -> str:
        return "Report"
    
class Invoice(Document):
    def render(self) -> str:
        return "Invoice"
    
class Contract(Document):
    def render(self) -> str:
        return "Contract"
    
class NullDocument(Document):
    def render(self) -> str:
        return "Null doc"
    
class DocFact:
    _types = {
        "report": Report,
        "invoice": Invoice,
        "contract": Contract
    }

    @staticmethod
    def create(doc_type: str) -> Document:
        a = DocFact._types.get(doc_type, NullDocument)
        return a()
    

if __name__ == "__main__":
    docs = ["report", "123", "invoice","contract", "qwer"]

    for d in docs:
        doc = DocFact.create(d)
        print(doc.render())