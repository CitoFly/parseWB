import asyncio
import aiohttp
import threading
import csv
import customtkinter
from tkinter import *
from tkinter import ttk
import tkinter.messagebox as mb
import webbrowser

from parse import (get_pages_number, get_filter_info, get_item_id, get_item_links, async_get_chars_dict)
from csvHandler import save_csv, numerate_csv, create_csv, update_price_file, show_graph
from models import Items


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

        self.tree = None
        self.progress_bar = None
        self.ScrollableTableFrameV = None
        self.ScrollableTableFrameH = None

        # конфигурация окна
        self.title("Парсер Wildberries v0.4")
        self.geometry(f"{1100}x{580}")
        # прозрачность
        # self.attributes('-alpha', 0.95)

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

        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="Создать график",
                                                        command=self.graph_create)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, text="О программе...",
                                                        command=self.about_program)
        self.sidebar_button_5.grid(row=9, column=0, padx=20, pady=10)

        # создаем меню тем
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_option_menu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # создаем меню изменения масштаба
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_option_menu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_option_menu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # создаем строку ввода
        self.address_bar = customtkinter.CTkEntry(self, placeholder_text="Введите ссылку формата: https://wildberries.ru/...")
        self.address_bar.insert(0, "https://www.wildberries.ru/catalog/elektronika/noutbuki-pereferiya/noutbuki-ultrabuki")
        self.address_bar.grid(row=0, column=1, padx=(20, 0), pady=(16, 0), sticky="new")

        self.page_number_label = customtkinter.CTkLabel(self, text="Число страниц:", anchor="w")
        self.page_number_label.grid(row=0, column=2, padx=(20, 0), pady=(16, 0), sticky="new")
        self.page_number_bar = customtkinter.CTkEntry(self, width=50)
        self.page_number_bar.insert(0, "3")
        self.page_number_bar.grid(row=0, column=2, padx=(120, 10), pady=(16, 0), sticky="new")

        # создаем прокручиваемое окно для checkbox'ов
        self.scrollable_checkbox_frame = ScrollableCheckBoxFrame(self, width=200, label_text="Фильтр")
        self.scrollable_checkbox_frame.grid(row=0, column=2, padx=(20, 10), pady=(67, 10), rowspan=3, sticky="nsew")
        self.scrollable_checkbox_frame.grid_columnconfigure(0, weight=1)

        # задаем стандартные настройки темы и масштаба отображения
        self.appearance_mode_option_menu.set("Dark")
        self.change_appearance_mode_event("Dark")
        self.scaling_option_menu.set("100%")
        self.style = ttk.Style()
        self.style.theme_use("alt")
        self.style.configure("Treeview.Heading", background="#2B2B2B",filedbackground="#2B2B2B", foreground="#F9F9FA")
        self.style.configure("Treeview", background="#2B2B2B", fieldbackground="#2B2B2B", foreground="#F9F9FA")

        self.style.configure("Treeview.Heading", font=(None, 11))
        self.style.configure("Treeview", font=(None, 10))

    # функция изменения темы
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        if new_appearance_mode == "Dark":
            style = ttk.Style()
            style.theme_use("alt")
            style.configure("Treeview.Heading", background="#2B2B2B", foreground="#F9F9FA")
            style.configure("Treeview", background="#2B2B2B", fieldbackground="#2B2B2B", foreground="#F9F9FA")
        else:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview.Heading", background="white", foreground="black")
            style.configure("Treeview", background="white", fieldbackground="white", foreground="black")

    # функция изменения масштаба
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

        tree_scaling = int(int(new_scaling.replace("%", "")) / 10 + 1)

        self.style.configure("Treeview.Heading", font=(None, tree_scaling))
        self.style.configure("Treeview", font=(None, tree_scaling-1))

    def create_filter_thread(self):
        filter_thread = threading.Thread(target=self.filter_create)
        filter_thread.start()

    def create_parse_thread(self):
        parse_thread = threading.Thread(target=self.parse_start)
        parse_thread.start()

    # функция создания фильтра
    def filter_create(self):
        url = self.address_bar.get()
        self.sidebar_button_1.configure(state="disabled")
        # получаем список фильтров
        item_list = get_filter_info(url)
        # очищаем окно фильтра
        self.scrollable_checkbox_frame.remove_items()
        # заполняем окно фильтра
        for item in item_list:
            self.scrollable_checkbox_frame.add_item(item)
        self.sidebar_button_1.configure(state="normal")

    def table_create(self):
        # добавляем данные в таблицу
        with open('wb_data.csv', 'r', newline='') as csvfile:
            wb_table = csv.reader(csvfile, delimiter=',', quotechar='|')  # получаем данные из csv файла
            heads = next(wb_table)  # определяем столбцы будущей таблицы

            # создание основы таблицы
            self.tree = ttk.Treeview(master=self, columns=heads, show="headings")
            self.tree.grid(row=0, column=1, padx=(20, 0), pady=(67, 10), rowspan=3, sticky="nsew")
            self.tree.bind('<Double-Button-1>', self.open_item_url)

            self.ScrollableTableFrameV = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=self.ScrollableTableFrameV.set)
            self.ScrollableTableFrameV.grid(row=0, column=1, padx=(20, 0), pady=(67, 10), rowspan=3, sticky="nse")

            self.ScrollableTableFrameH = customtkinter.CTkScrollbar(self, orientation="horizontal", command=self.tree.xview)
            self.tree.configure(xscrollcommand=self.ScrollableTableFrameH.set)
            self.ScrollableTableFrameH.grid(row=2, column=1, padx=(20, 0), pady=(16, 0), sticky="sew")

            for head in heads:
                self.tree.heading(head, text=head)
                self.tree.column(head, anchor="w", stretch=NO, width=100)
            # заполнение таблицы
            for row in wb_table:
                self.tree.insert("", END, values=row)

    def open_item_url(self, event):
        try:
            selected_id = self.tree.focus()
            item_id = int(self.tree.item(selected_id)["values"][1])
        except:
            return
        url = f"https://www.wildberries.ru/catalog/{item_id}/detail.aspx"
        webbrowser.open(url, new=0, autoraise=True)

    def graph_create(self):
        try:
            selected_id = self.tree.focus()
            item_id = int(self.tree.item(selected_id)["values"][1])
            show_graph(item_id)
        except:
            mb.showinfo("Ошибка", "Объект таблицы не выбран.")

    def update_price_list(self):
        update_price_file()

    def about_program(self):
        msg = ("Страница: https://github.com/CitoFly/parseWB\n\n"
               "Программа предназначена для получения информации о товарах с сайта Wildberries.ru.\n\n"
               "Правила использования:\n"
               "1) Скопируйте и вставьте ссылку на категорию товаров в адресную строку;\n"
               "2) Нажмите кнопку 'Создать фильтр' и дождитесь его создания;\n"
               "3) Выберите интересующие вас пункты;\n"
               "4) Над фильтром укажите количество страниц, которые обработает программа;\n"
               "5) Нажмите кнопку 'Начать парсинг' и дождитесь завершения."
               "После завершения автоматически создастся таблица с информацией о товарах"
               "и обновятся цены в файле 'price_history.pkl'\n"
               "6) Для того, чтобы вывести график истории цен, выделите в таблице используя ЛКМ"
               "и нажмите кнопку 'Создать график'.\n")
        mb.showinfo("О программе", msg)

    def parse_start(self):
        url = self.address_bar.get()

        if not url:
            mb.showinfo("Ошибка", "Ссылка отсутствует.")
            exit()

        checkbox_selected_list = self.scrollable_checkbox_frame.get_checked_items()
        if not checkbox_selected_list:
            mb.showinfo("Ошибка", "Фильтр пуст.")
            exit()

        self.sidebar_button_2.configure(state="disabled")

        # Начинаем парсинг
        create_csv(checkbox_selected_list)

        pages_number = int(self.page_number_bar.get()) if self.page_number_bar.get() else int(get_pages_number(url))

        self.progress_bar = customtkinter.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=(20, 0), pady=(50, 0), sticky="new")

        for _page in range(1, pages_number+1):
            links = get_item_links(url)
            self.progress_bar.configure(self, determinate_speed=100 / len(links) / pages_number / 2)
            asyncio.run(main_parse(links, checkbox_selected_list))

        # пронумеруем строки
        self.progress_bar.destroy()
        self.sidebar_button_2.configure(state="normal")
        numerate_csv()
        self.table_create()
        update_price_file()


async def main_parse(links: list, filter_list: list):
    tasks = []

    async with aiohttp.ClientSession() as session:

        for link in links:
            task = asyncio.create_task(parse_item_chars(link, filter_list, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def parse_item_chars(link: str, filter_list: list, session):
    filtered_chars_list = []
    item_id = get_item_id(link)

    async with session.get(
            f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=123585774&spp=25&nm={item_id}") as response:
        json_data = await response.json()
        item_main_info = Items.model_validate(json_data["data"])

    for item_info in item_main_info.products:
        filtered_chars_list.append(item_info.id)
        filtered_chars_list.append(item_info.name)
        filtered_chars_list.append(item_info.salePriceU)
        filtered_chars_list.append(item_info.brand)
        filtered_chars_list.append(item_info.sale)
        filtered_chars_list.append(item_info.rating)
        filtered_chars_list.append(item_info.volume)

    full_chars_dict = await async_get_chars_dict(link, session)
    for item in filter_list:
        try:
            filtered_chars_list.append(full_chars_dict[item].replace(',', ';'))
        except:
            filtered_chars_list.append("NaN")
    save_csv(filtered_chars_list)
    app.progress_bar.step()


if __name__ == "__main__":
    app = App()
    app.mainloop()
