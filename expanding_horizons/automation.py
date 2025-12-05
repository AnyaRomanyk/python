import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, uuid, os
from datetime import datetime
import requests
from requests.exceptions import RequestException

CSV_HEADER = ['id','name','category','quantity','price','location','created_at']
SERVER_URL = "http://127.0.0.1:5000"  
CACHE_FILE = "cache.csv"

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
        filemenu.add_command(label="Відкрити (локальний CSV)", command=self.load_csv)
        filemenu.add_command(label="Зберегти (локальний CSV)", command=self.save_csv)
        filemenu.add_command(label="Зберегти як", command=self.save_as_csv)
        filemenu.add_separator()
        filemenu.add_command(label="Синхронізувати зараз", command=self.sync_now)
        filemenu.add_command(label="Експорт CSV (сервер)", command=self.export_csv_from_server)
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

        self.load_cache()
        self.try_initial_sync()

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

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

    def is_server_available(self):
        try:
            r = requests.get(SERVER_URL + "/items", timeout=1.5)
            return r.status_code == 200
        except RequestException:
            return False

    def api_get_items(self):
        try:
            r = requests.get(SERVER_URL + "/items", timeout=3)
            r.raise_for_status()
            return r.json(), None
        except RequestException as e:
            return None, str(e)

    def api_add_item(self, item):
        try:
            r = requests.post(SERVER_URL + "/items", json=item, timeout=3)
            if r.status_code == 201:
                return r.json(), None
            return None, r.text
        except RequestException as e:
            return None, str(e)

    def api_update_item(self, item):
        try:
            r = requests.put(f"{SERVER_URL}/items/{item['id']}", json=item, timeout=3)
            if r.status_code in (200,201):
                return r.json(), None
            return None, r.text
        except RequestException as e:
            return None, str(e)

    def api_delete_item(self, item_id):
        try:
            r = requests.delete(f"{SERVER_URL}/items/{item_id}", timeout=3)
            if r.status_code == 200:
                return True, None
            return False, r.text
        except RequestException as e:
            return False, str(e)

    def add(self):
        d = self.validate_form()
        if not d: return
        if self.is_server_available():
            item, err = self.api_add_item(d)
            if err:
                self.set_status("Помилка сервера: " + str(err))
                return
            self.items.append(item)
            self.set_status("Додано на сервері")
            self.clear_form()
            self.apply_filter()
            self.save_cache()
        else:
            self.items.append(d)
            self.set_status("Сервер недоступний — додано в кеш")
            self.clear_form()
            self.apply_filter()
            self.save_cache()

    def update(self):
        sel = self.tree.selection()
        if not sel: self.set_status("Спочатку виберіть рядок для оновлення"); return
        d = self.validate_form(for_update=True)
        if not d: return
        old_id = self.tree.item(sel[0])['values'][0]
        if self.is_server_available():
            item, err = self.api_update_item(d)
            if err:
                self.set_status("Помилка сервера: " + str(err))
                return
            for it in self.items:
                if it['id']==old_id:
                    it.update(item)
                    break
            self.set_status("Оновлено на сервері")
            self.apply_filter()
            self.save_cache()
        else:
            for it in self.items:
                if it['id']==old_id:
                    it.update(d)
                    break
            self.set_status("Сервер недоступний — оновлено в кеші")
            self.apply_filter()
            self.save_cache()

    def delete(self):
        sel = self.tree.selection()
        if not sel: self.set_status("Нічого не вибрано"); return
        vals = self.tree.item(sel[0])['values']
        if not messagebox.askyesno("Підтвердження", f"Видалити '{vals[1]}'?"): return
        item_id = vals[0]
        if self.is_server_available():
            ok, err = self.api_delete_item(item_id)
            if not ok:
                self.set_status("Помилка сервера: " + str(err))
                return
            self.items = [it for it in self.items if it['id']!=item_id]
            self.set_status("Видалено на сервері")
            self.apply_filter()
            self.save_cache()
        else:
            self.items = [it for it in self.items if it['id']!=item_id]
            self.set_status("Сервер недоступний — видалено в кеші")
            self.apply_filter()
            self.save_cache()
            self.clear_form()

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
            self.set_status(f"Завантажено {len(self.items)} записів (локально)")
            self.clear_form()
            self.save_cache()
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
            if col=='quantity': 
                try: return int(it.get(col,0))
                except: return 0
            if col=='price': 
                try: return float(it.get(col,0))
                except: return 0.0
            return it.get(col,'').lower()
        self.items.sort(key=key, reverse=rev)
        self.sort_state[col] = not rev
        self.apply_filter()
        self.set_status(f"Сортування: {col} {'спадання' if rev else 'зростання'}")

    def load_selected(self):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        keys = ['id','name','category','quantity','price','location']
        for k,v in zip(keys,vals): 
            self.fields[k].delete(0,'end'); self.fields[k].insert(0,str(v))
        self.set_status("Заповнено форму з вибраного рядка")

    def clear_form(self):
        for e in self.fields.values(): e.delete(0,'end'); e.config(background='white')
        try:
            self.tree.selection_remove(self.tree.selection())
        except:
            pass
        self.set_status("Форма очищена")

    def load_cache(self):
        if not os.path.exists(CACHE_FILE):
            self.items = []
            return
        try:
            with open(CACHE_FILE,'r',newline='',encoding='utf-8') as f:
                r = csv.DictReader(f)
                self.items = [{k: row.get(k,'') for k in CSV_HEADER} for row in r]
            self.apply_filter()
            self.set_status("Завантажено кеш")
        except Exception as e:
            self.set_status("Помилка читання кешу")

    def save_cache(self):
        try:
            with open(CACHE_FILE,'w',newline='',encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=CSV_HEADER)
                w.writeheader()
                for it in self.items:
                    w.writerow({k:it.get(k,'') for k in CSV_HEADER})
        except:
            pass

    def try_initial_sync(self):
        if self.is_server_available():
            self.set_status("Сервер доступний — синхронізуюсь...")
            self.sync_with_server(stop_on_error=False)
        else:
            self.set_status("Працює в офлайн-режимі (сервер недоступний)")

    def sync_now(self):
        if not self.is_server_available():
            self.set_status("Не вдалось з'єднатись із сервером")
            return
        ok = self.sync_with_server()
        if ok:
            self.set_status("Синхронізація завершена")
        else:
            self.set_status("Помилка синхронізації")

    def sync_with_server(self, stop_on_error=True):
        server_items, err = self.api_get_items()
        if err:
            if stop_on_error:
                self.set_status("Помилка отримання з сервера: " + str(err))
            return False
        server_map = {it['id']: it for it in server_items}

        for local in list(self.items):
            sid = local.get('id')
            if not sid or sid not in server_map:
                res, err = self.api_add_item(local)
                if err:
                    if stop_on_error:
                        self.set_status("Помилка додавання на сервер: " + str(err))
                        return False
                    continue
            else:
                res, err = self.api_update_item(local)
                if err:
                    if stop_on_error:
                        self.set_status("Помилка оновлення на сервер: " + str(err))
                        return False
                    continue

        server_items, err = self.api_get_items()
        if err:
            if stop_on_error:
                self.set_status("Помилка отримання після відправки: " + str(err))
            return False
        self.items = server_items
        self.apply_filter()
        self.save_cache()
        return True

    def export_csv_from_server(self):
        try:
            r = requests.get(SERVER_URL + "/export", timeout=5)
            if r.status_code == 200:
                path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
                if not path: return
                with open(path,'w',encoding='utf-8',newline='') as f:
                    f.write(r.text)
                self.set_status("Експортовано CSV з сервера")
            else:
                self.set_status("Сервер повернув помилку при експорті")
        except RequestException as e:
            self.set_status("Помилка під час експорту: " + str(e))

if __name__=="__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
