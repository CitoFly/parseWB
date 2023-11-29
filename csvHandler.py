import csv
import fileinput


def create_csv(head: list):
    heads_main = ['id', 'название', 'цена со скидкой', 'бренд', 'продаж', 'рейтинг', 'в наличии']
    all_heads = heads_main + head
    with open("wb_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(all_heads)


def __save_csv(chars: list):
    with open("wb_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(chars)


def numerate_csv():
    with fileinput.FileInput("wb_data.csv", inplace=True) as file:
        for n, row in enumerate(file, start=0):
            print(f"{n},", row, end='')
