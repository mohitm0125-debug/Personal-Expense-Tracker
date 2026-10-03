import json
import random
import tkinter as tk
from datetime import date, datetime
from tkinter import ttk, messagebox, filedialog

# ---------- Colours ----------
BG = "#f1f5f9"
SIDE = "#0f172a"
WHITE = "#ffffff"
TEXT = "#0f172a"
MUTED = "#64748b"
GREEN = "#16a34a"
RED = "#dc2626"
BLUE = "#2563eb"
AMBER = "#d97706"
GREY = "#475569"

FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
TITLE = ("Segoe UI", 20, "bold")


def round_rect(c, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


class Card(tk.Canvas):
    """Rounded summary card that stretches with the window."""

    def __init__(self, parent, title, colour, h=110):
        super().__init__(parent, height=h, bg=BG, highlightthickness=0)
        self.colour = colour
        self.h = h
        self.create_text(20, 30, text=title, anchor="w", fill="white", font=("Segoe UI", 11))
        self.value = self.create_text(20, 70, text="0.00", anchor="w", fill="white",
                                      font=("Segoe UI", 24, "bold"))
        self.bind("<Configure>", self._redraw)

    def _redraw(self, e):
        self.delete("bg")
        shape = round_rect(self, 2, 2, e.width - 2, self.h - 2, 18, fill=self.colour,
                           outline=self.colour, tags="bg")
        self.tag_lower(shape)

    def set(self, amount):
        self.itemconfig(self.value, text=f"{amount:,.2f}")


def flat_button(parent, text, colour, command, **kw):
    b = tk.Button(parent, text=text, command=command, bg=colour, fg="white",
                  activebackground=colour, activeforeground="white", relief="flat",
                  bd=0, font=FONT_B, cursor="hand2", **kw)
    return b


TABLE_COLS = ("No", "Type", "ID", "Date", "Source / Category", "Amount", "Description")
TABLE_WIDTHS = (50, 75, 55, 95, 130, 105, 160)
TABLE_ANCHORS = ("center",) * 7  # every cell and heading centred
TABLE_STRETCH = ("Source / Category", "Description")


def make_table(parent, height=10):
    """Bordered table with aligned headings, striped rows and a scrollbar."""
    wrap = tk.Frame(parent, bg="#cbd5e1", padx=1, pady=1)
    inner = tk.Frame(wrap, bg=WHITE)
    inner.pack(fill="both", expand=True)
    tree = ttk.Treeview(inner, columns=TABLE_COLS, show="headings", height=height, selectmode="extended")
    for c, w, a in zip(TABLE_COLS, TABLE_WIDTHS, TABLE_ANCHORS):
        tree.heading(c, text=c, anchor=a)
        tree.column(c, width=w, minwidth=40, anchor=a, stretch=c in TABLE_STRETCH)
    tree.tag_configure("even", background=WHITE)
    tree.tag_configure("odd", background="#f1f5f9")
    tree.tag_configure("Income", foreground=GREEN)
    tree.tag_configure("Expense", foreground=RED)
    sb = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return wrap, tree


def table_row(n, t):
    """Values + tags for one transaction row."""
    kind = t["Type Of Transaction"]
    detail = t.get("Source") or t.get("Category", "")
    sign = "+" if kind == "Income" else "-"
    values = (n, kind, t["Transaction id"], t["Date"], detail,
              f"{sign}{t['Amount']:,.2f}", str(t.get("Description", "")).strip())
    return values, (kind, "odd" if n % 2 == 0 else "even")


class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Expense Tracker")
        self.geometry("1050x660")
        self.minsize(900, 560)
        self.configure(bg=BG)

        self.income = []
        self.expense = []

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=FONT, background=WHITE,
                        fieldbackground=WHITE, borderwidth=0)
        style.configure("Treeview.Heading", font=FONT_B, background="#e2e8f0",
                        foreground=TEXT, relief="groove", borderwidth=1, padding=(8, 7))
        style.map("Treeview", background=[("selected", "#bfdbfe")],
                  foreground=[("selected", TEXT)])

        self._build_sidebar()
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)

        self.pages = {}
        for name, cls in (("Dashboard", DashboardPage), ("Add Income", FormPage),
                          ("Add Expense", FormPage), ("Transactions", TransactionsPage)):
            if cls is FormPage:
                page = cls(self.content, self, "Income" if name == "Add Income" else "Expense")
            else:
                page = cls(self.content, self)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[name] = page

        self.show("Dashboard")
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

    # ---------- Layout ----------
    def _build_sidebar(self):
        side = tk.Frame(self, bg=SIDE, width=210)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(side, text="💰 Expense\nTracker", bg=SIDE, fg="white",
                 font=("Segoe UI", 16, "bold"), justify="left").pack(anchor="w", padx=20, pady=(28, 24))

        items = [
            ("Dashboard", "Dashboard", GREY, lambda: self.show("Dashboard")),
            ("Add Income", "＋  Add Income", GREEN, lambda: self.show("Add Income")),
            ("Add Expense", "－  Add Expense", RED, lambda: self.show("Add Expense")),
            ("Transactions", "Transactions", BLUE, lambda: self.show("Transactions")),
        ]
        for _, label, colour, cmd in items:
            flat_button(side, label, colour, cmd, anchor="w", padx=16).pack(
                fill="x", padx=16, pady=5, ipady=7)

        tk.Frame(side, bg=SIDE).pack(expand=True, fill="both")

        flat_button(side, "Save Data", BLUE, self.save_data).pack(fill="x", padx=16, pady=5, ipady=6)
        flat_button(side, "Load Data", AMBER, self.load_data).pack(fill="x", padx=16, pady=5, ipady=6)
        flat_button(side, "Exit", "#334155", self.exit_app).pack(fill="x", padx=16, pady=(5, 20), ipady=6)

    def show(self, name):
        page = self.pages[name]
        if hasattr(page, "refresh"):
            page.refresh()
        page.tkraise()

    def refresh_all(self):
        for p in self.pages.values():
            if hasattr(p, "refresh"):
                p.refresh()

    # ---------- Data helpers ----------
    def totals(self):
        inc = sum(i["Amount"] for i in self.income)
        exp = sum(e["Amount"] for e in self.expense)
        return inc, exp, inc - exp

    def new_id(self):
        used = {t["Transaction id"] for t in self.income + self.expense}
        while True:
            n = random.randint(1000, 10000)
            if n not in used:
                return n

    def add_transaction(self, kind, amount, detail, day, desc):
        if kind == "Income":
            rec = {"Type Of Transaction": "Income", "Transaction id": self.new_id(),
                   "Amount": amount, "Source": detail, "Date": day, "Description": desc}
            self.income.append(rec)
        else:
            rec = {"Type Of Transaction": "Expense", "Transaction id": self.new_id(),
                   "Amount": amount, "Category": detail, "Date": day, "Description": desc}
            self.expense.append(rec)
        self.refresh_all()

    def delete_transaction(self, tid):
        self.income = [i for i in self.income if i["Transaction id"] != tid]
        self.expense = [e for e in self.expense if e["Transaction id"] != tid]
        self.refresh_all()

    # ---------- Save / Load / Exit ----------
    def save_data(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            try:
                with open(path, "r") as f:
                    old = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                old = {"Income": [], "Expense": []}
            for i in self.income:
                if i not in old["Income"]:
                    old["Income"].append(i)
            for e in self.expense:
                if e not in old["Expense"]:
                    old["Expense"].append(e)
            with open(path, "w") as f:
                json.dump(old, f, indent=4)
            messagebox.showinfo("Saved", "Data saved successfully.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def load_data(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.income = data["Income"]
            self.expense = data["Expense"]
            self.refresh_all()
            messagebox.showinfo("Loaded", f"Data loaded from\n{path}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def exit_app(self):
        if self.income or self.expense:
            ans = messagebox.askyesnocancel("Exit", "Do you want to save your data before exiting?")
            if ans is None:
                return
            if ans:
                self.save_data()
        self.destroy()


class DashboardPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        tk.Label(self, text="Dashboard", font=TITLE, bg=BG, fg=TEXT).pack(anchor="w", padx=30, pady=(25, 15))

        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=30)
        self.c_inc = Card(row, "Total Income", GREEN)
        self.c_exp = Card(row, "Total Expense", RED)
        self.c_bal = Card(row, "Current Balance", BLUE)
        for i, c in enumerate((self.c_inc, self.c_exp, self.c_bal)):
            c.grid(row=0, column=i, sticky="ew", padx=(0, 0 if i == 2 else 16))
            row.columnconfigure(i, weight=1, uniform="cards")

        tk.Label(self, text="Recent Transactions", font=("Segoe UI", 13, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", padx=30, pady=(25, 8))

        wrap, self.tree = make_table(self, height=10)
        wrap.pack(fill="both", expand=True, padx=30)

        self.footer = tk.Label(self, text="", bg=BG, fg=MUTED, font=FONT)
        self.footer.pack(anchor="w", padx=30, pady=(8, 16))

    def refresh(self):
        inc, exp, bal = self.app.totals()
        self.c_inc.set(inc)
        self.c_exp.set(exp)
        self.c_bal.set(bal)
        self.tree.delete(*self.tree.get_children())
        allt = sorted(self.app.income + self.app.expense, key=lambda t: t["Date"], reverse=True)
        for n, t in enumerate(allt[:30], start=1):
            values, tags = table_row(n, t)
            self.tree.insert("", "end", values=values, tags=tags)
        self.footer.config(text=f"Showing {min(len(allt), 30)} of {len(allt)} transaction(s) - "
                                f"open Transactions to search or delete")


class FormPage(tk.Frame):
    def __init__(self, parent, app, kind):
        super().__init__(parent, bg=BG)
        self.app = app
        self.kind = kind
        colour = GREEN if kind == "Income" else RED

        tk.Label(self, text=f"Add {kind}", font=TITLE, bg=BG, fg=TEXT).pack(anchor="w", padx=30, pady=(25, 15))

        card = tk.Canvas(self, bg=BG, highlightthickness=0)
        card.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        card.bind("<Configure>", lambda e: self._draw_bg(card, e.width, e.height))
        self.card = card

        form = tk.Frame(card, bg=WHITE)
        card.create_window(30, 25, anchor="nw", window=form, width=520)

        self.amount = tk.StringVar()
        self.detail = tk.StringVar()
        self.day = tk.StringVar(value=str(date.today()))
        self.use_today = tk.IntVar(value=1)

        def label(text, r):
            tk.Label(form, text=text, bg=WHITE, fg=MUTED, font=FONT).grid(row=r, column=0, sticky="w", pady=(10, 2))

        label("Amount", 0)
        ttk.Entry(form, textvariable=self.amount, font=FONT).grid(row=1, column=0, sticky="ew")

        if kind == "Income":
            label("Source of income", 2)
            ttk.Entry(form, textvariable=self.detail, font=FONT).grid(row=3, column=0, sticky="ew")
        else:
            label("Category", 2)
            cb = ttk.Combobox(form, textvariable=self.detail, values=("Food", "Groceries", "Transport", "Shopping", "Bills", "Rent",
                                      "Health", "Education", "Entertainment", "Travel", "Other"),
                              state="readonly", font=FONT)
            cb.current(0)
            cb.grid(row=3, column=0, sticky="ew")

        label("Date", 4)
        drow = tk.Frame(form, bg=WHITE)
        drow.grid(row=5, column=0, sticky="ew")
        self.day_entry = ttk.Entry(drow, textvariable=self.day, font=FONT, state="disabled")
        self.day_entry.pack(side="left", fill="x", expand=True)
        tk.Checkbutton(drow, text="Today", variable=self.use_today, bg=WHITE, font=FONT,
                       command=self._toggle_date).pack(side="left", padx=10)

        label("Description", 6)
        self.desc = tk.Text(form, height=4, font=FONT, relief="solid", bd=1)
        self.desc.grid(row=7, column=0, sticky="ew")

        flat_button(form, f"Add {kind}", colour, self.submit).grid(
            row=8, column=0, sticky="ew", pady=(20, 10), ipady=8)
        form.columnconfigure(0, weight=1)

    def _draw_bg(self, c, w, h):
        c.delete("bg")
        poly = round_rect(c, 2, 2, w - 2, h - 2, 18, fill=WHITE, outline="#e2e8f0", tags="bg")
        c.tag_lower(poly)

    def _toggle_date(self):
        if self.use_today.get():
            self.day.set(str(date.today()))
            self.day_entry.config(state="disabled")
        else:
            self.day_entry.config(state="normal")

    def submit(self):
        try:
            amount = float(self.amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid amount", "Enter a valid amount greater than 0.")
            return
        detail = self.detail.get().strip()
        if not detail:
            messagebox.showwarning("Missing info", "Please fill in the " +
                                   ("source." if self.kind == "Income" else "category."))
            return
        day = str(date.today()) if self.use_today.get() else self.day.get().strip()
        try:
            datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid date", "Use the format YYYY-MM-DD.")
            return

        self.app.add_transaction(self.kind, amount, detail, day,
                                 self.desc.get("1.0", "end").strip())
        self.amount.set("")
        if self.kind == "Income":
            self.detail.set("")
        self.desc.delete("1.0", "end")
        messagebox.showinfo("Success", f"{self.kind} added.")


class TransactionsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        tk.Label(self, text="Transactions", font=TITLE, bg=BG, fg=TEXT).pack(anchor="w", padx=30, pady=(25, 10))

        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(bar, text="Search:", bg=BG, font=FONT).pack(side="left")
        self.query = tk.StringVar()
        self.query.trace_add("write", lambda *a: self.refresh())
        ttk.Entry(bar, textvariable=self.query, width=28, font=FONT).pack(side="left", padx=(6, 18))

        tk.Label(bar, text="Show:", bg=BG, font=FONT).pack(side="left")
        self.kind = tk.StringVar(value="All")
        kcb = ttk.Combobox(bar, textvariable=self.kind, values=("All", "Income", "Expense"),
                           state="readonly", width=10, font=FONT)
        kcb.pack(side="left", padx=6)
        kcb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        flat_button(bar, "Delete Selected", RED, self.delete_selected).pack(side="right", ipadx=10, ipady=4)

        wrap, self.tree = make_table(self, height=14)
        wrap.pack(fill="both", expand=True, padx=30)

        self.footer = tk.Label(self, text="", bg=BG, fg=MUTED, font=FONT)
        self.footer.pack(anchor="w", padx=30, pady=10)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        q = self.query.get().strip().lower()
        k = self.kind.get()
        rows = []
        if k in ("All", "Income"):
            rows += self.app.income
        if k in ("All", "Expense"):
            rows += self.app.expense

        n = 0
        for t in rows:
            detail = t.get("Source") or t.get("Category", "")
            desc = str(t.get("Description", "")).strip()
            hay = f"{t['Date']} {t['Amount']} {t['Transaction id']} {detail} {desc}".lower()
            if q and q not in hay:
                continue
            n += 1
            values, tags = table_row(n, t)
            self.tree.insert("", "end", iid=str(t["Transaction id"]), values=values, tags=tags)
        self.footer.config(text=f"{n} transaction(s) shown")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a transaction first.")
            return
        if messagebox.askyesno("Confirm", f"Delete {len(sel)} transaction(s)?"):
            for iid in sel:
                self.app.delete_transaction(int(iid))


if __name__ == "__main__":
    ExpenseApp().mainloop()