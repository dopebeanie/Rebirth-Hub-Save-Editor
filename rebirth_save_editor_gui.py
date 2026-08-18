#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebirth Pub — редактор сохранений (GUI).

Простое окно: вводишь нужные значения валют/отношений/предметов и жмёшь «Применить».
Правятся сразу и папка игры (SaveDir), и облако Goldberg (GSE Saves).
"""
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

import rebirth_save_editor as R

AUTHOR_HANDLE = "@dopebeanie"
AUTHOR_CHANNEL = "https://t.me/dopebeanie"

# ---------- тема ----------
BG = "#1b1e2b"
PANEL = "#232737"
ENTRY_BG = "#2d3346"
FG = "#e2e8f0"
FG_DIM = "#8b93a7"
ACCENT = "#7c8cff"
ACCENT_DARK = "#5b6ce8"
OK = "#4ade80"
WARN = "#fbbf24"
ERR = "#f87171"

FONT = ("Segoe UI", 10)
FONT_SM = ("Segoe UI", 9)
FONT_TITLE = ("Segoe UI Semibold", 15)


class App:
    def __init__(self, root):
        self.root = root
        self.game_dir = R.DEFAULT_GAME_DIR

        self.slot = tk.IntVar(value=1)
        self.path_var = tk.StringVar()

        self.cost_vars = {cid: tk.StringVar() for cid in R.COSTS}
        self.favor_vars = {hid: tk.StringVar() for hid in R.HEROINES}
        self.all_items_var = tk.StringVar(value="99")
        self.use_all_items = tk.BooleanVar(value=False)

        self.item_map = {}  # "ID  Название" -> item_id
        self.pending_items = {}  # item_id -> count

        self._build_styles()
        self._build_ui()
        self.update_path()
        self.refresh()

    # ---------- стили ----------
    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, font=FONT)
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG, font=FONT)
        style.configure("Panel.TLabel", background=PANEL, foreground=FG, font=FONT)
        style.configure("Dim.TLabel", background=PANEL, foreground=FG_DIM, font=FONT_SM)
        style.configure("Title.TLabel", background=BG, foreground=FG, font=FONT_TITLE)
        style.configure("Accent.TLabel", background=PANEL, foreground=ACCENT, font=FONT)

        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=FG, insertcolor=FG,
                        bordercolor="#3b4252", lightcolor="#3b4252", darkcolor="#3b4252",
                        padding=4, font=FONT)
        style.map("TEntry", bordercolor=[("focus", ACCENT)])

        style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=FG,
                        background=PANEL, arrowcolor=FG, bordercolor="#3b4252",
                        lightcolor="#3b4252", darkcolor="#3b4252", padding=4, font=FONT)
        style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)],
                  foreground=[("readonly", FG)])

        style.configure("Primary.TButton", background=ACCENT, foreground="#0b1020",
                        bordercolor=ACCENT, focusthickness=0, padding=(14, 9), font=("Segoe UI Semibold", 11))
        style.map("Primary.TButton",
                  background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
                  bordercolor=[("active", ACCENT_DARK)])

        style.configure("Sec.TButton", background="#39405a", foreground=FG,
                        bordercolor="#39405a", focusthickness=0, padding=(10, 6), font=FONT)
        style.map("Sec.TButton", background=[("active", "#454e6e")])

        style.configure("TCheckbutton", background=PANEL, foreground=FG, font=FONT)
        style.map("TCheckbutton", background=[("active", PANEL)], foreground=[("active", FG)])

        style.configure("TSpinbox", fieldbackground=ENTRY_BG, foreground=FG,
                        background=PANEL, arrowcolor=FG, bordercolor="#3b4252",
                        lightcolor="#3b4252", darkcolor="#3b4252", padding=4, font=FONT)

        style.configure("TListbox", background=ENTRY_BG, foreground=FG,
                        bordercolor="#3b4252", font=FONT)
        self.root.option_add("*TCombobox*Listbox.background", ENTRY_BG)
        self.root.option_add("*TCombobox*Listbox.foreground", FG)

    # ---------- UI ----------
    def _build_ui(self):
        self.root.title("Rebirth Pub — Редактор сохранений")
        self.root.configure(bg=BG)
        self.root.geometry("760x640")
        self.root.minsize(720, 600)

        # шапка
        head = ttk.Frame(self.root, padding=(16, 12))
        head.pack(fill="x")
        ttk.Label(head, text="⚙ Rebirth Pub", style="Title.TLabel").pack(anchor="w")
        ttk.Label(head, text="Редактор сохранений — меняй значения и нажимай «Применить»",
                  style="Dim.TLabel").pack(anchor="w", pady=(2, 0))

        # строка сейва
        row = ttk.Frame(head)
        row.pack(fill="x", pady=(10, 0))
        ttk.Label(row, text="Слот:").pack(side="left")
        spin = ttk.Spinbox(row, from_=1, to=30, textvariable=tk.StringVar(value="1"),
                           width=4, command=self.on_slot_change)
        spin.delete(0, "end")
        spin.insert(0, "1")
        self.slot_spin = spin
        self.slot_spin.bind("<KeyRelease>", self.on_slot_change)
        spin.pack(side="left", padx=(4, 12))
        ttk.Button(row, text="Обзор...", style="Sec.TButton", command=self.browse).pack(side="left")
        ttk.Label(row, textvariable=self.path_var, style="Dim.TLabel").pack(side="left", padx=(10, 0))

        body = ttk.Frame(self.root, padding=(16, 0))
        body.pack(fill="both", expand=True)

        # --- колонка валют ---
        left = ttk.Frame(body, style="Panel.TFrame", padding=12)
        left.pack(side="left", fill="y", padx=(0, 10))
        ttk.Label(left, text="ВАЛЮТЫ", style="Accent.TLabel").pack(anchor="w")
        self.cost_entries = {}
        for cid, name in R.COSTS.items():
            f = ttk.Frame(left, style="Panel.TFrame")
            f.pack(fill="x", pady=3)
            ttk.Label(f, text=name, style="Panel.TLabel").pack(side="left")
            e = ttk.Entry(f, textvariable=self.cost_vars[cid], width=12, justify="right")
            e.pack(side="right")
            self.cost_entries[cid] = e

        ttk.Frame(left, style="Panel.TFrame", height=1).pack(fill="x", pady=8)

        ttk.Label(left, text="ОТНОШЕНИЯ (Favor)", style="Accent.TLabel").pack(anchor="w")
        self.favor_entries = {}
        for hid, name in R.HEROINES.items():
            f = ttk.Frame(left, style="Panel.TFrame")
            f.pack(fill="x", pady=3)
            ttk.Label(f, text=name, style="Panel.TLabel").pack(side="left")
            e = ttk.Entry(f, textvariable=self.favor_vars[hid], width=12, justify="right")
            e.pack(side="right")
            self.favor_entries[hid] = e

        # --- колонка предметов ---
        right = ttk.Frame(body, style="Panel.TFrame", padding=12)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(right, text="ПРЕДМЕТЫ", style="Accent.TLabel").pack(anchor="w")

        self.names = R.load_item_names(self.game_dir)
        values = []
        for iid in sorted(R.ITEM_ENUM.values()):
            label = "%d  %s" % (iid, self.names.get(iid, iid))
            self.item_map[label] = iid
            values.append(label)
        self.item_combo = ttk.Combobox(right, values=values, state="readonly", width=42)
        self.item_combo.current(0)
        self.item_combo.pack(fill="x", pady=(6, 4))

        frow = ttk.Frame(right, style="Panel.TFrame")
        frow.pack(fill="x")
        ttk.Label(frow, text="Кол-во:", style="Panel.TLabel").pack(side="left")
        self.item_count = ttk.Entry(frow, width=8)
        self.item_count.insert(0, "99")
        self.item_count.pack(side="left", padx=(6, 0))
        ttk.Button(frow, text="+ Добавить", style="Sec.TButton", command=self.add_item).pack(side="left", padx=(10, 0))

        self.items_list = tk.Listbox(right, bg=ENTRY_BG, fg=FG, selectbackground=ACCENT_DARK,
                                     selectforeground="#0b1020", height=9, highlightthickness=0,
                                     font=FONT)
        self.items_list.pack(fill="both", expand=True, pady=(8, 4))
        self.items_list.bind("<Delete>", lambda e: self.remove_selected_item())
        ttk.Button(right, text="Убрать выбранный", style="Sec.TButton",
                   command=self.remove_selected_item).pack(anchor="w")

        ttk.Frame(right, style="Panel.TFrame", height=1).pack(fill="x", pady=8)
        chk = ttk.Checkbutton(right, text="Выдать ВСЕ предметы по:", variable=self.use_all_items,
                              style="TCheckbutton")
        chk.pack(anchor="w")
        frow2 = ttk.Frame(right, style="Panel.TFrame")
        frow2.pack(fill="x", pady=(4, 0))
        e = ttk.Entry(frow2, textvariable=self.all_items_var, width=8, justify="right")
        e.pack(side="left")
        ttk.Label(frow2, text="шт.", style="Panel.TLabel").pack(side="left", padx=(6, 0))

        # --- низ: кнопки и лог ---
        bottom = ttk.Frame(self.root, padding=(16, 10))
        bottom.pack(fill="x")
        btns = ttk.Frame(bottom)
        btns.pack(fill="x")
        ttk.Button(btns, text="⟳ Обновить из сейва", style="Sec.TButton",
                   command=self.refresh).pack(side="left")
        ttk.Button(btns, text="Сброс", style="Sec.TButton", command=self.clear_fields).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="О программе", style="Sec.TButton",
                   command=self.show_about).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="ПРИМЕНИТЬ ИЗМЕНЕНИЯ", style="Primary.TButton",
                   command=self.apply).pack(side="right")

        self.log = scrolledtext.ScrolledText(self.root, height=7, bg=ENTRY_BG, fg=FG,
                                             insertbackground=FG, font=("Consolas", 9),
                                             relief="flat", state="disabled", wrap="word")
        self.log.pack(fill="x", padx=16, pady=(0, 14))

        # --- футер с крeдитами ---
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=16, pady=(0, 12))
        tk.Label(footer, text="Сделано ", bg=BG, fg=FG_DIM, font=FONT_SM).pack(side="left")
        handle = tk.Label(footer, text=AUTHOR_HANDLE, bg=BG, fg=ACCENT, cursor="hand2",
                          font=("Segoe UI Semibold", 9))
        handle.pack(side="left")
        handle.bind("<Button-1>", lambda e: self.open_channel())
        tk.Label(footer, text="  |  Telegram Channel: ", bg=BG, fg=FG_DIM, font=FONT_SM).pack(side="left")
        chan = tk.Label(footer, text=AUTHOR_CHANNEL, bg=BG, fg=ACCENT, cursor="hand2",
                        font=("Segoe UI Semibold", 9))
        chan.pack(side="left")
        chan.bind("<Button-1>", lambda e: self.open_channel())

    # ---------- крeдиты ----------
    def open_channel(self):
        webbrowser.open(AUTHOR_CHANNEL)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Rebirth Pub — Редактор сохранений\n\n"
            "Сделано с любовью by %s\n"
            "Telegram Channel: %s\n\n"
            "Меняет золото, AP, выносливость, осколки,\n"
            "отношения и предметы прямо в сейве.\n"
            "Закрывай игру перед применением!" % (AUTHOR_HANDLE, AUTHOR_CHANNEL),
            parent=self.root,
        )

    # ---------- логика ----------
    def update_path(self):
        path = os.path.join(self.game_dir, "SaveDir", "saveData%02d.bin" % self.slot.get())
        self.path_var.set(path)
        return path

    def on_slot_change(self, _=None):
        try:
            val = int(self.slot_spin.get())
        except ValueError:
            val = 1
        self.slot.set(val)
        path = self.update_path()
        if os.path.exists(path):
            self.refresh()
        else:
            self.clear_fields()

    def browse(self):
        p = filedialog.askopenfilename(title="Выберите saveDataXX.bin",
                                        initialdir=os.path.join(self.game_dir, "SaveDir"),
                                        filetypes=[("Save", "saveData*.bin"), ("All", "*.*")])
        if p:
            name = os.path.basename(p)
            if name.startswith("saveData") and name.endswith(".bin"):
                try:
                    self.slot.set(int(name[8:10]))
                except ValueError:
                    pass
            self.path_var.set(p)
            self.refresh()

    def _read_obj_from_path(self):
        path = self.path_var.get()
        if not os.path.exists(path):
            self.log_msg("Файл не найден: %s" % path, ERR)
            return None
        try:
            return R.read_obj(path)
        except Exception as e:
            self.log_msg("Не удалось прочитать сейв: %s" % e, ERR)
            return None

    def refresh(self):
        obj = self._read_obj_from_path()
        if obj is None:
            return
        cost = json_cost(obj)
        for cid in R.COSTS:
            self.cost_vars[cid].set(str(cost.get(str(cid), {}).get("HaveAmount", 0)))
        hero = json_hero(obj)
        for hid in R.HEROINES:
            self.favor_vars[hid].set(str(hero.get(str(hid), {}).get("Favor", 0)))
        self.log_msg("Загружены текущие значения: %s" % os.path.basename(self.path_var.get()), OK)

    def clear_fields(self):
        for v in self.cost_vars.values():
            v.set("")
        for v in self.favor_vars.values():
            v.set("")
        self.items_list.delete(0, "end")
        self.pending_items.clear()

    def add_item(self):
        label = self.item_combo.get()
        if not label:
            return
        iid = self.item_map.get(label)
        try:
            cnt = int(self.item_count.get())
        except ValueError:
            self.log_msg("Неверное количество предмета", WARN)
            return
        if iid is None:
            return
        self.pending_items[iid] = cnt
        self._render_pending()
        self.log_msg("+ %s x%d" % (self.names.get(iid, iid), cnt), OK)

    def remove_selected_item(self):
        sel = self.items_list.curselection()
        if not sel:
            return
        line = self.items_list.get(sel[0])
        iid = int(line.split("  ")[0].strip())
        self.pending_items.pop(iid, None)
        self._render_pending()

    def _render_pending(self):
        self.items_list.delete(0, "end")
        for iid, cnt in sorted(self.pending_items.items()):
            self.items_list.insert("end", "%d  %s x%d" % (iid, self.names.get(iid, iid), cnt))

    def apply(self):
        obj = self._read_obj_from_path()
        if obj is None:
            return
        changed = False
        try:
            for cid, var in self.cost_vars.items():
                t = var.get().strip()
                if t:
                    R.set_cost(obj, cid, int(t))
                    changed = True
            for hid, var in self.favor_vars.items():
                t = var.get().strip()
                if t:
                    R.set_favor(obj, hid, int(t))
                    changed = True
            for iid, cnt in self.pending_items.items():
                R.set_item(obj, iid, cnt)
                changed = True
            if self.use_all_items.get():
                try:
                    n = int(self.all_items_var.get().strip() or "99")
                except ValueError:
                    n = 99
                for iid in R.ITEM_ENUM.values():
                    R.set_item(obj, iid, n)
                changed = True
        except ValueError as e:
            self.log_msg("Введите целые числа: %s" % e, ERR)
            return
        except Exception as e:
            self.log_msg("Ошибка: %s" % e, ERR)
            return

        if not changed:
            self.log_msg("Нечего применять — заполните хотя бы одно поле", WARN)
            return

        targets = R.all_target_paths(self.path_var.get())
        try:
            for t in targets:
                bak = R.write_obj(t, obj)
                self.log_msg("Записано: %s  (бэкап: %s)" % (t, os.path.basename(bak)), OK)
        except Exception as e:
            self.log_msg("Ошибка записи: %s" % e, ERR)
            return
        self.log_msg("Готово! Закройте игру перед применением и загрузите сейв.", ACCENT)

    def log_msg(self, msg, color=FG):
        self.log.configure(state="normal")
        self.log.insert("end", "• " + msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


def json_cost(obj):
    return json_load(obj, "costData")


def json_hero(obj):
    return json_load(obj, "heroineData")


def json_load(obj, key):
    import json
    return json.loads(obj.get(key, "{}"))


def main():
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.2)
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()