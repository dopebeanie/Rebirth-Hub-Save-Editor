#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebirth Pub - редактор сохранений (золото, AP, выносливость, осколки, отношения, предметы)

Формат сейва: AES-128-ECB(key="(H+MbQeThWmZq4t7") -> GZip -> MessagePack -> JSON

Примеры:
  python rebirth_save_editor.py --gold 999999999
  python rebirth_save_editor.py --ap 99 --stamina 999 --souljam 99999
  python rebirth_save_editor.py --favor all 999
  python rebirth_save_editor.py --item Chocolate 99
  python rebirth_save_editor.py --all-items 999
  python rebirth_save_editor.py --info
  python rebirth_save_editor.py --list-items
  python rebirth_save_editor.py --menu
"""
import argparse
import gzip
import io
import json
import os
import sys
import time
from Crypto.Cipher import AES
import msgpack

KEY = b"(H+MbQeThWmZq4t7"
DEFAULT_GAME_DIR = r"D:\Games\Steam\steamapps\common\Rebirth Pub"

# CostID: id -> (краткое имя, русское имя)
COSTS = {
    1: "Золото",
    2: "SoulJam (Осколки/Алмазы)",
    3: "AP",
    4: "Выносливость",
    60: "Очки навыков (SP)",
}
COST_KEYS = {"gold": 1, "souljam": 2, "ap": 3, "stamina": 4, "sp": 60, "skillpoint": 60}

HEROINES = {1: "Николь (Nicole)", 2: "Айрин (Irene)", 3: "Серена (Serena)"}
HEROINE_KEYS = {"nicole": 1, "irene": 2, "serena": 3, "all": None}

# ItemID: имя -> id
ITEM_ENUM = {
    "NormalRecipePiece": 11, "RareRecipePiece": 12, "LegendaryRecipePiece": 13,
    "NormalCostumePiece": 101, "RareCostumePiece": 102, "LegendaryCostumePiece": 103,
    "NormalRelicPiece": 201, "RareRelicPiece": 202, "LegendaryRelicPiece": 203,
    "Ruby": 301, "Sapphire": 302, "Emerald": 303, "Topaz": 304,
    "NormalRecipe": 311, "RareRecipe": 312, "LegendaryRecipe": 313,
    "Chocolate": 1001, "EnergyBar": 1002, "EnergyDrink": 1003,
    "LegendaryMushroom": 1004, "HolyWater": 1005,
    "CookieSet": 1011, "StrawberryCake": 1012,
    "Bouquet": 1021, "PoetryBook": 1022, "LuxuryPerfume": 1023,
    "StuffedDoll": 1031, "LuxuryCushion": 1032, "SnowGlobe": 1033,
    "SilkScarf": 1041, "VintageWine": 1042, "JewelMusicBox": 1043,
    "LovePotion": 1051,
    "RedPetal": 1061, "BluePetal": 1062,
    "SkillBook": 1071, "AdvSkillBook": 1072,
    "MagicalTeaLeaf": 1081, "SacredTeaLeaf": 1082,
    "MysteryBox": 1091, "AdvMysteryBox": 1092,
    "SecretMapA": 10001, "SecretMapB": 10002, "SecretMapC": 10003, "SecretMapD": 10004,
    "H_Document_Normal_Lying_HandJob": 10101, "H_Document_Normal_Spreading": 10102,
    "H_Document_Normal_Touch_Breast": 10103, "H_Document_Normal_Sit_Doggy": 10104,
    "H_Document_Normal_69": 10105, "H_Document_Normal_Cunnlingus": 10106,
    "H_Document_Normal_Stand_Side": 10107, "H_Document_Normal_Stand_Missionary": 10108,
    "H_Document_Normal_Sit_Touch_Breast": 10109, "H_Document_Normal_Prone": 10110,
    "H_Document_Special_Foot_Job": 10201, "H_Document_Special_Rimming": 10202,
    "H_Document_Special_Spanking": 10203, "H_Document_Special_Anal_Bodybuilder": 10204,
}


def load_item_names(game_dir=DEFAULT_GAME_DIR):
    """Названия предметов: русские из локализации, иначе английские (ID -> имя)."""
    names = {}
    try:
        with io.open(os.path.join(game_dir, "LocalizeData", "ru", "Item.json"), "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        for k, v in d.items():
            if k.startswith("Item_") and isinstance(v, dict) and "text" in v:
                en = k[5:]
                if en in ITEM_ENUM:
                    names[ITEM_ENUM[en]] = v["text"]
    except Exception:
        pass
    for name, iid in ITEM_ENUM.items():
        names.setdefault(iid, name)
    return names


def decrypt(data):
    aes = AES.new(KEY, AES.MODE_ECB)
    dec = aes.decrypt(data)
    pad = dec[-1]
    if 1 <= pad <= 16 and all(b == pad for b in dec[-pad:]):
        dec = dec[:-pad]
    return json.loads(msgpack.unpackb(gzip.decompress(dec), raw=False))


def encrypt(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    packed = msgpack.packb(s, use_bin_type=True)
    z = gzip.compress(packed)
    padlen = 16 - (len(z) % 16)
    z = z + bytes([padlen]) * padlen
    return AES.new(KEY, AES.MODE_ECB).encrypt(z)


def read_obj(path):
    with open(path, "rb") as f:
        return decrypt(f.read())


def write_obj(path, obj, backup=True):
    out = encrypt(obj)
    assert decrypt(out) == obj, "round-trip mismatch"
    if backup:
        bak = path + "." + time.strftime("%Y%m%d_%H%M%S") + ".bak"
        with open(path, "rb") as f:
            open(bak, "wb").write(f.read())
    with open(path, "wb") as f:
        f.write(out)
    return bak


def all_target_paths(path):
    """Возвращает [path] + зеркала сейва в Goldberg (GSE) cloud, если они есть."""
    out = [path]
    fname = os.path.basename(path)
    appdata = os.environ.get("APPDATA", "")
    base = os.path.join(appdata, "GSE Saves")
    if os.path.isdir(base):
        for d in os.listdir(base):
            remote = os.path.join(base, d, "remote")
            if os.path.isdir(remote) and os.path.exists(os.path.join(remote, fname)):
                out.append(os.path.join(remote, fname))
    return out


def get_cost(obj, cost_id):
    d = json.loads(obj["costData"])
    return d.get(str(cost_id))


def set_cost(obj, cost_id, amount):
    d = json.loads(obj["costData"])
    key = str(cost_id)
    if key not in d:
        d[key] = {"id": cost_id, "ID": cost_id}
    d[key]["HaveAmount"] = amount
    obj["costData"] = json.dumps(d, ensure_ascii=False, separators=(",", ":"))


def set_favor(obj, heroine_id, amount):
    d = json.loads(obj["heroineData"])
    key = str(heroine_id)
    if key not in d:
        d[key] = {"id": heroine_id, "ID": heroine_id, "Datas": {}}
    d[key]["Favor"] = amount
    obj["heroineData"] = json.dumps(d, ensure_ascii=False, separators=(",", ":"))


def set_item(obj, item_id, amount):
    d = json.loads(obj["itemData"])
    key = str(item_id)
    if key not in d:
        d[key] = {"id": item_id, "ID": item_id, "Datas": {}}
    d[key]["HaveAmount"] = amount
    obj["itemData"] = json.dumps(d, ensure_ascii=False, separators=(",", ":"))


def show_info(obj, game_dir=DEFAULT_GAME_DIR):
    names = load_item_names(game_dir)
    print("== Валюты ==")
    d = json.loads(obj["costData"])
    for cid, cname in COSTS.items():
        e = d.get(str(cid), {})
        print("  %-32s %s" % (cname + ":", e.get("HaveAmount", 0)))
    print("\n== Отношения (Favor) ==")
    h = json.loads(obj["heroineData"])
    for hid, hname in HEROINES.items():
        e = h.get(str(hid), {})
        print("  %-20s %s" % (hname + ":", e.get("Favor", 0)))
    print("\n== Предметы (с количеством > 0) ==")
    it = json.loads(obj["itemData"])
    for k in sorted(it.keys(), key=lambda x: (x != "-1", int(x))):
        e = it[k]
        cnt = e.get("HaveAmount", 0)
        if cnt:
            nm = names.get(int(k), "Item " + k)
            print("  %-8s %-45s x%d" % (k, nm, cnt))


def list_items(game_dir=DEFAULT_GAME_DIR):
    names = load_item_names(game_dir)
    print("ID      Название")
    for iid in sorted(ITEM_ENUM.values()):
        print("  %-6d %s" % (iid, names.get(iid, iid)))


def resolve_item(s, names):
    """Принимает ID или имя (англ./рус.)."""
    if s.isdigit():
        return int(s)
    low = s.lower()
    for en, iid in ITEM_ENUM.items():
        if en.lower() == low:
            return iid
    for iid, name in names.items():
        if name and name.lower() == low:
            return iid
    raise ValueError("Не найден предмет: %s" % s)


def menu_loop(path, game_dir=DEFAULT_GAME_DIR):
    while True:
        obj = read_obj(path)
        print("\n=== Rebirth Pub: редактор сейва ===")
        show_info(obj, game_dir)
        print("\nЧто меняем?")
        print("  1. Золото")
        print("  2. AP")
        print("  3. Выносливость")
        print("  4. Осколки (SoulJam)")
        print("  5. Очки навыков (SP)")
        print("  6. Отношения (Favor)")
        print("  7. Предмет")
        print("  8. Все предметы")
        print("  0. Выход")
        ch = input("> ").strip()
        if ch == "0":
            break
        try:
            if ch == "1":
                set_cost(obj, 1, int(input("Золото: ")))
            elif ch == "2":
                set_cost(obj, 3, int(input("AP: ")))
            elif ch == "3":
                set_cost(obj, 4, int(input("Выносливость: ")))
            elif ch == "4":
                set_cost(obj, 2, int(input("Осколки: ")))
            elif ch == "5":
                set_cost(obj, 60, int(input("SP: ")))
            elif ch == "6":
                who = input("Кому (nicole/irene/serena/all): ").strip().lower()
                amt = int(input("Сколько: "))
                hid = HEROINE_KEYS.get(who)
                if hid is None and who != "all":
                    print("Неверное имя героини")
                    continue
                targets = list(HEROINE_KEYS.values()) if who == "all" else [hid]
                for t in targets:
                    if t is not None:
                        set_favor(obj, t, amt)
            elif ch == "7":
                item = input("Предмет (ID или имя): ").strip()
                amt = int(input("Количество: "))
                set_item(obj, resolve_item(item, load_item_names(game_dir)), amt)
            elif ch == "8":
                amt = int(input("Количество всем предметам: "))
                for iid in ITEM_ENUM.values():
                    set_item(obj, iid, amt)
            else:
                print("Неизвестный пункт")
                continue
            for target in all_target_paths(path):
                mbak = write_obj(target, obj)
                print("Записано: %s%s" % (target, "  (бэкап: %s)" % mbak if mbak else ""))
        except Exception as e:
            print("Ошибка: %s" % e)


def main():
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Rebirth Pub - редактор сохранений")
    ap.add_argument("save", nargs="?", help="путь к saveDataXX.bin (по умолчанию слот 1)")
    ap.add_argument("--game-dir", default=DEFAULT_GAME_DIR)
    ap.add_argument("--slot", type=int, default=1, help="номер слота сохранения (1-30)")
    ap.add_argument("--gold", type=int)
    ap.add_argument("--ap", type=int)
    ap.add_argument("--stamina", type=int)
    ap.add_argument("--souljam", type=int)
    ap.add_argument("--sp", type=int)
    ap.add_argument("--favor", nargs=2, metavar=("WHO", "AMOUNT"))
    ap.add_argument("--item", action="append", nargs=2, metavar=("ITEM", "AMOUNT"))
    ap.add_argument("--all-items", type=int)
    ap.add_argument("--info", action="store_true")
    ap.add_argument("--list-items", action="store_true")
    ap.add_argument("--list-costs", action="store_true")
    ap.add_argument("--menu", action="store_true")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()

    game_dir = args.game_dir
    if args.save:
        path = args.save
    else:
        path = os.path.join(game_dir, "SaveDir", "saveData%02d.bin" % args.slot)

    if not os.path.exists(path):
        print("Файл не найден: %s" % path)
        sys.exit(1)

    if args.list_items:
        list_items(game_dir)
        return

    obj = read_obj(path)
    if args.info:
        show_info(obj, game_dir)
        return

    changes = False

    def do_cost(cid, name):
        global changes
        if name is not None:
            set_cost(obj, cid, name)
            print("  %s -> %d" % (COSTS[cid], name))
            changes = True

    do_cost(1, args.gold)
    do_cost(3, args.ap)
    do_cost(4, args.stamina)
    do_cost(2, args.souljam)
    do_cost(60, args.sp)

    if args.favor:
        who, amt = args.favor[0].strip().lower(), int(args.favor[1])
        hid = HEROINE_KEYS.get(who)
        targets = list(HEROINE_KEYS.values()) if who == "all" else [hid]
        if hid is None and who != "all":
            print("Неверное имя героини: %s (nicole/irene/serena/all)" % who)
            sys.exit(1)
        for t in targets:
            if t is not None:
                set_favor(obj, t, amt)
                print("  %s -> %d" % (HEROINES[t], amt))
        changes = True

    if args.item:
        names = load_item_names(game_dir)
        for item, amt_str in args.item:
            try:
                iid = resolve_item(item, names)
            except ValueError as e:
                print("Ошибка: %s" % e)
                sys.exit(1)
            amt = int(amt_str)
            set_item(obj, iid, amt)
            print("  Предмет %s (%d) -> x%d" % (names.get(iid, iid), iid, amt))
        changes = True

    if args.all_items is not None:
        for iid in ITEM_ENUM.values():
            set_item(obj, iid, args.all_items)
        print("  Все предметы -> x%d" % args.all_items)
        changes = True

    if args.menu:
        menu_loop(path, game_dir)
        return

    if not changes:
        ap.print_help()
        sys.exit(0)

    bak = write_obj(path, obj, backup=not args.no_backup)
    print("\nГотово. Записано в %s" % path)
    if bak:
        print("Бэкап: %s" % bak)
    for mirror in all_target_paths(path)[1:]:
        mbak = write_obj(mirror, obj, backup=not args.no_backup)
        print("Зеркало GSE: %s" % mirror)
        if mbak:
            print("  бэкап: %s" % mbak)
    print("\nВАЖНО: закройте игру перед применением, иначе автосейв перезапишет файл.")


if __name__ == "__main__":
    main()