# Rebirth-Hub-Save-Editor
Rebirth Pub Save Editor — edit gold, AP, stamina, currency, relationships and items in your save with one click.

# 💰 Rebirth Pub Save Editor

> ⚙️ **Графический редактор сохранений для игры Rebirth Pub**
> ⚙️ **A graphical save editor for the game Rebirth Pub**

Edit your save in a couple of clicks — no Python, no Cheat Engine, no manual file editing.
Меняй значения в сейве в пару кликов — без Python, без Cheat Engine и без ручной возни с файлами.

---

## 🇬🇧 English

### 🚀 Features

Change in the save (slot 1-30):

- 💛 **Gold**
- 💎 **Soul Shards (SoulJam)** — premium currency
- ⚡ **AP** — action points
- 🏃 **Stamina**
- 📚 **Skill Points (SP)**
- 💕 **Relationships (Favor)** with all heroines: Nicole, Irene, Serena
- 🎒 **Items** — any item by name or ID, or all items at once

Extras:

- ✅ Automatically updates **both save locations**:
  - the game folder `SaveDir/`
  - Goldberg Steam Emulator (GSE) cloud `%APPDATA%\GSE Saves\<appid>\remote\` (important for "cracked" copies)
- 🛡️ Automatic **backup** (`.bak`) before every change
- 👀 View current save values
- 📋 Full item list with Russian names
- 🌙 Dark theme, one-click **"Apply"**

### 🔧 How it works

The save file is encrypted with this chain:

```
JSON → MessagePack → GZip → AES-128-ECB (key is embedded in the game)
```

The tool fully decrypts the file, changes the fields you want, and encrypts it back — the game reads it perfectly.

### 💻 Requirements

- 🪟 Windows x64
- 🐍 **No Python or dependencies needed** — everything is packed into a single `.exe`

### 📖 Usage

1. ⬇️ Download `RebirthPub_SaveEditor.exe` from **Releases**.
2. ❌ **Close the game** (otherwise autosave will overwrite your changes).
3. ▶️ Run the exe.
4. 🎛️ Pick the save slot (default 1). If the game is in a non-standard folder — press **"Browse..."** and select your `saveDataXX.bin`.
5. ✏️ Enter the values you want and press **"APPLY CHANGES"**.
6. 🎮 Start the game and load the save.

> ⚠️ If Windows/SmartScreen complains about an unsigned exe: **More info → Run anyway**. False positives from antivirus are normal for PyInstaller builds.

### 🖥️ Interface

- **CURRENCIES** — gold, soul shards, AP, stamina, SP
- **RELATIONSHIPS** — a separate field for each heroine
- **ITEMS** — dropdown list + quantity, add several items at once; checkbox "Give ALL items xN"
- Buttons: **Refresh from save**, **Reset**, **About**, **APPLY CHANGES**

Every apply creates a backup `<file>.2026MMDD_HHMMSS.bak` next to the save. To roll back, rename the backup back to `saveDataXX.bin` (in both folders if GSE is used).

### ⌨️ CLI version (bonus)

```
python rebirth_save_editor.py --gold 999999999
python rebirth_save_editor.py --ap 99 --stamina 999 --souljam 99999
python rebirth_save_editor.py --favor all 999
python rebirth_save_editor.py --item Chocolate 50 --item Bouquet 10
python rebirth_save_editor.py --all-items 99
python rebirth_save_editor.py --info          # current values
python rebirth_save_editor.py --list-items    # item list
python rebirth_save_editor.py --menu          # interactive menu
```

Flags can be combined. Requires `pycryptodome` and `msgpack`.

### ⚠️ Warning

- Always close the game before editing.
- Single-player tool. Use cheats at your own risk (extreme values may break a save).

---

## 🇷🇺 Русский

### 🚀 Возможности

Изменяет в сохранении (слот 1-30):

- 💛 **Золото**
- 💎 **Осколки (SoulJam)** — премиум-валюта
- ⚡ **AP** — очки действия
- 🏃 **Выносливость**
- 📚 **Очки навыков (SP)**
- 💕 **Отношения (Favor)** с героинями: Николь, Айрин, Серена
- 🎒 **Предметы** — любой предмет по названию или ID, или все сразу

Дополнительно:

- ✅ Автоматически правит **оба места хранения сейва**:
  - папку игры `SaveDir/`
  - облако Goldberg Steam Emulator (GSE) `%APPDATA%\GSE Saves\<appid>\remote\` (актуально для «пиратских» версий)
- 🛡️ Автоматический **бэкап** (`.bak`) перед каждым изменением
- 👀 Просмотр текущих значений сейва
- 📋 Список всех предметов с русскими названиями
- 🌙 Тёмная тема, применение в один клик

### 🔧 Как работает

Сейв игры зашифрован цепочкой:

```
JSON → MessagePack → GZip → AES-128-ECB (ключ вшит в игру)
```

Программа полностью расшифровывает файл, меняет нужные поля и зашифровывает обратно — игра читает его без проблем.

### 💻 Требования

- 🪟 Windows x64
- 🐍 **Никакого Python и зависимостей** — всё упаковано в один `.exe`

### 📖 Как пользоваться

1. ⬇️ Скачай `RebirthPub_SaveEditor.exe` из раздела **Releases**.
2. ❌ **Закрой игру** (иначе автосейв перезапишет изменения).
3. ▶️ Запусти exe.
4. 🎛️ Выбери слот (по умолчанию 1). Если игра в нестандартной папке — нажми **«Обзор...»** и выбери файл `saveDataXX.bin`.
5. ✏️ Впиши нужные значения и нажми **«ПРИМЕНИТЬ ИЗМЕНЕНИЯ»**.
6. 🎮 Запусти игру и загрузи сейв.

> ⚠️ Если SmartScreen ругается на неподписанный exe: **Подробнее → Выполнить в любом случае**. Ложные срабатывания антивируса — норма для PyInstaller-сборок.

### 🖥️ Интерфейс

- **ВАЛЮТЫ** — золото, осколки, AP, выносливость, SP
- **ОТНОШЕНИЯ** — отдельное поле для каждой героини
- **ПРЕДМЕТЫ** — выпадающий список + количество, можно добавить несколько; галочка «Выдать ВСЕ предметы по N»
- Кнопки: **Обновить из сейва**, **Сброс**, **О программе**, **ПРИМЕНИТЬ ИЗМЕНЕНИЯ**

Каждое применение создаёт бэкап `<файл>.2026MMDD_HHMMSS.bak` рядом с сейвом. Чтобы откатить — переименуй бэкап обратно в `saveDataXX.bin` (в обеих папках, если используется GSE).

### ⌨️ Командная строка (бонус)

```
python rebirth_save_editor.py --gold 999999999
python rebirth_save_editor.py --ap 99 --stamina 999 --souljam 99999
python rebirth_save_editor.py --favor all 999
python rebirth_save_editor.py --item Chocolate 50 --item Bouquet 10
python rebirth_save_editor.py --all-items 99
python rebirth_save_editor.py --info          # текущие значения
python rebirth_save_editor.py --list-items    # список предметов
python rebirth_save_editor.py --menu          # интерактивное меню
```

Флаги можно комбинировать. Требуется `pycryptodome` и `msgpack`.

### ⚠️ Предупреждение

- Всегда закрывай игру перед редактированием.
- Инструмент для одиночной игры. Использование читов — на свой страх и риск (слишком экстремальные значения могут «поехать» сейв).

---

## 👤 Author / Автор

Made with ❤️ by **@dopebeanie**

Telegram Channel: https://t.me/dopebeanie

Subscribe — more tools and updates coming! Подписывайся на канал — там больше инструментов и новости.
