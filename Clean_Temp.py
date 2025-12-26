import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import ctypes

class CleanTempApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clean Temp - Удаление временных файлов")
        self.root.geometry("900x650")

        # Запрещаем изменение размера окна
        self.root.resizable(False, False)
        
        # Переменные для сортировки
        self.sort_column = "file"
        self.sort_reverse = False
        self.display_data = []  # Для хранения данных для сортировки
        
        # Переменные для хранения данных
        self.temp_files = []
        self.total_size = 0
        
        # Стиль для виджетов
        self.setup_styles()
        
        # Основная структура
        self.create_widgets()
        
    def setup_styles(self):
        """Настройка стилей виджетов"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Стиль для вкладок
        style.configure("Custom.TNotebook", background="#FFFFFF")
        style.configure("Custom.TNotebook.Tab", 
                       background="#910909",
                       foreground="white",
                       padding=[10, 5],
                       font=("Segoe UI", 10, "bold"))
        style.map("Custom.TNotebook.Tab", 
                 background=[("selected", "#910909")],
                 foreground=[("selected", "white")])
        
        # Стиль для кнопок
        style.configure("CleanTemp.TButton", 
                       background="#910909",
                       foreground="white",
                       borderwidth=2,
                       font=("Segoe UI", 10, "bold"),
                       padding=8,
                       relief="raised")
        style.map("CleanTemp.TButton",
                 background=[("active", "#B22222")],
                 foreground=[("active", "white")])
        
        # Стиль для Treeview
        style.configure("CleanTemp.Treeview",
                      background="#FFFFFF",
                      foreground="#1A1A2E",
                      fieldbackground="#FFFFFF",
                      rowheight=25,
                      font=("Segoe UI", 9))
        style.configure("CleanTemp.Treeview.Heading",
                      background="#910909",
                      foreground="white",
                      relief="flat",
                      font=("Segoe UI", 10, "bold"))
        style.map("CleanTemp.Treeview.Heading",
                 background=[("active", "#B22222")])
        
        # Стиль для скроллбаров
        style.configure("TScrollbar",
                       background="#910909",
                       troughcolor="#F0F0F0",
                       borderwidth=2,
                       relief="flat")
        style.map("TScrollbar",
                 background=[("active", "#B22222")])
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""

        # Цвет фона окна
        self.root.configure(bg='#FFFFFF')
        
        # Основной фрейм для содержимого
        self.main_frame = tk.Frame(self.root, bg='#FFFFFF')
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Notebook (вкладки)
        notebook = ttk.Notebook(self.main_frame, style="Custom.TNotebook")
        notebook.pack(fill="both", expand=True)
        
        # Вкладка 1: Проверка файлов
        self.check_frame = ttk.Frame(notebook, style="Custom.TNotebook")
        notebook.add(self.check_frame, text="Проверка файлов")
        
        # Вкладка 2: Удаление файлов
        self.delete_frame = ttk.Frame(notebook, style="Custom.TNotebook")
        notebook.add(self.delete_frame, text="Удаление файлов")
        
        # Настройка вкладки проверки
        self.setup_check_tab()
        
        # Настройка вкладки удаления
        self.setup_delete_tab()
        
        # Панель статистики внизу окна
        self.setup_footer_stats()
        
    def setup_check_tab(self):
        """Настройка вкладки проверки файлов"""

        # Панель с кнопками
        button_frame = tk.Frame(self.check_frame, bg='#FFFFFF')
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Кнопка проверки
        check_btn = ttk.Button(button_frame, 
                              text="Проверить файлы",
                              style="CleanTemp.TButton",
                              command=self.check_temp_files)
        check_btn.pack(side="left", padx=(0, 10))
        
        # Фрейм для таблицы с прокруткой
        table_frame = tk.Frame(self.check_frame, bg='#FFFFFF')
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        # Таблица для отображения файлов
        columns = ("file", "size", "date")
        self.tree = ttk.Treeview(table_frame, 
                                columns=columns, 
                                show="headings",
                                style="CleanTemp.Treeview",
                                height=18,
                                selectmode="extended")
        
        # Настройка колонок с функциями сортировки и выравниванием
        self.tree.heading("file", text="Temp File", 
                         command=lambda: self.sort_by_column("file"))
        self.tree.heading("size", text="Size", 
                         command=lambda: self.sort_by_column("size"))
        self.tree.heading("date", text="Date Created", 
                         command=lambda: self.sort_by_column("date"))
        
        # Выравнивание колонок
        self.tree.column("file", width=400, minwidth=200, anchor="w")
        self.tree.column("size", width=150, minwidth=100, anchor="e")
        self.tree.column("date", width=200, minwidth=150, anchor="e")
        
        # Полосы прокрутки
        v_scrollbar = ttk.Scrollbar(table_frame, 
                                   orient="vertical", 
                                   command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame,
                                   orient="horizontal",
                                   command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set,
                           xscrollcommand=h_scrollbar.set)
        
        # Размещение виджетов в grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Настройка grid для растягивания
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Изначально показываем "No Files Deleted"
        self.tree.insert("", "end", values=("No Files Deleted", "", ""))
        
    def setup_delete_tab(self):
        """Настройка вкладки удаления файлов"""

        # Фрейм для содержимого
        content_frame = tk.Frame(self.delete_frame, bg='#FFFFFF')
        content_frame.place(relx=0.5, rely=0.35, anchor="center")  # Подняли немного выше
        
        # Заголовок
        title_label = tk.Label(content_frame,
                              text="Удалить временные файлы",
                              font=("Segoe UI", 18, "bold"),
                              fg="#1A1A2E",
                              bg="#FFFFFF")
        title_label.pack(pady=(0, 20))
        
        # Описание
        description_label = tk.Label(content_frame,
                                    text="Нажмите кнопку выше для удаления временных файлов.\nПеред удалением потребуется подтверждение.",
                                    font=("Segoe UI", 11),
                                    fg="#1A1A2E",
                                    bg="#FFFFFF",
                                    justify="center")
        description_label.pack(pady=(0, 30))
        
        # Кнопка удаления
        delete_btn = ttk.Button(content_frame,
                               text="Удалить временные файлы",
                               style="CleanTemp.TButton",
                               command=self.delete_temp_files)
        delete_btn.pack(ipadx=20, ipady=5)
        
    def setup_footer_stats(self):
        """Панель статистики внизу окна"""

        # Отдельный фрейм для статистики под основным фреймом
        self.footer_frame = tk.Frame(self.root, bg='#910909', height=40)
        self.footer_frame.pack(side="bottom", fill="x", padx=0, pady=0)
        
        # Статистика файлов
        self.stats_label = tk.Label(self.footer_frame,
                                    text="Обнаружено файлов: 0 | Общий вес: 0 Б",
                                    font=("Segoe UI", 10, "bold"),
                                    bg="#910909",
                                    fg="white",
                                    padx=20,
                                    pady=10)
        self.stats_label.pack(side="right")
        
    def sort_by_column(self, column):
        """Сортировка данных по колонке"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Ключ для сортировки
        if column == "file":
            key = lambda x: x[0].lower()  # Сортировка по имени без учета регистра
        elif column == "size":
            key = lambda x: x[3]  # Сортировка по размеру в байтах
        elif column == "date":
            key = lambda x: x[4]  # Сортировка по дате создания
        
        # Сортировка данных
        self.display_data.sort(key=key, reverse=self.sort_reverse)
        
        # Обновление отображения
        self.update_treeview()
        
        # Обновление заголовков для отображения стрелки сортировки
        self.update_sort_indicators()
    
    def update_sort_indicators(self):
        """Обновление индикаторов сортировки в заголовках"""
        columns = ["file", "size", "date"]
        for col in columns:
            current_text = self.tree.heading(col, "text").replace(" ↑", "").replace(" ↓", "")
            if col == self.sort_column:
                arrow = " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(col, text=f"{current_text}{arrow}")
            else:
                self.tree.heading(col, text=current_text)
    
    def update_treeview(self):
        """Обновление отображения данных в Treeview"""

        # Очищаем текущие данные
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Если нет файлов
        if not self.display_data:
            self.tree.insert("", "end", values=("No Files Deleted", "", ""))
        else:
            # Добавляем отсортированные данные
            for file_data in self.display_data:
                self.tree.insert("", "end", 
                               values=(file_data[0], file_data[1], file_data[2]))
    
    def format_size(self, bytes):
        """Форматирование размера файла"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} ТБ"
    
    def check_temp_files(self):
        """Проверка временных файлов"""
        temp_path = os.environ.get('TEMP', 'C:\\Windows\\Temp')
        
        # Очистка предыдущих данных
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.temp_files = []
        self.total_size = 0
        file_count = 0
        self.display_data = []
        
        try:
            # Рекурсивный поиск файлов в папке Temp
            for root_dir, dirs, files in os.walk(temp_path):
                for file in files:
                    try:
                        file_path = os.path.join(root_dir, file)
                        
                        # Получаем информацию о файле
                        stat = os.stat(file_path)
                        size = stat.st_size
                        # Получаем дату создания
                        date_created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Добавляем файл в списки
                        self.temp_files.append(file_path)
                        self.total_size += size
                        file_count += 1
                        
                        # Добавляем данные для отображения и сортировки
                        display_name = file if len(file) <= 50 else file[:47] + "..."
                        self.display_data.append([
                            display_name,  # 0 - отображаемое имя
                            self.format_size(size),  # 1 - форматированный размер
                            date_created,  # 2 - дата создания
                            size,  # 3 - размер в байтах для сортировки
                            stat.st_ctime  # 4 - время создания для сортировки
                        ])
                        
                    except (PermissionError, OSError, FileNotFoundError):
                        continue  # Пропускаем файлы, к которым нет доступа
            
            # Обновляем отображение
            self.sort_by_column(self.sort_column)  # Применяем текущую сортировку
            
            # Обновляем статистику внизу окна
            self.update_footer_stats(file_count, self.total_size)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить файлы: {str(e)}")
    
    def update_footer_stats(self, file_count, total_size):
        """Обновление статистики в подвале"""
        self.stats_label.config(text=f"Обнаружено файлов: {file_count} | Общий вес: {self.format_size(total_size)}")
        
    def delete_temp_files(self):
        """Удаление временных файлов"""
        if not self.temp_files:
            messagebox.showwarning("Предупреждение", "Сначала проверьте файлы!")
            return
        
        # Диалог подтверждения
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы действительно хотите очистить {len(self.temp_files)} файлов?\n"
            f"Общий вес файлов: {self.format_size(self.total_size)}",
            icon='warning',
            parent=self.root
        )
        
        if confirm:
            deleted_count = 0
            deleted_size = 0
            errors = []
            
            for file_path in self.temp_files:
                try:
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_count += 1
                        deleted_size += size
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)[:30]}...: {str(e)}")
            
            # Обновляем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.tree.insert("", "end", values=("No Files Deleted", "", ""))
            
            # Сбрасываем данные
            self.temp_files = []
            self.total_size = 0
            self.display_data = []
            
            # Обновляем статистику внизу окна
            self.update_footer_stats(0, 0)
            
            # Показываем результат
            messagebox.showinfo("Успех", 
                               f"Удалено файлов: {deleted_count}\nОсвобождено места: {self.format_size(deleted_size)}",
                               parent=self.root)
            
            # Сбрасываем сортировку
            self.sort_column = "file"
            self.sort_reverse = False
            self.update_sort_indicators()

def main():
    root = tk.Tk()
    
    # Настраиваем иконку окна
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CleanTemp.App")
    except:
        pass
    
    # Настраиваем стиль окна для Windows 11
    try:
        root.call('tk', 'scaling', 1.5)  # Масштабирование для HiDPI
    except:
        pass
    
    # Центрируем окно на экране
    root.update_idletasks()
    width = 900
    height = 650
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Скрываем консольное окно
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    app = CleanTempApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()