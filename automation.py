import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, uuid
from datetime import datetime

CSV_HEADER = ['id','name','category','quantity','price','location','created_at']

class InventoryApp:
    def __init__(self, root):
        self.root = root
        root.title("Облік товарів")
        root.geometry("950x550")

        self.items = []      
        self.filtered = None 
        self.filename = None
        self.sort_state = {}

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Відкрити", command=self.load_csv)
        filemenu.add_command(label="Зберегти", command=self.save_csv)
        filemenu.add_command(label="Зберегти як", command=self.save_as_csv)
        filemenu.add_separator()
        filemenu.add_command(label="Вихід", command=root.quit)
        menubar.add_cascade(label="Файл", menu=filemenu)
        root.config(menu=menubar)

        search_frame = ttk.Frame(root)
        search_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(search_frame, text="Пошук:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.apply_filter())
        tk.Entry(search_frame, textvariable=self.search_var).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(search_frame, text="Очистити", command=self.clear_search).pack(side='left', padx=5)

        main_frame = ttk.Frame(root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        cols = ('id','name','category','quantity','price','location')
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(side='left', fill='both', expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree.heading(c, text=c.capitalize(), command=lambda _c=c: self.sort_by(_c))
            self.tree.column(c, width=120)
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.load_selected())
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        form_frame = ttk.Frame(main_frame, padding=5)
        form_frame.pack(side='right', fill='y')
        self.fields = {}
        labels = [('id','ID (залишити порожнім — згенерується)'),('name','Назва'),('category','Категорія'),
                  ('quantity','Кількість'),('price','Ціна'),('location','Місцезнаходження')]
        for i, (key, text) in enumerate(labels):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, sticky='w', pady=2)
            e = ttk.Entry(form_frame)
            e.grid(row=i, column=1, pady=2, sticky='ew')
            self.fields[key] = e
        form_frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Додати", command=self.add).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Оновити", command=self.update).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Видалити", command=self.delete).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Очистити форму", command=self.clear_form).grid(row=0, column=3, padx=2)

        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        ttk.Label(root, textvariable=self.status_var, relief='sunken', anchor='w').pack(side='bottom', fill='x')

    def set_status(self, msg):
        self.status_var.set(msg)

    #  CRUD 
    def validate_form(self, for_update=False):
        for e in self.fields.values(): e.config(background='white')
        d = {}
        errors = []

        id_val = self.fields['id'].get().strip()
        if not for_update and id_val and any(it['id']==id_val for it in self.items):
            errors.append(('id','ID має бути унікальним'))
        d['id'] = id_val or str(uuid.uuid4())

        name = self.fields['name'].get().strip()
        if not name: errors.append(('name','Назва порожня'))
        category = self.fields['category'].get().strip()
        if not category: errors.append(('category','Категорія порожня'))
        d['name'] = name
        d['category'] = category

        qtxt = self.fields['quantity'].get().strip()
        try:
            q = int(qtxt)
            if q<0: raise ValueError
            d['quantity'] = str(q)
        except:
            errors.append(('quantity','Кількість має бути цілим числом >=0'))

        ptxt = self.fields['price'].get().strip().replace(',','.')
        try:
            p = float(ptxt)
            if p<0: raise ValueError
            d['price'] = f"{p:.2f}"
        except:
            errors.append(('price','Ціна має бути >=0'))

        d['location'] = self.fields['location'].get().strip()

        if errors:
            for key,_ in errors:
                if key in self.fields: self.fields[key].config(background='#f8d7da')
            self.set_status(errors[0][1])
            return None

        d['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return d

    def add(self):
        d = self.validate_form()
        if not d: return
        self.items.append(d)
        self.apply_filter()
        self.set_status("Додано")
        self.clear_form()

    def update(self):
        sel = self.tree.selection()
        if not sel: self.set_status("Спочатку виберіть рядок для оновлення"); return
        d = self.validate_form(for_update=True)
        if not d: return
        old_id = self.tree.item(sel[0])['values'][0]
        for it in self.items:
            if it['id']==old_id:
                it.update(d)
                break
        self.apply_filter()
        self.set_status("Оновлено")

    def delete(self):
        sel = self.tree.selection()
        if not sel: self.set_status("Нічого не вибрано"); return
        vals = self.tree.item(sel[0])['values']
        if not messagebox.askyesno("Підтвердження", f"Видалити '{vals[1]}'?"): return
        self.items = [it for it in self.items if it['id']!=vals[0]]
        self.apply_filter()
        self.set_status("Видалено")
        self.clear_form()

    def clear_form(self):
        for e in self.fields.values(): e.delete(0,'end'); e.config(background='white')
        self.tree.selection_remove(self.tree.selection())
        self.set_status("Форма очищена")

    def load_selected(self):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        keys = ['id','name','category','quantity','price','location']
        for k,v in zip(keys,vals): 
            self.fields[k].delete(0,'end'); self.fields[k].insert(0,str(v))
        self.set_status("Заповнено форму з вибраного рядка")

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not path: return
        try:
            with open(path,'r',newline='',encoding='utf-8') as f:
                r = csv.DictReader(f)
                self.items = []
                for row in r:
                    self.items.append({k: row.get(k,'') for k in CSV_HEADER})
            self.filename = path
            self.apply_filter()
            self.set_status(f"Завантажено {len(self.items)} записів")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))
            self.set_status("Помилка при відкритті CSV")

    def save_csv(self):
        if not self.filename: return self.save_as_csv()
        self._write_csv(self.filename)

    def save_as_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path: return
        self.filename = path
        self._write_csv(path)

    def _write_csv(self, path):
        try:
            with open(path,'w',newline='',encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
                writer.writeheader()
                for it in self.items:
                    writer.writerow({k:it.get(k,'') for k in CSV_HEADER})
            self.set_status(f"Збережено {len(self.items)} записів")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))
            self.set_status("Помилка при збереженні CSV")

    #  Пошук та сортування 
    def apply_filter(self):
        q = self.search_var.get().strip().lower()
        if q:
            self.filtered = [it for it in self.items if q in it['name'].lower() or q in it['category'].lower()]
        else:
            self.filtered = self.items[:]
        self.refresh_tree()

    def clear_search(self):
        self.search_var.set('')
        self.apply_filter()

    def refresh_tree(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for it in self.filtered:
            self.tree.insert('', 'end', values=(it['id'],it['name'],it['category'],it['quantity'],it['price'],it['location']))

    def sort_by(self, col):
        rev = self.sort_state.get(col, False)
        def key(it):
            if col=='quantity': return int(it.get(col,0))
            if col=='price': return float(it.get(col,0))
            return it.get(col,'').lower()
        self.items.sort(key=key, reverse=rev)
        self.sort_state[col] = not rev
        self.apply_filter()
        self.set_status(f"Сортування: {col} {'спадання' if rev else 'зростання'}")

if __name__=="__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()