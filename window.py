import threading
import customtkinter
from main import get_pages_number, get_filter_info, main_parse
from csvHandler import numerate_csv, create_csv
import csv
from tkinter import ttk
from tkinter import *


class ScrollableCheckBoxFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.checkbox_list = []

    def add_item(self, item):
        checkbox = customtkinter.CTkCheckBox(self, text=item)
        checkbox.grid(column=0, padx=10, pady=(0, 20), sticky="w")
        self.checkbox_list.append(checkbox)

    def remove_items(self):
        for checkbox in reversed(self.checkbox_list):
            checkbox.destroy()
            self.checkbox_list.remove(checkbox)

    def get_checked_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.progress_bar = None
        self.ScrollableTableFrame = None

        # конфигурация окна
        self.title("Парсер Wildberries v0.3")
        self.geometry(f"{1100}x{580}")
        # прозрачность
        self.attributes('-alpha', 0.95)

        # конфигурация сетки отображения
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # создаем боковое окно для виджетов
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Парсер",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # создаем кнопки создания фильтра и начала парсинга
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Создать фильтр",
                                                        command=self.create_filter_thread)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Начать парсинг",
                                                        command=self.create_parse_thread)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Создать таблицу",
                                                        command=self.table_create)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="Стоп",
        #                                                 command=self.create_parse_thread.stop_parse_thread)
        # self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        # создаем меню тем
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # создаем меню изменения масштаба
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # создаем строку ввода
        self.address_bar = customtkinter.CTkEntry(self, placeholder_text="Введите ссылку формата: https://wildberries.ru/...")
        self.address_bar.insert(0, "https://www.wildberries.ru/catalog/elektronika/noutbuki-pereferiya/noutbuki-ultrabuki")
        self.address_bar.grid(row=0, column=1, padx=(20, 0), pady=(16, 0), sticky="new")

        self.page_number_label = customtkinter.CTkLabel(self, text="Число страниц:", anchor="w")
        self.page_number_label.grid(row=0, column=2, padx=(20, 0), pady=(16, 0), sticky="new")
        self.page_number_bar = customtkinter.CTkEntry(self)
        self.page_number_bar.grid(row=0, column=2, padx=(120, 10), pady=(16, 0), sticky="new")

        # создаем прокручиваемое окно для checkbox'ов
        self.scrollable_checkbox_frame = ScrollableCheckBoxFrame(master=self, width=200, label_text="Фильтр")
        self.scrollable_checkbox_frame.grid(row=0, column=2, padx=(20, 10), pady=(67, 10), rowspan=3, sticky="nsew")
        self.scrollable_checkbox_frame.grid_columnconfigure(0, weight=1)

        # задаем стандартные настройки темы и масштаба отображения
        self.appearance_mode_optionemenu.set("Dark")
        self.change_appearance_mode_event("Dark")
        self.scaling_optionemenu.set("100%")
        style = ttk.Style()
        style.theme_use("alt")
        style.configure("Treeview.Heading", background="#2B2B2B",filedbackground="#2B2B2B", foreground="#F9F9FA")
        style.configure("Treeview", background="#2B2B2B", fieldbackground="#2B2B2B", foreground="#F9F9FA")

    # функция изменения темы
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode == "Dark":
            style = ttk.Style()
            style.theme_use("alt")
            style.configure("Treeview.Heading", background="#2B2B2B", foreground="#F9F9FA")
            style.configure("Treeview", background="#2B2B2B", fieldbackground="#2B2B2B", foreground="#F9F9FA")
        elif new_appearance_mode in ["Light", "System"]:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview.Heading", background="white", foreground="black")
            style.configure("Treeview", background="white", fieldbackground="white", foreground="black")

    # функция изменения масштаба
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def create_filter_thread(self):
        print("Начинаем сбор фильтров")
        filter_thread = threading.Thread(target=self.filter_create)
        filter_thread.start()

    def create_parse_thread(self):
        parse_thread = threading.Thread(target=self.parse_start)
        parse_thread.start()

    # функция создания фильтра
    def filter_create(self):
        url = self.address_bar.get()
        # получаем список фильтров
        item_list = get_filter_info(url)
        # очищаем окно фильтра
        self.scrollable_checkbox_frame.remove_items()
        # заполняем окно фильтра
        for item in item_list:
            self.scrollable_checkbox_frame.add_item(item)

    def table_create(self):
        # добавляем данные в таблицу
        with open('wb_data.csv', 'r', newline='') as csvfile:
            # получаем данные из csv файла
            wb_table = csv.reader(csvfile, delimiter=',', quotechar='|')
            # определяем столбцы будущей таблицы
            heads = next(wb_table)
            # создание основы таблицы
            self.ScrollableTableFrame = customtkinter.CTkScrollableFrame(self, orientation="horizontal")
            self.ScrollableTableFrame.grid(row=0, column=1, padx=(20, 0), pady=(67, 10), rowspan=3, sticky="nsew")
            tree = ttk.Treeview(master=self.ScrollableTableFrame, columns=heads, show="headings", style="myStyle.Treeview")
            tree.pack(expand=True, fill="y")
            for head in heads:
                tree.heading(head, text=head)
                tree.column(head, anchor=CENTER, stretch=NO, width=100)
            # заполнение таблицы
            for row in wb_table:
                tree.insert("", END, values=row)

    def parse_start(self):
        url = self.address_bar.get()

        if not url:
            print("ссылка отсутствует")
            exit()

        checkbox_selected_list = self.scrollable_checkbox_frame.get_checked_items()
        if not checkbox_selected_list:
            print("Фильтр пуст")
            exit()

        print("Начинаем парсинг")
        # парсим
        create_csv(checkbox_selected_list)

        pages_number = int(self.page_number_bar.get()) if self.page_number_bar.get() else int(get_pages_number(url))
        print(f"Число страниц: {pages_number}")
        self.progress_bar = customtkinter.CTkProgressBar(self, width=130, determinate_speed=100/pages_number/2)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=10)
        self.progress_bar.set(0)

        for i in range(1, pages_number+1):
            main_parse(url + f"?page={i}", checkbox_selected_list)
            self.progress_bar.step()
        # пронумеруем строки
        numerate_csv()
        self.table_create()


if __name__ == "__main__":
    app = App()
    app.mainloop()
