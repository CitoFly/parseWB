import csv
import fileinput
import pickle
import matplotlib.pyplot as plt


def create_csv(head: list):
    heads_main = ['id', 'название', 'цена со скидкой', 'бренд', 'продаж', 'рейтинг', 'в наличии']
    all_heads = heads_main + head
    with open("wb_data.csv", mode="w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(all_heads)


def __save_csv(chars: list):
    with open("wb_data.csv", mode="a", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(chars)


def numerate_csv():
    with fileinput.FileInput("wb_data.csv", inplace=True, encoding='utf-8') as file:
        for n, row in enumerate(file, start=0):
            if n != 0:
                print(f"{n},", row, end='')
            else:
                print("№,", row, end='')


def update_price_file():
    temp_dict = {}
    with open('wb_data.csv', 'r', encoding='utf-8') as csv_file:
        for row in csv.DictReader(csv_file):
            temp_dict[int(row[" id"])] = float(row["цена со скидкой"])

    with open('price_history.pkl', 'rb') as file:
        try:
            loaded_dict = pickle.load(file)
        except:
            loaded_dict = {}

    for item in temp_dict:
        try:
            temp_list = loaded_dict[item]
            temp_list.append(temp_dict[item])
            loaded_dict[item] = temp_list
        except:
            loaded_dict[item] = [temp_dict[item]]
        print(item, ":", loaded_dict.get(item))

    with open('price_history.pkl', 'wb') as file:
        pickle.dump(loaded_dict, file)


def show_graph(item_id):
    with open('price_history.pkl', 'rb') as file:
        try:
            loaded_dict = pickle.load(file)
        except:
            loaded_dict = {}

    x = [i for i in range(len(loaded_dict[item_id]))]
    y = loaded_dict[item_id]

    plt.plot(x, y)
    plt.show()
