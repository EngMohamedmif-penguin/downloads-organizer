from __future__ import annotations

import logging
import os
import queue
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

import downloads_organizer as engine


class QueueHandler(logging.Handler):
    def __init__(self, output: queue.Queue[str]):
        super().__init__()
        self.output = output

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.output.put(self.format(record))
        except Exception:
            pass


class CategoryDialog(tk.Toplevel):
    def __init__(self, parent, title: str, category: str = "", extensions: list[str] | None = None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry("500x240")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#111827")
        self.columnconfigure(1, weight=1)
        tk.Label(self, text="اسم التصنيف / المجلد", bg="#111827", fg="#f9fafb", font=("Segoe UI", 10)).grid(row=0, column=0, padx=18, pady=(22, 8), sticky="w")
        self.category_var = tk.StringVar(value=category)
        ttk.Entry(self, textvariable=self.category_var).grid(row=0, column=1, padx=(0, 18), pady=(22, 8), sticky="ew")
        tk.Label(self, text="الامتدادات مفصولة بفاصلة", bg="#111827", fg="#f9fafb", font=("Segoe UI", 10)).grid(row=1, column=0, padx=18, pady=8, sticky="w")
        self.ext_var = tk.StringVar(value=", ".join(extensions or []))
        ttk.Entry(self, textvariable=self.ext_var).grid(row=1, column=1, padx=(0, 18), pady=8, sticky="ew")
        tk.Label(self, text="مثال: .jpg, .png, .webp", bg="#111827", fg="#94a3b8", font=("Segoe UI", 9)).grid(row=2, column=1, sticky="w", padx=(0, 18))
        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, columnspan=2, pady=24)
        ttk.Button(buttons, text="حفظ", style="Accent.TButton", command=self.accept).pack(side="left", padx=6)
        ttk.Button(buttons, text="إلغاء", command=self.destroy).pack(side="left", padx=6)
        self.bind("<Return>", lambda _event: self.accept())
        self.bind("<Escape>", lambda _event: self.destroy())

    def accept(self):
        category = self.category_var.get().strip().replace("\\", "/").strip("/")
        extensions = sorted({engine.normalize_extension(x) for x in self.ext_var.get().split(",") if engine.normalize_extension(x)})
        if not category:
            messagebox.showerror("بيانات ناقصة", "اكتب اسم التصنيف.", parent=self)
            return
        if not extensions:
            messagebox.showerror("بيانات ناقصة", "أدخل امتدادًا واحدًا على الأقل.", parent=self)
            return
        self.result = (category, extensions)
        self.destroy()


class OrganizerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Downloads Organizer | مدير التنزيلات")
        self.geometry("1050x720")
        self.minsize(900, 620)
        self.configure(bg="#0b1120")
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.log_handler = QueueHandler(self.log_queue)
        self.log_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S"))
        engine.log.addHandler(self.log_handler)
        self.monitor_observer = None
        self.monitor_organizer: engine.Organizer | None = None
        self.operation_running = False
        self.path_var = tk.StringVar(value=str(engine.get_downloads_dir()))
        self.status_var = tk.StringVar(value="جاهز")
        self.group_month_var = tk.BooleanVar()
        self.duplicate_mode_var = tk.StringVar()
        self._configure_style()
        self._build_ui()
        self.load_settings()
        self.refresh_categories()
        self.after(150, self.drain_logs)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#0b1120")
        style.configure("Card.TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#0b1120", foreground="#f8fafc", font=("Segoe UI", 25, "bold"))
        style.configure("Subtitle.TLabel", background="#0b1120", foreground="#94a3b8", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#111827", foreground="#38bdf8", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", background="#263449", foreground="#f8fafc", padding=(12, 9), font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#3b4c66")])
        style.configure("Accent.TButton", background="#2563eb", foreground="white", padding=(13, 10), font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#3b82f6")])
        style.configure("Danger.TButton", background="#991b1b", foreground="white", padding=(12, 9), font=("Segoe UI", 10, "bold"))
        style.map("Danger.TButton", background=[("active", "#dc2626")])
        style.configure("TNotebook", background="#0b1120", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e293b", foreground="#cbd5e1", padding=(18, 10), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#2563eb")], foreground=[("selected", "white")])
        style.configure("Treeview", background="#0f172a", fieldbackground="#0f172a", foreground="#e2e8f0", rowheight=30, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#1e293b", foreground="#f8fafc", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#1d4ed8")])
        style.configure("TCheckbutton", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("TCombobox", fieldbackground="#0f172a", background="#263449", foreground="#f8fafc")

    def _build_ui(self):
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Downloads Organizer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="لوحة تحكم عصرية لتنظيم ملفاتك تلقائيًا", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 18))
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True)
        self.dashboard_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=18)
        self.categories_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=18)
        self.settings_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=18)
        self.tabs.add(self.dashboard_tab, text="لوحة التحكم")
        self.tabs.add(self.categories_tab, text="إدارة التصنيفات")
        self.tabs.add(self.settings_tab, text="الإعدادات")
        self.build_dashboard()
        self.build_categories()
        self.build_settings()

    def build_dashboard(self):
        tab = self.dashboard_tab
        path_box = ttk.Frame(tab, style="Card.TFrame")
        path_box.pack(fill="x", pady=(0, 12))
        ttk.Label(path_box, text="المجلد الذي سيتم تنظيمه").pack(anchor="w")
        row = ttk.Frame(path_box, style="Card.TFrame")
        row.pack(fill="x", pady=(7, 0))
        ttk.Entry(row, textvariable=self.path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="اختيار مجلد", command=self.choose_folder).pack(side="left", padx=(10, 0))
        actions = ttk.Frame(tab, style="Card.TFrame")
        actions.pack(fill="x", pady=(0, 12))
        ttk.Button(actions, text="معاينة بدون نقل", command=lambda: self.run_once(True)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="فرز الملفات الآن", style="Accent.TButton", command=lambda: self.run_once(False)).pack(side="left", padx=8)
        ttk.Button(actions, text="بدء المراقبة", style="Accent.TButton", command=self.start_monitor).pack(side="left", padx=8)
        ttk.Button(actions, text="إيقاف المراقبة", style="Danger.TButton", command=self.stop_monitor).pack(side="left", padx=8)
        ttk.Button(actions, text="فتح السجل", command=self.open_log).pack(side="right")
        status = ttk.Frame(tab, style="Card.TFrame")
        status.pack(fill="x", pady=(0, 12))
        ttk.Label(status, text="الحالة:").pack(side="left")
        ttk.Label(status, textvariable=self.status_var, style="Status.TLabel").pack(side="left", padx=8)
        log_box = ttk.LabelFrame(tab, text="سجل العمليات", padding=10)
        log_box.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_box, bg="#020617", fg="#cbd5e1", insertbackground="white", relief="flat", font=("Consolas", 10), wrap="none")
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(log_box, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set, state="disabled")
        self.append_log("مرحبًا. استخدم المعاينة قبل الفرز أول مرة.\n")

    def build_categories(self):
        tab = self.categories_tab
        ttk.Label(tab, text="أدر التصنيفات والامتدادات وسيتم حفظ التعديلات فورًا.").pack(anchor="w", pady=(0, 12))
        toolbar = ttk.Frame(tab, style="Card.TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(toolbar, text="إضافة تصنيف", style="Accent.TButton", command=self.add_category).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="تعديل المحدد", command=self.edit_category).pack(side="left", padx=8)
        ttk.Button(toolbar, text="حذف المحدد", style="Danger.TButton", command=self.delete_category).pack(side="left", padx=8)
        ttk.Button(toolbar, text="إعادة تحميل", command=self.refresh_categories).pack(side="right")
        table_box = ttk.Frame(tab, style="Card.TFrame")
        table_box.pack(fill="both", expand=True)
        self.category_tree = ttk.Treeview(table_box, columns=("category", "extensions", "count"), show="headings", selectmode="browse")
        self.category_tree.heading("category", text="التصنيف / المجلد")
        self.category_tree.heading("extensions", text="الامتدادات")
        self.category_tree.heading("count", text="العدد")
        self.category_tree.column("category", width=260, anchor="w")
        self.category_tree.column("extensions", width=560, anchor="w")
        self.category_tree.column("count", width=80, anchor="center")
        self.category_tree.pack(side="left", fill="both", expand=True)
        category_scroll = ttk.Scrollbar(table_box, orient="vertical", command=self.category_tree.yview)
        category_scroll.pack(side="right", fill="y")
        self.category_tree.configure(yscrollcommand=category_scroll.set)
        self.category_tree.bind("<Double-1>", lambda _event: self.edit_category())

    def build_settings(self):
        tab = self.settings_tab
        ttk.Label(tab, text="تُحفظ الإعدادات تلقائيًا في config.json عند كل تغيير.").pack(anchor="w", pady=(0, 18))
        card = ttk.Frame(tab, style="Card.TFrame", padding=18)
        card.pack(fill="x", anchor="n")
        ttk.Checkbutton(card, text="تقسيم الملفات داخل التصنيف حسب السنة والشهر (YYYY-MM)", variable=self.group_month_var, command=self.save_settings).pack(anchor="w", pady=8)
        ttk.Label(card, text="طريقة التعامل مع المكرر المتطابق:").pack(anchor="w", pady=(18, 5))
        combo = ttk.Combobox(card, textvariable=self.duplicate_mode_var, state="readonly", values=("نقل إلى مجلد _Duplicates", "إضافة رقم تسلسلي (1)"), width=35)
        combo.pack(anchor="w")
        combo.bind("<<ComboboxSelected>>", lambda _event: self.save_settings())
        ttk.Label(card, text="المجلد الافتراضي للامتدادات غير المعروفة: Other", foreground="#94a3b8").pack(anchor="w", pady=(20, 0))
        ttk.Label(tab, text="نصيحة: جرّب المعاينة من لوحة التحكم قبل تفعيل الفرز الفعلي.", foreground="#94a3b8").pack(anchor="w", pady=18)

    def choose_folder(self):
        selected = filedialog.askdirectory(initialdir=self.path_var.get())
        if selected:
            self.path_var.set(selected)

    def load_settings(self):
        config = engine.load_config()
        self.group_month_var.set(bool(config.get("group_by_year_month", False)))
        self.duplicate_mode_var.set("نقل إلى مجلد _Duplicates" if config.get("duplicate_mode") == "duplicates_folder" else "إضافة رقم تسلسلي (1)")

    def save_settings(self):
        config = engine.load_config()
        config["group_by_year_month"] = self.group_month_var.get()
        config["duplicate_mode"] = "duplicates_folder" if self.duplicate_mode_var.get() == "نقل إلى مجلد _Duplicates" else "serial"
        try:
            engine.save_config(config)
            if self.monitor_organizer:
                self.monitor_organizer.reload_config()
            self.status_var.set("تم حفظ الإعدادات")
        except Exception as exc:
            messagebox.showerror("خطأ في الحفظ", str(exc))

    def refresh_categories(self):
        if not hasattr(self, "category_tree"):
            return
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        categories = engine.load_config().get("categories", {})
        for category, extensions in sorted(categories.items()):
            self.category_tree.insert("", "end", iid=category, values=(category, ", ".join(extensions), len(extensions)))

    def add_category(self):
        dialog = CategoryDialog(self, "إضافة تصنيف")
        self.wait_window(dialog)
        if dialog.result:
            category, extensions = dialog.result
            config = engine.load_config()
            if category in config["categories"]:
                messagebox.showerror("التصنيف موجود", "يوجد تصنيف بهذا الاسم بالفعل.")
                return
            config["categories"][category] = extensions
            engine.save_config(config)
            self.refresh_categories()
            self.reload_monitor_config()

    def edit_category(self):
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showinfo("اختيار مطلوب", "اختر تصنيفًا أولًا.")
            return
        old = selected[0]
        config = engine.load_config()
        dialog = CategoryDialog(self, "تعديل التصنيف", old, config["categories"].get(old, []))
        self.wait_window(dialog)
        if dialog.result:
            new, extensions = dialog.result
            if new != old and new in config["categories"]:
                messagebox.showerror("التصنيف موجود", "يوجد تصنيف بهذا الاسم بالفعل.")
                return
            del config["categories"][old]
            config["categories"][new] = extensions
            engine.save_config(config)
            self.refresh_categories()
            self.reload_monitor_config()

    def delete_category(self):
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showinfo("اختيار مطلوب", "اختر تصنيفًا أولًا.")
            return
        category = selected[0]
        if not messagebox.askyesno("تأكيد الحذف", f"حذف التصنيف {category}؟\nلن تُحذف الملفات الموجودة داخله."):
            return
        config = engine.load_config()
        config["categories"].pop(category, None)
        engine.save_config(config)
        self.refresh_categories()
        self.reload_monitor_config()

    def reload_monitor_config(self):
        if self.monitor_organizer:
            self.monitor_organizer.reload_config()
        self.status_var.set("تم تحديث التصنيفات")

    def run_once(self, dry_run: bool):
        if self.operation_running:
            messagebox.showinfo("عملية جارية", "انتظر انتهاء العملية الحالية.")
            return
        path = Path(self.path_var.get()).expanduser()
        if not path.is_dir():
            messagebox.showerror("مجلد غير موجود", str(path))
            return
        if not dry_run and not messagebox.askyesno("تأكيد الفرز", "سيتم نقل الملفات الموجودة الآن. هل تريد المتابعة؟"):
            return
        self.operation_running = True
        self.status_var.set("جارٍ التنفيذ...")
        self.append_log("\n--- بدء المعالجة ---\n")
        def worker():
            organizer = engine.Organizer(path.resolve(), dry_run=dry_run)
            organizer.sweep()
            organizer.pool.shutdown(wait=True)
            self.after(0, lambda: self.operation_done("اكتملت المعالجة"))
        threading.Thread(target=worker, daemon=True).start()

    def operation_done(self, message):
        self.operation_running = False
        self.status_var.set(message)

    def start_monitor(self):
        if self.monitor_observer:
            messagebox.showinfo("المراقبة", "المراقبة تعمل بالفعل.")
            return
        path = Path(self.path_var.get()).expanduser()
        if not path.is_dir():
            messagebox.showerror("مجلد غير موجود", str(path))
            return
        self.monitor_organizer = engine.Organizer(path.resolve())
        self.monitor_observer = engine.Observer()
        self.monitor_observer.schedule(engine.Handler(self.monitor_organizer), str(path.resolve()), recursive=False)
        self.monitor_observer.start()
        self.monitor_organizer.sweep()
        self.status_var.set("المراقبة تعمل")
        self.append_log(f"بدأت المراقبة: {path.resolve()}\n")

    def stop_monitor(self):
        if self.monitor_observer:
            self.monitor_observer.stop()
            self.monitor_observer.join(timeout=5)
            self.monitor_observer = None
        if self.monitor_organizer:
            self.monitor_organizer.close()
            self.monitor_organizer = None
        self.status_var.set("المراقبة متوقفة")
        self.append_log("تم إيقاف المراقبة.\n")

    def open_log(self):
        path = engine.get_app_dir() / "organizer.log"
        path.touch(exist_ok=True)
        try:
            os.startfile(path)
        except AttributeError:
            subprocess.Popen(["xdg-open", str(path)])

    def append_log(self, text: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def drain_logs(self):
        while True:
            try:
                self.append_log(self.log_queue.get_nowait() + "\n")
            except queue.Empty:
                break
        self.after(150, self.drain_logs)

    def close(self):
        self.stop_monitor()
        engine.log.removeHandler(self.log_handler)
        self.destroy()


if __name__ == "__main__":
    OrganizerGUI().mainloop()
