# -*- coding: utf-8 -*-
# Add-on for the Anki program. For the window with add-ons, it implements the ability 
# to sort and color the list, it is possible to set a hint for a specific add-on.
# https://github.com/AndreyKaiu/Anki_Add-ons-window-Sort-Colors-Hint
# Version 1.3, date: 2025-04-26
import subprocess
import sys
import traceback
import os
import re
import json
import time
import aqt
import aqt.forms
import aqt.main
import anki.lang
from aqt.addons import AddonsDialog
from aqt.addons import ConfigEditor
from aqt import mw
from aqt.addons import AddonManager
from aqt.addons import GetAddons
from aqt.addons import DownloaderInstaller
from aqt.addons import download_addons
from aqt.qt import *
from aqt.qt import QApplication
from aqt import gui_hooks
from aqt.gui_hooks import addons_dialog_will_show
from aqt.gui_hooks import addons_dialog_did_change_selected_addon
from aqt.gui_hooks import dialog_manager_did_open_dialog
from aqt.utils import (askUser, showInfo, tooltip, showText, tr)
from aqt.theme import theme_manager
from datetime import datetime
from pathlib import Path
from types import MethodType
import shutil

# ========================= PYQT_VERSION ======================================
try:    
    from PyQt6.QtCore import Qt, QTimer, QRegularExpression, QSize, QEvent, QTimer
    from PyQt6.QtWidgets import QLabel, QListWidgetItem, QStyledItemDelegate, QListWidgetItem, QTextEdit, QListWidget, QDialog, QVBoxLayout
    from PyQt6.QtGui import QTextDocument, QTextCursor, QColor, QSyntaxHighlighter, QPainter, QPalette, QTextCharFormat, QFont   
    pyqt_version = "PyQt6"
except ImportError:
    from PyQt5.QtCore import Qt, QTimer, QRegularExpression, QSize, QEvent, QTimer
    from PyQt5.QtWidgets import QLabel, QListWidgetItem, QStyledItemDelegate, QListWidgetItem, QTextEdit, QListWidget, QDialog, QVBoxLayout
    from PyQt5.QtGui import QTextDocument, QTextCursor, QColor, QSyntaxHighlighter, QPainter, QPalette, QTextCharFormat, QFont
    pyqt_version = "PyQt5"  
# =============================================================================

if pyqt_version == "PyQt6":    
    QTextCursor_KeepAnchor = QTextCursor.MoveMode.KeepAnchor
    QTextDocument_FindBackward = QTextDocument.FindFlag.FindBackward    
    QEvent_Resize = QEvent.Type.Resize
    QEvent_Paint = QEvent.Type.Paint
    QEvent_Show = QEvent.Type.Show
    QEvent_WindowActivate = QEvent.Type.WindowActivate
    QTextCursor_NoMove = QTextCursor.MoveOperation.NoMove
    QTextCursor_Start = QTextCursor.MoveOperation.Start
    QTextCursor_StartOfLine = QTextCursor.MoveOperation.StartOfLine
    QTextCursor_StartOfBlock = QTextCursor.MoveOperation.StartOfBlock
    QTextCursor_StartOfWord = QTextCursor.MoveOperation.StartOfWord
    QTextCursor_PreviousBlock = QTextCursor.MoveOperation.PreviousBlock
    QTextCursor_PreviousCharacter = QTextCursor.MoveOperation.PreviousCharacter
    QTextCursor_PreviousWord = QTextCursor.MoveOperation.PreviousWord
    QTextCursor_Up = QTextCursor.MoveOperation.Up
    QTextCursor_Left = QTextCursor.MoveOperation.Left
    QTextCursor_WordLeft = QTextCursor.MoveOperation.WordLeft
    QTextCursor_End = QTextCursor.MoveOperation.End
    QTextCursor_EndOfLine = QTextCursor.MoveOperation.EndOfLine
    QTextCursor_EndOfWord = QTextCursor.MoveOperation.EndOfWord
    QTextCursor_EndOfBlock = QTextCursor.MoveOperation.EndOfBlock
    QTextCursor_NextBlock = QTextCursor.MoveOperation.NextBlock
    QTextCursor_NextCharacter = QTextCursor.MoveOperation.NextCharacter
    QTextCursor_NextWord = QTextCursor.MoveOperation.NextWord
    QTextCursor_Down = QTextCursor.MoveOperation.Down
    QTextCursor_Right = QTextCursor.MoveOperation.Right
    QTextCursor_WordRight = QTextCursor.MoveOperation.WordRight
    QTextCursor_NextCell = QTextCursor.MoveOperation.NextCell
    QTextCursor_PreviousCell = QTextCursor.MoveOperation.PreviousCell
    QTextCursor_NextRow = QTextCursor.MoveOperation.NextRow
    QTextCursor_PreviousRow = QTextCursor.MoveOperation.PreviousRow
else:    
    QTextCursor_KeepAnchor = QTextCursor.KeepAnchor
    QTextDocument_FindBackward = QTextDocument.FindBackward
    QEvent_Resize = QEvent.Resize
    QEvent_Paint = QEvent.Paint
    QEvent_Show = QEvent.Show
    QEvent_WindowActivate = QEvent.WindowActivate
    QTextCursor_NoMove = QTextCursor.NoMove
    QTextCursor_Start = QTextCursor.Start
    QTextCursor_StartOfLine = QTextCursor.StartOfLine
    QTextCursor_StartOfBlock = QTextCursor.StartOfBlock
    QTextCursor_StartOfWord = QTextCursor.StartOfWord
    QTextCursor_PreviousBlock = QTextCursor.PreviousBlock
    QTextCursor_PreviousCharacter = QTextCursor.PreviousCharacter
    QTextCursor_PreviousWord = QTextCursor.PreviousWord
    QTextCursor_Up = QTextCursor.Up
    QTextCursor_Left = QTextCursor.Left
    QTextCursor_WordLeft = QTextCursor.WordLeft
    QTextCursor_End = QTextCursor.End
    QTextCursor_EndOfLine = QTextCursor.EndOfLine
    QTextCursor_EndOfWord = QTextCursor.EndOfWord
    QTextCursor_EndOfBlock = QTextCursor.EndOfBlock
    QTextCursor_NextBlock = QTextCursor.NextBlock
    QTextCursor_NextCharacter = QTextCursor.NextCharacter
    QTextCursor_NextWord = QTextCursor.NextWord
    QTextCursor_Down = QTextCursor.Down
    QTextCursor_Right = QTextCursor.Right
    QTextCursor_WordRight = QTextCursor.WordRight
    QTextCursor_NextCell = QTextCursor.NextCell
    QTextCursor_PreviousCell = QTextCursor.PreviousCell
    QTextCursor_NextRow = QTextCursor.NextRow
    QTextCursor_PreviousRow = QTextCursor.PreviousRow


    

def logError(e):
    # print("logError: ", e)
    return 

# ========================= CONFIG ============================================
# Loading the add-on configuration
config = mw.addonManager.getConfig(__name__)
meta  = mw.addonManager.addon_meta(__name__)
this_addon_provided_name = meta.provided_name

def configF(par1, par2, default=""):
    """получить данные из конфига"""
    try:
        ret = config[par1][par2]
        return ret
    except Exception as e:        
        logError(e)
        return default     

languageName = configF("GLOBAL_SETTINGS", "language", "en")
current_language = anki.lang.current_lang #en, pr-BR, en-GB, ru и подобное 
if not languageName: # если надо автоопределение       
    languageName = current_language
    if languageName not in config["LOCALIZATION"]:        
        languageName = "en" # Если не поддерживается, откатываемся на английский                
    
try:
    localization = config["LOCALIZATION"][languageName]
except Exception as e:
    text = f"ERROR in add-on '{this_addon_provided_name}'\n"
    text += f"Config[\"GLOBAL_SETTINGS\"][\"language\"] does not contain '{languageName}'"
    text += "\nChange the add-on configuration, \"language\": \"en\""
    languageName = "en"
    config["GLOBAL_SETTINGS"]["language"] = languageName # меняем язык
    mw.addonManager.writeConfig(__name__, config) # записываем конфиг с изменениями  
    showText(text, type="error")

def localizationF(par1, default=""):
    """получить данные из localization = config["LOCALIZATION"][languageName] """
    try:
        ret = localization[par1]
        return ret
    except Exception as e:        
        logError(e)
        return default      



# Добавляем глобальную переменную для отслеживания текущей сортировки
current_sort_flag = 0  # 0 - no, 1 - Sort1, 2 - Sort2
try:
    current_sort_flag = configF("GLOBAL_SETTINGS","sorting_type", 0)
except Exception as e: logError(e)

    
def restart_anki():
    anki_exe = sys.executable
    # Только имя исполняемого файла, без аргументов, иначе Anki подумает что ему передали .apkg
    subprocess.Popen([anki_exe])
    # Закрываем текущую Anki после запуска новой
    QTimer.singleShot(100, mw.close)    
# Добавляем в меню перезапуск
action = QAction(localizationF("Restart_Anki", "🔄 Restart Anki"), mw)
action.setShortcut("Alt+Shift+F4")
action.triggered.connect(restart_anki)
mw.form.menuTools.addAction(action)


active_profile = 1 # активный профиль (загружен  с anki)
current_profile = active_profile # текущий профиль выбранный
profile_list_addons = []
the_profile_will_change = False # если меняют профиль

def create_and_load_profiles():        
    """создание профилей если их нет и загрузка"""
    global active_profile, current_profile, profile_list_addons, the_profile_will_change
    try:
        # Путь к meta.json
        addon_dir = Path(mw.addonManager.addonsFolder()) / __name__
        meta_path = addon_dir / "meta.json"
        original_mtime = None
        # Читаем meta.json
        if meta_path.exists():
            original_mtime = os.path.getmtime(meta_path) # Сохраняем старую дату модификации
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

        we_will_write = False

        # Проверяем и создаём параметры профилей, если их нет
        for i in range(1, 6):
            key = f"profile{i}"
            if key not in meta:
                we_will_write = True
                meta[key] = []

        # Проверяем и создаём active_profile, если его нет
        if "active_profile" not in meta:
            we_will_write = True
            meta["active_profile"] = 1

        # получим активный профиль
        active_profile = meta.get("active_profile", 1)     
        # ограничение на кол. профилей
        if active_profile < 1:
            active_profile = 1
        elif active_profile > 5:
            active_profile = 5
        current_profile = active_profile # текущий профиль выбранный
        # Загружаем список из активного профиля в глобальную переменную        
        profile_key = f"profile{active_profile}"
        profile_list_addons = meta.get(profile_key, [])

        # Записываем обратно в meta.json если чего меняли we_will_write == True
        if we_will_write == True:            
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=4)
            if original_mtime:
                os.utime(meta_path, (original_mtime, original_mtime))  # Восстанавливаем дату модификации

    except Exception as e: logError(e)       
    

# создаем и загружаем профили
create_and_load_profiles()



# =============================================================================   

# Сохраняем оригинальный метод (из anki-main\qt\aqt\addons.py)
original_redraw = AddonsDialog.redrawAddons
current_dialog = None # текущий объект dialog 
CurrentAddon = ["",""] # активная строка, dir_name и provided_name

theme_night = True
def dialog_will_show(dialog):
    """перед показом настроим свое дополнение"""    
    global theme_night
    if theme_manager.night_mode: # определям темная или светлая тема
        theme_night = True
    else:
        theme_night = False

    for child in dialog.findChildren(QLabel):
        # Проверка по положению
        if child.x() < 170  and child.y() < 130:
            original_text = child.text()
            if "[Alt+Shift+F4]" not in original_text:
                child.setText(original_text + " [Alt+Shift+F4]")
            break

    QShortcut(QKeySequence("Alt+Shift+F4"), dialog, lambda: restart_anki())        
            
        
    global current_dialog
    current_dialog = dialog 
    setup_context_menu(current_dialog.form.addonList, current_dialog)
    add_buttons_to_addons_dialog(dialog)
    if CurrentAddon[0] == "":
        QTimer.singleShot(150, lambda:dialog.form.addonList.setCurrentRow(-1))
    else:
        #QTimer.singleShot(300, lambda:setCurrentItem(dialog, CurrentAddon))
        setCurrentItem(dialog, CurrentAddon)

    # global current_profile
    # QTimer.singleShot(300, lambda:save_profile(current_profile))
     
           

def change_selected_addon(dialog, add_on):    
    CurrentAddon[0] = add_on.dir_name
    CurrentAddon[1] = add_on.provided_name


def setCurrentItem(dialog, curAddon):        
    if curAddon[1] != "":            
        if dialog.form.addonList.count() > 0:
            i = 0            
            for addon in dialog.addons:
                if addon.dir_name == curAddon[0]:                    
                    dialog.form.addonList.setCurrentRow(i)
                    item = dialog.form.addonList.item(i)   
                    dialog.form.addonList.scrollToItem(item)  # Прокручиваем к элементу
                    break
                i += 1        

# Подключаемся к хуку addons_dialog_did_change_selected_addon
addons_dialog_did_change_selected_addon.append(change_selected_addon)                
# Подключаемся к хуку addons_dialog_will_show
addons_dialog_will_show.append(dialog_will_show)



# ============================================================================= 
colorsHL = {
    "dark": {
        "number": "#ffaea8",
        "const": "#569cd6",
        "brace": "#cccccc",
        "brace1": "#bb0000",
        "brace2": "#ffff00",
        "brace3": "#fc4e77",
        "brace4": "#179fff",
        "key": "#007acc",
        "key1": "#009aaa",
        "key2": "#999999",
        "string": "#d69d85"
    },
    "light": {
        "number": "#ffaea8",
        "const": "#569cd6",
        "brace": "#000000",
        "brace1": "#bb0000",
        "brace2": "#e80af7",
        "brace3": "#fc4e77",
        "brace4": "#179fff",
        "key": "#007acc",
        "key1": "#009aaa",
        "key2": "#999999",
        "string": "#7d3618"
    }
}



class LineNumberArea(QWidget):    
    def __init__(self, editor):        
        super().__init__(editor)
        self.editor = editor        
  

    def paintEvent(self, event):               
        lnbgcolor = "#363636" if theme_night else "#e5efe5"        
        lntcolor = "#FFFFFF" if theme_night else "#000000" 
        self.setStyleSheet("background-color: "+ lnbgcolor + "; color: "  + lntcolor + ";") 
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(lnbgcolor))       

        document = self.editor.document()
        font_metrics = self.editor.fontMetrics()
        line_height = font_metrics.height()

        scroll_value = self.editor.verticalScrollBar().value()
        page_bottom = scroll_value + self.editor.viewport().height()

        cursor = self.editor.cursorForPosition(QPoint(0, 0))
        first_visible_block = cursor.block()
        first_visible_block_number = first_visible_block.blockNumber()
        rect = self.editor.cursorRect(cursor)
        top = rect.top()

        block = first_visible_block
        block_number = first_visible_block_number

        # Получаем номер текущей строки
        current_block_number = self.editor.textCursor().blockNumber()
               

        while block.isValid() and top <= page_bottom:
            if block.isVisible():                
                number = str(block_number + 1)
                # Цвет для текущей строки
                if block_number == current_block_number:
                    color = QColor("#ffd700") if theme_night else QColor("#af00db")
                    painter.setPen( color )  # цвет текущей строки 
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:                    
                    color = QColor("##FFFFFF") if theme_night else QColor("#000000")
                    painter.setPen( color )
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
                painter.drawText(
                    0, int(top), self.width() - 5, line_height,
                    Qt.AlignmentFlag.AlignRight if pyqt_version == "PyQt6" else Qt.AlignRight, number
                )

                if block_number == current_block_number:
                    # Горизонтальная линия сверху
                    color = QColor("#ffd700") if theme_night else QColor("#af00db")
                    pen = QPen(color)
                    pen.setWidthF(0.5)
                    painter.setPen(pen)
                    painter.drawLine(0, int(top), self.width(), int(top))
                   

            block = block.next()
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            rect = self.editor.cursorRect(cursor)
            top = rect.top()
            block_number += 1

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)




def merge_configs_with_duplicates(config_path, meta_path):
    """Слить конфиги с показом пользовательских изменений (дубли ключей рядом, красивая строка, русские символы)."""
    import json

    defCFG = json.load(open(config_path, "r", encoding="utf-8"))
    
    # Сохраняем копию meta.json в meta_backup.json
    meta_dir, meta_filename = os.path.split(meta_path)
    meta_base, _ = os.path.splitext(meta_filename)
    metaTMP_path = os.path.join(meta_dir, meta_base + "_backup.json")
    shutil.copyfile(meta_path, metaTMP_path)

    meta = json.load(open(meta_path, "r", encoding="utf-8"))
    metaCFG = meta.get("config", {})

    def format_value(val, indent=2):
        # Форматирует значение с нужным отступом и ensure_ascii=False
        return json.dumps(val, ensure_ascii=False, indent=None, separators=(",", ": "))

    def merge_dict(def_dict, meta_dict, level=1):
        lines = []
        indent = "    " * level
        for key in def_dict:
            def_val = def_dict[key]
            if meta_dict: 
                meta_val = meta_dict.get(key, None)
            else:
                meta_val = def_val
            key_str = json.dumps(key, ensure_ascii=False)
            # Если оба значения - dict, рекурсивно
            if isinstance(def_val, dict) and isinstance(meta_val, dict):
                merged = merge_dict(def_val, meta_val, level+1)
                lines.append(f'{indent}{key_str}: {merged},')
            # Если отличаются и meta_val существует
            elif meta_val is not None and meta_val != def_val:
                # Сначала пользовательское
                lines.append(f'{indent}{key_str}: {format_value(meta_val)},')
                # Потом дефолтное
                lines.append(f'{indent}{key_str}: {format_value(def_val)},')
            else:
                lines.append(f'{indent}{key_str}: {format_value(def_val)},')
        # Убираем последнюю запятую
        if lines and lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]
        return '{' + '\r\n' + '\r\n'.join(lines) + '\r\n' + ("    " * (level-1)) + '}'

    
    result = merge_dict(defCFG, metaCFG)
    return result



class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, document, editor=None):
        super().__init__(document)
        self.editor = editor
        self.selected_text = ""
        self.rules = []

        theme = "dark" if theme_night else "light"
        
        # Числа
        number_format = self.format(QColor(colorsHL[theme]["number"]))
        self.rules.append((QRegularExpression(r'(?<=[^#])\b(\d+(\.\d+)?)\b'), number_format))

        # Булевы и null
        const_format = self.format(QColor(colorsHL[theme]["const"]), italic=True)
        self.rules.append((QRegularExpression(r'\b(true|false|null)\b'), const_format))

        # Скобки и запятые
        brace_format = self.format(QColor(colorsHL[theme]["brace"]))
        for symbol in r'()\,.:':
            self.rules.append((QRegularExpression(rf'(\{symbol})'), brace_format))

        brace1_format = self.format(QColor(colorsHL[theme]["brace1"]))
        for symbol in r'.;':
            self.rules.append((QRegularExpression(rf'(\{symbol})'), brace1_format))

        brace2_format = self.format(QColor(colorsHL[theme]["brace2"]), bold=True)    
        for symbol in r'{}':
            self.rules.append((QRegularExpression(rf'(\{symbol})'), brace2_format))
        brace3_format = self.format(QColor(colorsHL[theme]["brace3"]), bold=True)    
        for symbol in r'[]':
            self.rules.append((QRegularExpression(rf'(\{symbol})'), brace3_format))
        brace4_format = self.format(QColor(colorsHL[theme]["brace4"]), bold=True)    
        for symbol in r'()':
            self.rules.append((QRegularExpression(rf'(\{symbol})'), brace4_format))

        # Строки: "значение"
        string_format = self.format(QColor(colorsHL[theme]["string"]))
        self.rules.append((QRegularExpression(r'("([^"\\]|\\.)*")'), string_format))

        # Ключи: "ключ"
        key_format = self.format(QColor(colorsHL[theme]["key"]), bold=True)
        self.rules.append((QRegularExpression(r'("([^"\\]|\\.)*")\s*:'), key_format))      

        # Ключи: {
        key1_format = self.format(QColor(colorsHL[theme]["key1"]), bold=True)
        self.rules.append((QRegularExpression(r'("([^"\\]|\\.)*")\s*:\s*\{'), key1_format))       

        # Ключи ?: "ключ"
        key2_format = self.format(QColor(colorsHL[theme]["key2"]))
        self.rules.append((QRegularExpression(r'("([^"\\]|\\.)* \?"\s*:)'), key2_format))  
        self.rules.append((QRegularExpression(r'( \?"\s*:\s*"([^"\\]|\\.)*")'), key2_format))  

        

    def line_number_area_width(self, edit_area):
        digits = len(str(max(1, edit_area.document().blockCount())))
        space = 3 + edit_area.fontMetrics().horizontalAdvance('9') * digits
        return space + 10

    def update_line_number_area_width(self, edit_area):
        edit_area.setViewportMargins(edit_area.line_number_area_width(), 0, 0, 0)        
        edit_area.line_number_area.update()

    def eventFilter(self, obj, event):        
        if event.type() == QEvent_Resize:
            cr = obj.contentsRect()
            obj.line_number_area.setGeometry(
                QRect(cr.left(), cr.top(), obj.line_number_area_width(), cr.height())
            )
            obj.line_number_area.update()
        elif event.type() == QEvent_WindowActivate: 
            cr = obj.contentsRect()
            obj.line_number_area.setGeometry(
                QRect(cr.left(), cr.top(), obj.line_number_area_width(), cr.height())
            )
            obj.line_number_area.update()            
            QTimer.singleShot(0, lambda: self.update_line_number_area_width(obj))
        return False  # обязательно возвращайте False, чтобы событие не блокировалось
    
    def enhance_text_edit(self, edit_area):                  
        edit_area.setStyleSheet("""
                font-family: Consolas;
                font-size: 10pt;
                selection-background-color: #264f78;
                selection-color: #ffffff00;
        """)                               
        edit_area.line_number_area = LineNumberArea(edit_area)                
        edit_area.line_number_area_width = lambda: self.line_number_area_width(edit_area)              
        edit_area.textChanged.connect(lambda: self.update_line_number_area_width(edit_area))
        edit_area.verticalScrollBar().valueChanged.connect(lambda: edit_area.line_number_area.update())                        
        # self.update_line_number_area_width(edit_area)            
        edit_area.installEventFilter(self)
        edit_area.line_number_area.show()  
        edit_area.line_number_area.raise_()
        # Отложенное обновление после показа
        QTimer.singleShot(0, lambda: self.update_line_number_area_width(edit_area))



    def setSelectedText(self, text):
            self.selected_text = text    
        
    def format(self, color_hex, bold=False, italic=False, color_back=None):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))
        if not color_back == None:
            fmt.setBackground(QColor(color_back))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def highlightBlock(self, text):                  

        for pattern, fmt in self.rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                if match.lastCapturedIndex() >= 1:
                    # Есть захваченная группа (например, строка)
                    start = match.capturedStart(1)
                    length = match.capturedLength(1)
                    self.setFormat(start, length, fmt)

        # Подсветка строк с цветами
        color_regex = QRegularExpression(r'"([#a-zA-Z0-9]{3,20})"')
        color_iter = color_regex.globalMatch(text)
        while color_iter.hasNext():
            match = color_iter.next()
            color_code = match.captured(1)
            qcolor = QColor(color_code)

            if not qcolor.isValid():
                continue

            fmt = QTextCharFormat()
            fmt.setBackground(qcolor)

            # Автоматически выбираем белый/чёрный текст по яркости
            if qcolor.lightness() < 128:
                fmt.setForeground(Qt.GlobalColor.white)
            else:
                fmt.setForeground(Qt.GlobalColor.black)

            # Подсветка только содержимого (без кавычек)
            self.setFormat(match.capturedStart(1), match.capturedLength(1), fmt)

        # Подсветка выделенного текста
        if self.selected_text and len(self.selected_text) >= 1 and len(self.selected_text) < 1024:
            fmt = QTextCharFormat()
            if theme_night:
                fmt.setBackground(QColor("#5e5e30"))
                fmt.setForeground(QColor("black"))
            else:
                fmt.setBackground(QColor("#cfcf6d"))
                fmt.setForeground(QColor("black"))

            pattern = QRegularExpression(re.escape(self.selected_text))
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)
            # особо для парных
            if len(self.selected_text) == 1:
                strp1 = "{[(<}])>"
                strp2 = "}])>{[(<"
                findp = strp1.find(self.selected_text)
                if findp >= 0:              
                    fmt = QTextCharFormat()
                    if theme_night:
                        fmt.setBackground(QColor("#cfcf6d"))
                        fmt.setForeground(QColor("#e80af7"))
                    else:
                        fmt.setBackground(QColor("#cfcf6d"))
                        fmt.setForeground(QColor("#e80af7"))

                    pattern = QRegularExpression(re.escape( strp2[findp] ))
                    match_iter = pattern.globalMatch(text)
                    while match_iter.hasNext():
                        match = match_iter.next()
                        start = match.capturedStart()
                        length = match.capturedLength()
                        self.setFormat(start, length, fmt)


        # Регулярка для поиска ключа "A" (или любого ключа)
        key_regex = QRegularExpression(r'^\s*"([^"]+)"\s*:')
        match = key_regex.match(text)
        key = match.captured(1) if match.hasMatch() else None        

        # Получаем ключ из предыдущего блока (если был)
        prev_key = self.previousBlockState()       

        # Сохраняем текущий ключ в state (можно через hash или id)
        if key:
            cur_key = hash(key) & 0x0FFFFFFF # Ограничиваем значение state до 32 бит
            if prev_key != 0 and cur_key == prev_key:                
                start = match.capturedStart(1)
                length = match.capturedLength(1)
                fmt = QTextCharFormat()
                fmt.setBackground(QColor("#ff5555"))
                self.setFormat(start, length, fmt)             
            self.setCurrentBlockState( cur_key )
        else:
            self.setCurrentBlockState( 0 )        
    


def patch_config_editor(dialog: QDialog):
    """изменения для редактора конфига """
    try:        
        highlighter = JsonHighlighter(dialog.form.editor.document(), editor=dialog.form.editor)
        dialog.form.editor.highlighter = highlighter
        highlighter.enhance_text_edit(dialog.form.editor)

        # # Установить шрифт
        # font = QFont("Consolas", 8)
        # dialog.form.editor.setFont(font)
        # dialog.form.editor.setStyleSheet("""
        #     QTextEdit {
        #         font-family: Consolas;
        #         font-size: 9pt;
        #     }
        # """)
       
        # font-family: Consolas;
        # dialog.form.editor.setStyleSheet(""" 
        #     QTextEdit {                
        #         font-family: Consolas;
        #         font-size: 9pt;
        #         background-color: #1f1f1f;
        #         color: d4d4d4;
        #         selection-background-color: #264f78;
        #         selection-color: #ffffff00;
        #     }
        # """)

        # табуляция 4 символа
        dialog.form.editor.setTabStopDistance(dialog.form.editor.fontMetrics().horizontalAdvance('0000')) 

        # Подключаем сигнал изменения курсора
        def on_cursor_changed():
            text = dialog.form.editor.textCursor().selectedText()
            highlighter.setSelectedText(text)
            highlighter.rehighlight()
        dialog.form.editor.cursorPositionChanged.connect(on_cursor_changed)
        
        setup_context_menu_json(dialog.form.editor, dialog) # создаем контекстное меню

        # Создаём кнопки поиска
        dialog.btn_find_prev = QPushButton(" ← ")
        msg = localizationF("Search_previous_repl", "Search for previous replacement")
        dialog.btn_find_prev.setToolTip( msg )
        dialog.btn_find_prev.setDefault(False)
        dialog.btn_find_next = QPushButton(" → ")
        msg = localizationF("Search_next_repl", "Searching for the next replacement")
        dialog.btn_find_next.setToolTip( msg )
        dialog.btn_find_next.setDefault(False)
        # поиск индекса кнопки по умолчанию
        restore = dialog.form.buttonBox.button(QDialogButtonBox.StandardButton.RestoreDefaults)
        layout = dialog.form.buttonBox.layout()
        restore_index = None
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is restore:
                restore_index = i
                break
        # Добавляем их после 
        layout.insertWidget(restore_index + 1, dialog.btn_find_prev)
        layout.insertWidget(restore_index + 2, dialog.btn_find_next)

        status_label = QLabel()
        dialog.status_label = status_label
        status_label.setStyleSheet("font-size: 10pt; color: #777; padding: 2px;")
        layout.insertWidget(restore_index + 3, dialog.status_label)
        msg = localizationF("status_label", "Total replacements")
        status = f"{msg}" +": 0"        
        dialog.status_label.setText(status)
        msg = localizationF("status_label_ToolTip", "The last line will be saved")
        dialog.status_label.setToolTip( msg )

        # По умолчанию скрываем
        dialog.btn_find_prev.setVisible(False)
        dialog.btn_find_next.setVisible(False)
        dialog.status_label.setVisible(False)

        def get_key_from_line(line):
            if ':' not in line:
                return None
            return line.split(':', 1)[0].strip().strip('"')
        

        def on_find_next_prev(direction = QTextCursor_NextBlock):
            """поиск вперед или назад дублирующих или которые заменены будут"""
            editor = dialog.form.editor
            text = editor.toPlainText()

            # Текущая строка
            cursor = editor.textCursor()            
            curBN = cursor.block().blockNumber()
            cursor.movePosition(QTextCursor_StartOfBlock)
            cur_start = cursor.position()
            cursor.movePosition(QTextCursor_EndOfBlock)
            cur_end = cursor.position()

            cursor.setPosition( cur_start )
            cursor.setPosition( cur_end, QTextCursor_KeepAnchor )          

            cur_line = cursor.selectedText() 
            str_last = get_key_from_line(cur_line) 

            MaxN = 100000
            while True:
                # Перейти к следующей строке в начало              
                if not cursor.movePosition( direction ):
                    notfound = localizationF("notfound", "Not found")
                    tooltip(f"<p style='color: yellow; background-color: black'>{notfound}</p>", parent=dialog)                    
                    return
                next_start = cursor.position() 
                cursor.movePosition(QTextCursor_EndOfBlock)
                next_end = cursor.position()
                cursor.setPosition( next_start )
                cursor.setPosition( next_end, QTextCursor_KeepAnchor )          
                next_line = cursor.selectedText() 
                str_next = get_key_from_line(next_line) 

                nexBN = cursor.block().blockNumber()
                
                if str_next and str_last and str_next == str_last and abs(curBN-nexBN) > 1:
                    # Ставим курсор после двоеточия
                    colon_pos = next_line.find(':')
                    if colon_pos != -1:
                        abs_pos = next_start + colon_pos + 1
                        tc = editor.textCursor()
                        tc.setPosition(abs_pos)
                        editor.setTextCursor(tc)
                        editor.centerCursor()
                        return
                else:
                    # продолжим поиск
                    cur_start = next_start
                    cur_end = next_end 
                    cur_line = next_line
                    str_last = str_next

                MaxN -= 1
                if MaxN <= 0:
                    return
                

        # Подключаем обработчики        
        dialog.btn_find_prev.clicked.connect(lambda: on_find_next_prev(QTextCursor_PreviousBlock))
        dialog.btn_find_next.clicked.connect(lambda: on_find_next_prev(QTextCursor_NextBlock))        


        def custom_onRestoreDefaults(self):
            # default_conf = self.mgr.addonConfigDefaults(self.addon)       
            addon_dir = Path(mw.addonManager.addonsFolder()) / current_dialog.mgr.addonsFolder(self.addon)
            config_path = addon_dir / "config.json"
            meta_path = addon_dir / "meta.json"
            newCFG = merge_configs_with_duplicates(config_path, meta_path)            
            text = gui_hooks.addon_config_editor_will_display_json( newCFG )
            self.form.editor.setPlainText(text)
            if is_mac:
                self.form.editor.repaint()
            # повторная подсветка
            self.form.editor.highlighter.rehighlight()    
            
            n = 0
            text = self.form.editor.toPlainText()
            pattern = r'"([^"]+)"\s*:'
            matches = list(re.finditer(pattern, text))
            # Поиск дублей подряд
            for i in range(1, len(matches)):
                if matches[i].group(1) == matches[i-1].group(1):
                    n += 1
            if n > 0:
                self.btn_find_prev.setVisible(True)
                self.btn_find_next.setVisible(True)
                self.status_label.setVisible(True)
                msg = localizationF("status_label", "Total replacements")
                status = f"{msg}: {n}"
                self.status_label.setText(status)
            else:
                self.btn_find_prev.setVisible(False)
                self.btn_find_next.setVisible(False)
                self.status_label.setVisible(False)    
            cursor =  self.form.editor.textCursor()
            cursor.setPosition(0)
            self.form.editor.setTextCursor(cursor)

            tooltip(tr.addons_restored_defaults(), parent=self)

        # изменим загрузку по умолчанию конфига
        restore = dialog.form.buttonBox.button(
            QDialogButtonBox.StandardButton.RestoreDefaults
        )        
        # Привязываем кастомный метод к экземпляру dialog
        dialog.onRestoreDefaults = MethodType(custom_onRestoreDefaults, dialog)  
        # Переподключаем сигнал
        restore.clicked.disconnect()                     
        qconnect(restore.clicked, dialog.onRestoreDefaults)
             
     

    except Exception as e:
        print(f"[json_highlighter] Error: {e}") 


def intercept_on_config(dialog: AddonsDialog):  
    """Перехват конфигурации"""  
    original_on_config = dialog.onConfig

    def custom_on_config():        
        addon = dialog.onlyOneSelected()
        if not addon:
            return

        act = dialog.mgr.configAction(addon)
        if act and act() is not False:
            return

        conf = dialog.mgr.getConfig(addon)
        if conf is None:
            showInfo(tr.addons_addon_has_no_configuration())
            return

        editor = aqt.addons.ConfigEditor(dialog, addon, conf)
        patch_config_editor(editor)
       

    dialog.onConfig = custom_on_config

    # Переподключаем кнопки и двойной клик
    try:
        dialog.form.config.clicked.disconnect()
    except Exception:
        pass
    dialog.form.config.clicked.connect(custom_on_config)

    try:
        dialog.form.addonList.itemDoubleClicked.disconnect()
    except Exception:
        pass
    dialog.form.addonList.itemDoubleClicked.connect(custom_on_config)





addons_dialog_will_show.append(intercept_on_config)



findStrJson = "" # подстрока которую будем искать
def findF3Json(editor, dialog):    
    """Для JSON поиск вперед подстроки ранее запомненной"""
    global findStrJson
    if not findStrJson:
        return
    
    cursor = editor.textCursor()
    document = editor.document()
    # Начинаем поиск с позиции конца
    found_cursor = document.find(findStrJson,  cursor.selectionEnd() )

    if found_cursor.isNull():
        # Повторный поиск с начала
        notfound = localizationF("notfound", "Not found")
        tooltip(f"<p style='color: yellow; background-color: black'>{notfound}. ⏮️</p>", parent=dialog)
        found_cursor = document.find(findStrJson, 0)

    if not found_cursor.isNull():
        editor.setTextCursor(found_cursor)
        editor.centerCursor()
    else:
        notfound = localizationF("notfound", "Not found")
        tooltip(f"<p style='color: yellow; background-color: black'>{notfound}</p>", parent=dialog)


def findShiftF3Json(editor, dialog):    
    """Для JSON поиск назад подстроки ранее запомненной"""
    global findStrJson
    if not findStrJson:
        return
        
    
    cursor = editor.textCursor()
    document = editor.document()
    start_pos = cursor.selectionStart()

    # Если есть выделение — снимаем его и ставим курсор в начало выделения
    if cursor.hasSelection():        
        cursor.setPosition(start_pos)
        editor.setTextCursor(cursor)        

    found_cursor = document.find(findStrJson, start_pos, QTextDocument_FindBackward)

    if not found_cursor.isNull():        
        editor.setTextCursor(found_cursor)
    else:       
        # Если не найдено, можно начать поиск с конца документа
        notfound = localizationF("notfound", "Not found")
        tooltip(f"<p style='color: yellow; background-color: black'>{notfound}. ⏭️</p>", parent=dialog)
        found_cursor = document.find(findStrJson, document.characterCount() - 1, QTextDocument_FindBackward)

        if not found_cursor.isNull():
            editor.setTextCursor(found_cursor)
        else:
            tooltip(f"<p style='color: yellow; background-color: black'>{notfound}</p>", parent=dialog)

    


def findJson(editor, dialog):  
    """Для JSON поиск подстроки и запомним подстроку в findStrJson"""     
    global findStrJson
    find = localizationF("Find", "Find a substring")
    find_t = localizationF("Find_tooltip", "Enter a substring")
    user_find = ask_user_for_text(dialog, find, find_t, findStrJson) # ввод от пользователя строки 
    if user_find is None or not user_find.strip():
        return
    findStrJson = user_find
    findF3Json(editor, dialog)   



# формируем контекстное меню для редактора JSON
def setup_context_menu_json(editor, dialog):
    """Настраивает контекстное меню для конфигурации дополнения."""
    def show_context_menu_json(position):
        # Получаем стандартное меню
        menu = editor.createStandardContextMenu()

        # Добавляем разделительную линию
        menu.addSeparator()   

        # Добавляем пункт меню для поиска 
        find_action = QAction(localizationF("Find","Find a substring")+"...", menu)
        find_action.setToolTip(localizationF("Find_tooltip","Enter a substring"))
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(lambda: findJson(editor, dialog))
        menu.addAction(find_action)
        dialog.addAction(find_action)

        # Добавляем пункт меню для поиска F3 
        findF3_action = QAction(localizationF("FindF3","Search next"), menu)
        findF3_action.setToolTip(localizationF("FindF3_tooltip","Repeat search for substring"))
        findF3_action.setShortcut("F3")
        findF3_action.triggered.connect(lambda: findF3Json(editor, dialog))
        menu.addAction(findF3_action)
        dialog.addAction(findF3_action)

        # Добавляем пункт меню для поиска Shift+F3 
        findShiftF3_action = QAction(localizationF("FindShiftF3","🔍⬆️ Search Previous"), menu)        
        findShiftF3_action.setShortcut("Shift+F3")
        findShiftF3_action.triggered.connect(lambda: findShiftF3Json(editor, dialog))
        menu.addAction(findShiftF3_action)
        dialog.addAction(findShiftF3_action)

        # Показываем меню в позиции курсора
        menu.exec(editor.viewport().mapToGlobal(position))

    
    # Устанавливаем политику контекстного меню
    editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    editor.customContextMenuRequested.connect(show_context_menu_json)
    QShortcut(QKeySequence("Ctrl+F"), editor, lambda: findJson(editor, dialog))
    QShortcut(QKeySequence("F3"), editor, lambda: findF3Json(editor, dialog))
    QShortcut(QKeySequence("Shift+F3"), editor, lambda: findShiftF3Json(editor, dialog))    
    

# ============================================================================= 




class ColorfulDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        text = index.data(Qt.ItemDataRole.DisplayRole)
        text_color_brush = index.data(Qt.ItemDataRole.ForegroundRole)

        if theme_night: # темная тема
            # Проверка на None, если цвет не задан, используем цвет по умолчанию
            if text_color_brush is None:
                text_color = QColor("#f5f9fc")
            else:
                text_color = text_color_brush.color()  # Извлекаем цвет из QBrush
            
            # Если выделена строка, делаем фон свой
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, QColor("#323e4d"))
            else:
                painter.fillRect(option.rect, QColor("#252525"))  # основной фон
        else:
            # Проверка на None, если цвет не задан, используем цвет по умолчанию
            if text_color_brush is None:
                text_color = QColor("#020202")
            else:
                text_color = text_color_brush.color()  # Извлекаем цвет из QBrush

            # Если выделена строка, делаем фон свой
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, QColor("#dae5ff"))
            else:
                painter.fillRect(option.rect, QColor("#ffffff"))  # основной фон
             
        # Устанавливаем цвет текста
        painter.setPen(text_color)
        painter.drawText(option.rect.adjusted(5, 0, -5, 0), Qt.AlignmentFlag.AlignVCenter, text)

    def sizeHint(self, option, index): # Автоматически подстроит под стандартную высоту      
        # Получаем метрики шрифта для текущего элемента
        if pyqt_version == "PyQt6":
            # Для PyQt6 используем свойство fontMetrics
            font_metrics = option.fontMetrics
            # Получаем высоту текста для текущего элемента
            row_height = font_metrics.boundingRect(index.data(Qt.ItemDataRole.DisplayRole)).height()
        else:
            # Для PyQt5 также используем свойство fontMetrics
            font_metrics = option.fontMetrics
            row_height = font_metrics.boundingRect(index.data(Qt.DisplayRole)).height()  
        # Возвращаем QSize с шириной и рассчитанной высотой
        return QSize(option.rect.width(), row_height + 0)  # Можно добавить небольшой отступ, например, 10 пикселей
    

def safe_split_N(s: str, sep: str, n: int, first_missed: bool = False) -> list[str]:
    """разбить строку s по разделителю sep строго на n подстрок (first_missed пропущенные в начало)"""
    if not sep or n < 1:
        return [""] * n
    parts = s.split(sep, n - 1)
    len__parts = len(parts) 
    if len__parts < n:
        if first_missed:
            return ([""] * (n-len__parts) + parts)
        else:
            return (parts + [""] * (n-len__parts))            
    else:
        return parts 

    
    



def custom_redrawAddons(self):  
    """Специальная версия AddonsDialog.redrawAddons (из anki-main\qt\aqt\addons.py) """

    CurrentAddonPrev = CurrentAddon.copy() # сохраним какая активная    

    selected = set(self.selectedAddons())

    original_redraw(self) # надо вызвать оригинал, вдруг там какой-то код поменяли в новой версии
    
    addonList = self.form.addonList
    mgr = self.mgr
    self.addons = list(mgr.all_addon_meta())   

    # Обработка meta.json для каждого аддона
    for addon in self.addons:
        meta_path = os.path.join(mgr.addonsFolder(), addon.dir_name, "meta.json")
        manifest_path = os.path.join(mgr.addonsFolder(), addon.dir_name, "manifest.json")

        if not hasattr(addon, "provided_name") or addon.provided_name is None:
            addon.provided_name = "" # создаем, если такого атрибута почему-то нет

        user_hint = ""
        mark_color = "#000000"
        mod_timestamp_upd = 0
        auto_update = True
        version = ""

        addon_manager = mw.addonManager
        addons_list = self.form.addonList

        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta_data = json.load(f)

                # Получение или добавление поля "hint"
                user_hint = meta_data.get("hint", "")
                if "hint" not in meta_data:
                    meta_data["hint"] = user_hint

                # Получение или добавление поля "mark_color"
                mark_color = meta_data.get("mark_color", "#000000")
                if "mark_color" not in meta_data:
                    meta_data["mark_color"] = mark_color

                # 👉 Сохраняем старую дату модификации
                original_mtime = os.path.getmtime(meta_path)

                # ✍️ Сохраняем изменения в meta.json
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta_data, f, ensure_ascii=False, indent=4)

                # 🔄 Восстанавливаем дату модификации
                os.utime(meta_path, (original_mtime, original_mtime))  # (atime, mtime)

                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)
                    mod_timestamp_upd = manifest_data.get("mod", 0)

            except Exception as e:
                showText(f"Error while processing {meta_path}:\n{traceback.format_exc()}")
        else:
            showText(f"Meta.json file not found for addon {addon.dir_name}")

        # Формируем данные для нового отображения  
        min_point_version = str(meta_data.get("min_point_version", "-"))
        max_point_version = str(meta_data.get("max_point_version", "-"))
        version = meta_data.get("human_version", "")  
        if version.strip() != "":
            version += " "        
        version += f" anki [{min_point_version}...{max_point_version}]"
        auto_update = meta_data.get("update_enabled", True) 
        mod_timestamp = meta_data.get("mod", 0)
        creation_time = datetime.fromtimestamp(mod_timestamp).strftime('%Y-%m-%d %H:%M') if meta_data.get("mod") else "Unknown"
        creation_time_YYYY_MM = datetime.fromtimestamp(mod_timestamp).strftime('%Y-%m') if mod_timestamp else "Unknown"
        update_time = ""
        if mod_timestamp_upd > 0:
            update_time = datetime.fromtimestamp(mod_timestamp_upd).strftime('%Y-%m-%d %H:%M')
        modification_time = datetime.fromtimestamp(os.path.getmtime(meta_path)).strftime('%Y-%m-%d %H:%M')
        loc_cr = localizationF("Created", "Created")
        loc_md = localizationF("Modified", "Modified")
        date_info = f" {addon.human_name()} "
        if user_hint != "":
            date_info += "\n / " + user_hint + " / "
        loc_ver = localizationF("Version", "Version")        
        date_info += f"\n {loc_ver}: {version} "
        if mod_timestamp_upd > 0:
             loc_upd = localizationF("Updated", "Updated")
             date_info += f"\n {update_time} - {loc_upd} "
        date_info += f"\n {creation_time} - {loc_cr} "
        date_info += f"\n {modification_time} - {loc_md} "         
        loc_enupd = localizationF("Auto_update", "Auto update") 
        loc_true = localizationF("Yes", "Yes")
        loc_false = localizationF("No", "No")
        strNoUpd = ""
        if auto_update:            
            date_info += f"\n {loc_enupd}: {loc_true}"            
        else:
            date_info += f"\n {loc_enupd}: {loc_false}"
            strNoUpd = localizationF("update_enabled_False", " (!auto) ")
        date_info += f"\n id: {addon.dir_name} "

        # если первым символов идет # значит это до имени и следующее # - после
        if len(user_hint) > 0 and user_hint[0] == "#":
            user_hintS = safe_split_N(user_hint, "#", 3)
            user_hint1 = user_hintS[1]
            user_hint2 = user_hintS[2]            
            if user_hint1.strip() != "":
                user_hint1 += " "  
            if user_hint2.strip() != "":
                user_hint2 = " " + user_hint2 
            # Формируем новое имя в зависимости от типа сортировки
            if current_sort_flag == 0:                
                addon.provided_name = user_hint1 + addon.provided_name + user_hint2 + strNoUpd
            elif current_sort_flag == 1:
                addon.provided_name = f"{creation_time_YYYY_MM}   {modification_time}     {user_hint1}{addon.human_name()}{user_hint2}   {addon.dir_name}{strNoUpd}"                    
            elif current_sort_flag == 2:
                addon.provided_name = f"{modification_time}   {creation_time_YYYY_MM}     {user_hint1}{addon.human_name()}{user_hint2}   {addon.dir_name}{strNoUpd}"                
        else:
            # Формируем новое имя в зависимости от типа сортировки
            if current_sort_flag == 0:
                addon.provided_name += strNoUpd                        
            elif current_sort_flag == 1:
                addon.provided_name = f"{creation_time_YYYY_MM}   {modification_time}     {addon.human_name()}{strNoUpd}   {addon.dir_name}{strNoUpd}"
            elif current_sort_flag == 2:
                addon.provided_name = f"{modification_time}   {creation_time_YYYY_MM}     {addon.human_name()}{strNoUpd}   {addon.dir_name}{strNoUpd}"
                
            if user_hint != "":
                    addon.provided_name += "   / " + user_hint + " /" + strNoUpd 

              
        addon.date_info = date_info
        addon.user_hint = user_hint
        addon.mark_color = mark_color  

    # это модифицированный код def redrawAddons из addons.py 
    reverseSort = not current_sort_flag == 0
    self.addons.sort(key=lambda a: a.human_name().lower(), reverse=reverseSort)
    self.addons.sort(key=self.should_grey)    
        
    addonList.clear()
        
    # Назначаем кастомный делегат
    delegate = ColorfulDelegate(addonList)
    addonList.setItemDelegate(delegate)

    i = 0
    for addon in self.addons:
        name = self.name_for_addon_list(addon)
        item = QListWidgetItem(name, addonList)
        if not hasattr(addon, "date_info") or addon.date_info is None:
            addon.date_info = "" # создаем, если такого атрибута почему-то нет
        item.setToolTip(addon.date_info)  # Устанавливаем всплывающую подсказку                   
        
        if not hasattr(addon, "mark_color") or addon.mark_color is None:
            addon.mark_color = "#000000" # создаем, если такого атрибута почему-то нет

        if addon.mark_color not in ("#000000", "#ffffff", "#FFFFFF", ""): # раскрашиваем если не белый и не черный                    
            item.setForeground(QColor(addon.mark_color))
        else:
            if self.should_grey(addon):
                item.setForeground(Qt.GlobalColor.gray) 
                       

        if addon.dir_name in selected:            
            item.setSelected(True) 
    

    #addonList.reset() # раскомментировать если надо будет сбрасывать выделение

    #QTimer.singleShot(100, lambda:setCurrentItem(self, CurrentAddonPrev)) 
     
         

# Подменяем метод redrawAddons
AddonsDialog.redrawAddons = custom_redrawAddons



def custom_onGetAddons(self):
    """Специальная версия AddonsDialog.onGetAddons (из anki-main\qt\aqt\addons.py) """
    obj = GetAddons(self)
    if obj.ids:
        findOldAddons = False
        for addon in self.addons:
            if addon.dir_name.isdigit() and int(addon.dir_name) in obj.ids:
                findOldAddons = True
                break
        
        if findOldAddons:
            if askUser(localizationF("download_addons","Attention! There is already one of the add-ons in the list. Should we replace it?")):
                download_addons(self, self.mgr, obj.ids, self.after_downloading, force_enable=True)
        else:
            download_addons(self, self.mgr, obj.ids, self.after_downloading, force_enable=True)


# Подменяем метод onGetAddons
AddonsDialog.onGetAddons = custom_onGetAddons


# формируем меню
def setup_context_menu(addons_list, dialog):
    """Настраивает контекстное меню для списка дополнений."""
    def show_context_menu(position):
        # Показываем меню в позиции курсора
        menu.exec(addons_list.viewport().mapToGlobal(position))


    # Создаем контекстное меню
    menu = QMenu(addons_list)        

    # Добавляем пункт для ввода подсказки
    hint_action = QAction(localizationF("Hint","Hint")+"...", menu)
    hint_action.setToolTip(localizationF("Hint_tooltip", "Enter brief information that is understandable to you"))
    hint_action.setShortcut("F2")
    hint_action.triggered.connect(lambda: hint_item_list(addons_list, dialog))
    menu.addAction(hint_action)
    dialog.addAction(hint_action)

    # Добавляем пункт меню для поиска 
    find_action = QAction(localizationF("Find","Find a substring")+"...", menu)
    find_action.setToolTip(localizationF("Find_tooltip","Enter a substring"))
    find_action.setShortcut("Ctrl+F")
    find_action.triggered.connect(lambda: find(addons_list, dialog))
    menu.addAction(find_action)
    dialog.addAction(find_action)

    # Добавляем пункт меню для поиска F3 
    findF3_action = QAction(localizationF("FindF3","Search next"), menu)
    findF3_action.setToolTip(localizationF("FindF3_tooltip","Repeat search for substring"))
    findF3_action.setShortcut("F3")
    findF3_action.triggered.connect(lambda: findF3(addons_list, dialog))
    menu.addAction(findF3_action)
    dialog.addAction(findF3_action)


    # Добавляем пункт для пометки цветом
    mark_color_action = QAction(localizationF("Mark","🎨 Mark")+"...", menu)
    mark_color_action.setToolTip(localizationF("Mark_tooltip","Mark with color"))
    mark_color_action.setShortcut("F4")
    mark_color_action.triggered.connect(lambda: mark_item_list(addons_list, dialog))
    menu.addAction(mark_color_action)
    dialog.addAction(mark_color_action)    

    # Добавляем пункты для сортировки
    sort1_action = QAction(localizationF("Sort1","🔽 Sort (created)"), menu)
    sort1_action.setToolTip(localizationF("Sort1_tooltip","Click to sort the list of add-ons by creation date (descending)"))
    sort1_action.setShortcut("F5")
    sort1_action.triggered.connect(lambda: sort1(addons_list, dialog))
    menu.addAction(sort1_action)
    dialog.addAction(sort1_action)

    sort2_action = QAction(localizationF("Sort2","🔽 Sort (modified)"), menu)
    sort2_action.setToolTip(localizationF("Sort2_tooltip","Click to sort the list of add-ons by date modified (descending)"))
    sort2_action.setShortcut("F6")
    sort2_action.triggered.connect(lambda: sort2(addons_list, dialog))
    menu.addAction(sort2_action)  
    dialog.addAction(sort2_action)  

    # добавляем пункт как у кнопки toggleEnabled
    toggleEnabled_action = QAction(dialog.form.toggleEnabled.text(), menu)
    toggleEnabled_action.setToolTip(dialog.form.toggleEnabled.text())
    toggleEnabled_action.setShortcut("F9")
    toggleEnabled_action.triggered.connect(lambda: dialog.form.toggleEnabled.click())
    menu.addAction(toggleEnabled_action)  
    dialog.addAction(toggleEnabled_action) 

    # Добавляем разделительную линию
    menu.addSeparator()

    # Добавляем пункт для установки автообновления
    auto_updateYes_action = QAction(localizationF("auto_updateYes","🔄 Auto update"), menu)
    auto_updateYes_action.setToolTip(localizationF("auto_updateYes_tooltip","All selected add-ons will be updated automatically"))   
    auto_updateYes_action.triggered.connect(lambda: set_auto_update(addons_list, dialog, True))
    menu.addAction(auto_updateYes_action)  
    dialog.addAction(auto_updateYes_action)  

    # Добавляем пункт для снятия автообновления
    auto_updateNo_action = QAction(localizationF("auto_updateNo","🚫 No auto update"), menu)
    auto_updateNo_action.setToolTip(localizationF("auto_updateNo_tooltip","All selected add-ons will not be updated automatically."))   
    auto_updateNo_action.triggered.connect(lambda: set_auto_update(addons_list, dialog, False))
    menu.addAction(auto_updateNo_action)  
    dialog.addAction(auto_updateNo_action) 

    # Добавляем разделительную линию
    menu.addSeparator()

    # Добавляем пункт для копирования в буфер id
    id_to_clb_action = QAction("id → 📋", menu)
    id_to_clb_action.setToolTip("id → 📋")
    id_to_clb_action.setShortcut("Ctrl+C")
    id_to_clb_action.triggered.connect(lambda: id_selected_addons_to_clipboard(addons_list, dialog))
    menu.addAction(id_to_clb_action)  
    dialog.addAction(id_to_clb_action)  

    


    # Устанавливаем политику контекстного меню
    addons_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    addons_list.customContextMenuRequested.connect(show_context_menu)



findStr = "" # подстрока которую будем искать

def findF3(addons_list, dialog):    
    global findStr
    if dialog.form.addonList.count() > 0:
        i = dialog.form.addonList.currentRow()
        i += 1
        while i < dialog.form.addonList.count():            
            item = addons_list.item(i)
            # проверка попадания в условие
            if findStr.lower() in item.text().lower():
                dialog.form.addonList.setCurrentRow(i)
                item = dialog.form.addonList.item(i)
                dialog.form.addonList.scrollToItem(item)  # Прокручиваем к элементу
                return
            i += 1

        # если не нашли
        notfound = localizationF("notfound","Not found") 
        tooltip(f"<p style='color: yellow; background-color: black'>{notfound}</p>", parent=dialog)


def find(addons_list, dialog):    
    if dialog.form.addonList.count() > 0:
        # ввод от пользователя строки      
        global findStr    
        find = localizationF("Find","Find a substring")  
        find_t = localizationF("Find_tooltip","Enter a substring")       
        user_find = ask_user_for_text(dialog, find, find_t, findStr)   
        if user_find == None:
            return  
        findStr = user_find   
        dialog.form.addonList.setCurrentRow(0)
        item = dialog.form.addonList.item(0)
        dialog.form.addonList.scrollToItem(item)  # Прокручиваем к элементу
        dialog.form.addonList.setCurrentRow(-1)
        findF3(addons_list, dialog)   




def sort1(addons_list, dialog):
    """сортировка списка дополнений по дате создания (по убыванию)"""
    global current_sort_flag
    if current_sort_flag == 1:
        current_sort_flag = 0
    else:
        current_sort_flag = 1
    custom_redrawAddons(dialog)


def sort2(addons_list, dialog):
    """сортировка списка дополнений по дате изменения (по убыванию)""" 
    global current_sort_flag
    if current_sort_flag == 2:
        current_sort_flag = 0
    else:
        current_sort_flag = 2 
    custom_redrawAddons(dialog)


def mark_item_list(addons_list, dialog):
    """Пометить цветом все выбранные записи в списке дополнений."""
    addon_manager = mw.addonManager

    # Получаем текущие выбранные строки
    selected_items = addons_list.selectedItems()
    if not selected_items:
        QMessageBox.warning(dialog, localizationF("Warning","Warning"), localizationF("SelectedItems","Please select one or more (+Shift +Ctrl) lines to mark."))
        return
  

    open1 = False
    for selected_item in selected_items:
        addon_name = selected_item.text()

        # Найти соответствующий объект дополнения
        addon = next((a for a in dialog.addons if a.human_name() in addon_name), None)
        if not addon:
            continue  # Пропустить, если дополнение не найдено

        if not open1:
            open1 = True
            # Открыть диалог выбора цвета
            colorCur = QColor("#ffffff")
            if not hasattr(addon, "mark_color") or addon.mark_color is None:
                addon.mark_color = "#000000" # создаем, если такого атрибута почему-то нет

            try:
                colorCur = QColor(addon.mark_color)
            except Exception as e: pass
            color = QColorDialog.getColor(colorCur, dialog, localizationF("SelectedColor","Select a color"))
            if not color.isValid():
                return  # Пользователь закрыл диалог без выбора цвета
            # Преобразуем цвет в HEX
            color_hex = color.name()

        # Сохраняем цвет в meta.json
        addon_path = Path(addon_manager.addonsFolder()) / addon.dir_name
        meta_file = addon_path / "meta.json"

        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)

            # Обновляем или добавляем атрибут mark_color
            meta_data["mark_color"] = color_hex

            # 👉 Сохраняем старую дату модификации
            original_mtime = os.path.getmtime(meta_file)

            # ✍️ Сохраняем изменения в meta.json
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=4)
            
            # 🔄 Восстанавливаем дату модификации
            os.utime(meta_file, (original_mtime, original_mtime))  # (atime, mtime)

        # Сохраняем цвет в объекте дополнения
        addon.mark_color = color_hex

        # Обновляем цвет строки в списке
        if addon.mark_color not in ("#000000", "#ffffff", "#FFFFFF", ""): # раскрашиваем если не белый и не черный
            selected_item.setForeground(QColor(addon.mark_color))    

    custom_redrawAddons(dialog)





def hint_item_list(addons_list, dialog):
    """добавить hint всем выбранным записям в списке дополнений."""
    addon_manager = mw.addonManager

    # Получаем текущие выбранные строки
    selected_items = addons_list.selectedItems()
    if not selected_items:
        QMessageBox.warning(dialog, localizationF("Warning","Warning"), localizationF("SelectedItems","Please select one or more (+Shift +Ctrl) lines to mark."))
        return
  
    user_hint = ""
    open1 = False
    for selected_item in selected_items:
        addon_name = selected_item.text()

        # Найти соответствующий объект дополнения
        addon = next((a for a in dialog.addons if a.human_name() in addon_name), None)
        if not addon:
            continue  # Пропустить, если дополнение не найдено
        
        if not open1:             
            open1 = True
            if not hasattr(addon, "user_hint") or addon.user_hint is None:
                addon.user_hint = "" # создаем, если такого атрибута почему-то нет
            # Открыть диалог ввода строки hint в переменную user_hint   
            hint = localizationF("Hint","✍️ Hint")  
            hint_t = localizationF("Hint_tooltip","Enter brief information that is understandable to you")       
            user_hint = ask_user_for_text(dialog, hint, hint_t, addon.user_hint)   
            if user_hint == None:
                return         
            

        # Сохраняем в meta.json
        addon_path = Path(addon_manager.addonsFolder()) / addon.dir_name
        meta_file = addon_path / "meta.json"

        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)

            old_hint = meta_data.get("hint", "")

            # если user_hint > 1 и в начале идет + - ~ то особо обработка
            if len(user_hint) > 1 and (user_hint[0]=="+" or user_hint[0]=="-" or user_hint[0]=="*"):                                               
                if len(old_hint) == 0:
                    new_user_hint = user_hint[1:]     
                elif user_hint[0]=="-":
                    del_str = user_hint[1:] 
                    new_user_hint = old_hint                    
                    if (len(del_str) > 0 and del_str[0] != "#"):
                        # обычное удаление везде
                        new_user_hint = new_user_hint.replace(del_str, "")
                    else: # удаление сложное с # до # после   
                        del_strS = safe_split_N(del_str, "#", 3)
                        if old_hint[0] != "#":
                            # если особая команда -## удаляет все после
                            if user_hint == "-##":
                                new_user_hint = ""
                            else:
                                new_user_hint = new_user_hint.replace(del_strS[2], "")
                        else:
                            
                            if user_hint == "-##": # если особая команда -## удаляет все после
                                old_hintS = safe_split_N(old_hint, "#", 3)                            
                                new_user_hint = "#" + old_hintS[1] + "#"
                            elif user_hint == "-#": # если особая команда -# удаляет все до
                                old_hintS = safe_split_N(old_hint, "#", 3)                            
                                new_user_hint = "##" + old_hintS[2]
                            else:
                                old_hintS = safe_split_N(old_hint, "#", 3)                            
                                new_user_hint = "#" + old_hintS[1].replace(del_strS[1], "") + "#" + old_hintS[2].replace(del_strS[2], "")
                elif user_hint[0]=="+":
                    add_str = user_hint[1:]
                    new_user_hint = old_hint
                    if len(add_str) <= 1 or (len(add_str) > 0 and add_str[0] != "#"):
                        # обычное добавление в конец
                        new_user_hint = new_user_hint + add_str
                    else: # добавление сложное с # до # после                        
                        add_strS = safe_split_N(add_str, "#", 3)
                        if old_hint[0] != "#":
                            new_user_hint = "#" + add_strS[1] + "#" + old_hint + add_strS[2]
                        else:
                            old_hintS = safe_split_N(old_hint, "#", 3)
                            new_user_hint = "#" + add_strS[1] + old_hintS[1] + "#" + old_hintS[2] + add_strS[2]
                # Обновляем или добавляем атрибут hint
                meta_data["hint"] = new_user_hint # подменяем на измененное
            else:
                meta_data["hint"] = user_hint # полная подмена
                

            # 👉 Сохраняем старую дату модификации
            original_mtime = os.path.getmtime(meta_file)

            # ✍️ Сохраняем изменения в meta.json
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=4)
            
            # 🔄 Восстанавливаем дату модификации
            os.utime(meta_file, (original_mtime, original_mtime))  # (atime, mtime)

        # Сохраняем в объекте дополнения
        addon.hint = user_hint

    # Обновляем строки с учетом hint
    custom_redrawAddons(dialog)


def ask_user_for_text(dialog, title="Brief information that you can understand", label="Enter a hint:", default_text=""):
    """Запрашивает текстовое значение у пользователя."""
    if pyqt_version == "PyQt6":
        text, ok = QInputDialog.getText(dialog, title, label, QLineEdit.EchoMode.Normal, default_text)
    else:  # PyQt5
        text, ok = QInputDialog.getText(dialog, title, label, QLineEdit.Normal, default_text)    
    if ok:  # Если пользователь нажал "OK"
        return text
    return None  # Если пользователь нажал "Cancel"


def set_auto_update(addons_list, dialog, update=True):
    addon_manager = mw.addonManager

    # Получаем текущие выбранные строки
    selected_items = addons_list.selectedItems()
    if not selected_items:
        QMessageBox.warning(dialog, localizationF("Warning","Warning"), localizationF("SelectedItems","Please select one or more (+Shift +Ctrl) lines to mark."))
        return
        
    for selected_item in selected_items:
        addon_name = selected_item.text()

        # Найти соответствующий объект дополнения
        addon = next((a for a in dialog.addons if a.human_name() in addon_name), None)
        if not addon:
            continue  # Пропустить, если дополнение не найдено
       
        # Сохраняем в meta.json
        addon_path = Path(addon_manager.addonsFolder()) / addon.dir_name
        meta_file = addon_path / "meta.json"

        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)

            # Обновляем или добавляем атрибут "update_enabled"
            meta_data["update_enabled"] = update

            # 👉 Сохраняем старую дату модификации
            original_mtime = os.path.getmtime(meta_file)

            # ✍️ Сохраняем изменения в meta.json
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=4)
            
            # 🔄 Восстанавливаем дату модификации
            os.utime(meta_file, (original_mtime, original_mtime))  # (atime, mtime)

        # Сохраняем в объекте дополнения
        addon.update_enabled = update

    # Обновляем строки
    custom_redrawAddons(dialog)


def id_selected_addons_to_clipboard(addons_list, dialog):
    """отправить выделенные строки в буфер обмена"""
    # Получаем текущие выбранные строки
    selected_items = addons_list.selectedItems()
    if not selected_items:
        QMessageBox.warning(dialog, localizationF("Warning","Warning"), localizationF("SelectedItems","Please select one or more (+Shift +Ctrl) lines to mark."))
        return

    str_id = ""

    for selected_item in selected_items:
        addon_name = selected_item.text()

        # Найти соответствующий объект дополнения
        addon = next((a for a in dialog.addons if a.human_name() in addon_name), None)
        if not addon:
            continue  # Пропустить, если дополнение не найдено
       
        if str_id == "":
            str_id = addon.dir_name
        else:
            str_id += " " + addon.dir_name
    
    if str_id == "":
        return
    else:
        QApplication.clipboard().setText(str_id)

        
    


def add_buttons_to_addons_dialog(dialog):
    """Добавляет кнопки в окно 'Add-ons'."""
    global active_profile, current_profile, profile_list_addons, the_profile_will_change
    addons_list = dialog.form.addonList

    # Создаем кнопки
    sort_button1 = QPushButton(localizationF("Sort1","🔽 Sort (created)"), dialog)
    sort_button1.setToolTip(localizationF("Sort1_tooltip","Click to sort the list of add-ons by creation date (descending)"))
    sort_button2 = QPushButton(localizationF("Sort2","🔽 Sort (modified)"), dialog)
    sort_button2.setToolTip(localizationF("Sort2_tooltip","Click to sort the list of add-ons by date modified (descending)"))
    mark_button = QPushButton(localizationF("Mark","🎨 Mark"), dialog)
    mark_button.setToolTip(localizationF("Mark_tooltip","Mark with color"))
    hint_button = QPushButton(localizationF("Hint","✍️ Hint"), dialog)
    hint_button.setToolTip(localizationF("Hint_tooltip","Enter brief information that is understandable to you"))
    
    layout = dialog.form.verticalLayout
    layout.insertWidget(3, sort_button1)
    layout.insertWidget(4, sort_button2)
    layout.insertWidget(5, mark_button)
    layout.insertWidget(6, hint_button)
    
    the_profile_will_change = False # если меняют профиль   
    buttons = []
    group = QButtonGroup()
    group.setExclusive(True)

    for i in range(0, 6):
        btn = QToolButton()
        if i > 0:
            btn.setText(str(i))
            if i == current_profile and i == active_profile:
                # Яркая подсветка для текущей кнопки и активного профиля
                font = btn.font()
                font.setBold(True)
                btn.setFont(font) 
                btn.setStyleSheet("")  # сбросить стиль  
                btn.setStyleSheet("""
                    QToolButton {
                        background-color: #00d700;
                        color: #11C;                    
                    }
                """)   
            elif i == current_profile:     
                btn.setStyleSheet("")  # сбросить стиль  
                # Яркая подсветка для текущей кнопки
                btn.setStyleSheet("""
                    QToolButton {
                        background-color: #00d700;
                        color: #000000;                       
                    }
                """) 
            elif i == active_profile:
                font = btn.font()
                font.setBold(True)
                btn.setFont(font)     
                btn.setStyleSheet("")  # сбросить стиль                        
                # для активного профиля
                btn.setStyleSheet("""
                    QToolButton {                        
                        color: #11C;                      
                    }
                """)                      
        else:
            btn.setText("s⤞")  
            btn.setStyleSheet("")  # сбросить стиль          

        btn.setCheckable(True)
        group.addButton(btn, i)
        buttons.append(btn)

    buttons[current_profile].setChecked(True)
    msg = localizationF("Save_the_current", "Save the current selection of active add-ons to the profile whose number you click after this button")
    buttons[0].setToolTip(msg) 
    msg = localizationF("Profile_of_allowed", "Profile of allowed add-ons (bold - loaded in anki)")
    buttons[1].setToolTip(msg) 
    buttons[2].setToolTip(msg) 
    buttons[3].setToolTip(msg) 
    buttons[4].setToolTip(msg) 
    buttons[5].setToolTip(msg) 

    layoutBTN = QHBoxLayout()
    for btn in buttons:
        layoutBTN.addWidget(btn)

    containerBTN = QWidget()
    containerBTN.setLayout(layoutBTN)
    layout.insertWidget(7, containerBTN)




    def on_button_selected(button):        
        global active_profile, current_profile, profile_list_addons, the_profile_will_change
        id = group.id(button)
        # print(f"on_button_selected: {id}")
        

        if id > 0:
            save_profile(current_profile) 
            current_profile = id

        for idx, btn in enumerate(buttons):
            if idx == 0:
                if id == 0:
                    btn.setStyleSheet("""
                        QToolButton {
                            background-color: #cc3344;
                            color: #000000;                            
                        }
                    """)    
                else:
                    btn.setStyleSheet("")  # сбросить стиль

            else:
                if idx == current_profile and idx == active_profile:
                    font = btn.font()
                    font.setBold(True)
                    btn.setFont(font) 
                    if id != 0:
                        # Яркая подсветка для текущей кнопки и активного профиля                        
                        btn.setStyleSheet("")  # сбросить стиль  
                        btn.setStyleSheet("""
                            QToolButton {
                                background-color: #00d700;
                                color: #006;                                  
                            }
                        """)   
                    else:
                        # Яркая подсветка для текущей кнопки и активного профиля                        
                        btn.setStyleSheet("")  # сбросить стиль  
                        btn.setStyleSheet("""
                            QToolButton {
                                border: 1px solid #00d700;
                                color: #006;                                  
                            }
                        """)

                elif idx == current_profile:     
                    if id != 0:
                        btn.setStyleSheet("")  # сбросить стиль  
                        # Яркая подсветка для текущей кнопки
                        btn.setStyleSheet("""
                            QToolButton {
                                background-color: #00d700;
                                color: #000000;                      
                            }
                        """) 
                    else:
                        btn.setStyleSheet("""
                            QToolButton {
                                border: 1px solid #00d700;
                                color: #000000;                            
                            }
                        """)
                elif idx == active_profile:                    
                    font = btn.font()
                    font.setBold(True)
                    btn.setFont(font)     
                    btn.setStyleSheet("")  # сбросить стиль                        
                    # для активного профиля
                    btn.setStyleSheet("""
                        QToolButton {                        
                            color: #006;                               
                        }
                    """) 
                else:
                    btn.setStyleSheet("")  # сбросить стиль для остальных


        if id > 0:                                   
            if not the_profile_will_change:
                load_profile(id)  
            active_profile_save_meta(id)
            the_profile_will_change = False
        else:
            the_profile_will_change = True

            

        
    group.buttonClicked.connect(on_button_selected)
              
    # Привязываем обработчики к кнопкам
    sort_button1.clicked.connect(lambda: sort1(addons_list, dialog))
    sort_button2.clicked.connect(lambda: sort2(addons_list, dialog))
    mark_button.clicked.connect(lambda: mark_item_list(addons_list, dialog))
    hint_button.clicked.connect(lambda: hint_item_list(addons_list, dialog))

    

def active_profile_save_meta(profN):
    """установить номер активного профиля"""       
    if  profN < 1 or profN > 5: # если вне возможного номера профиля
        return
    try:
        # Путь к meta.json
        addon_dir = Path(mw.addonManager.addonsFolder()) / __name__ 
        meta_path = addon_dir / "meta.json"
        if meta_path.exists():
            original_mtime = os.path.getmtime(meta_path) # Сохраняем старую дату модификации
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                with open(meta_path, "w", encoding="utf-8") as f:                    
                    meta["active_profile"] = profN
                    json.dump(meta, f, ensure_ascii=False, indent=4)
            os.utime(meta_path, (original_mtime, original_mtime))  # Восстанавливаем дату модификации
    except Exception as e:          
        logError(e)             
        
        
def load_profile(profN):
    """загрузить профиль"""    
    global profile_list_addons
    if  profN < 1 or profN > 5: # если вне возможного номера профиля
        return
    try:
        # Путь к meta.json
        addon_dir = Path(mw.addonManager.addonsFolder()) / __name__
        meta_path = addon_dir / "meta.json"

        # Читаем meta.json
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

                profile_key = f"profile{profN}"
                if profile_key in meta:
                    # Загружаем список из выбранного профиля в глобальную переменную                    
                    profile_list_addons = meta.get(profile_key, [])     
                    active_profile_save_meta(profN)  

                    addonList = current_dialog.form.addonList
                    mgr = current_dialog.mgr
                    current_dialog.addons = list(mgr.all_addon_meta())   
                    all_addon_dir = Path(mw.addonManager.addonsFolder())
                    # Обработка meta.json для каждого аддона
                    for addon in current_dialog.addons:
                        addon_dir = all_addon_dir / addon.dir_name
                        meta_path = addon_dir / "meta.json"
                        original_mtime = os.path.getmtime(meta_path) # Сохраняем старую дату модификации
                        enad = addon.dir_name in profile_list_addons
                        if addon.enabled != enad:                            
                            mw.addonManager.toggleEnabled(addon.dir_name, enad)
                            os.utime(meta_path, (original_mtime, original_mtime))  # Восстанавливаем дату модификации
                    custom_redrawAddons(current_dialog)

                                 
    except Exception as e:        
        logError(e)            
    

def save_profile(profN):
    """сохранить профиль"""
    global profile_list_addons        
    if  profN < 1 or profN > 5: # если вне возможного номера профиля
        return

    addonList = current_dialog.form.addonList
    mgr = current_dialog.mgr
    current_dialog.addons = list(mgr.all_addon_meta())   

    profile_list_addons = []

    # Обработка meta.json для каждого аддона
    for addon in current_dialog.addons:
        if addon.enabled:
            profile_list_addons.append(addon.dir_name)


    try:
        # Путь к meta.json
        addon_dir = Path(mw.addonManager.addonsFolder()) / __name__
        meta_path = addon_dir / "meta.json"
        if meta_path.exists():            
            original_mtime = os.path.getmtime(meta_path) # Сохраняем старую дату модификации
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                with open(meta_path, "w", encoding="utf-8") as f:
                        profile_key = f"profile{profN}"
                        if profile_key in meta:
                            meta[profile_key] = profile_list_addons
                            json.dump(meta, f, ensure_ascii=False, indent=4)                            
            os.utime(meta_path, (original_mtime, original_mtime))  # Восстанавливаем дату модификации
                        
    except Exception as e:          
        logError(e)
            