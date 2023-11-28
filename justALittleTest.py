import matplotlib.pyplot as plt
import pickle
import csv


temp_dict = {}
with open('wb_data.csv', 'r', encoding='utf-8') as csv_file:
    for row in csv.DictReader(csv_file):
        temp_dict[int(row[" id"])] = float(row["цена со скидкой"])

# with open('my_dict.pkl', 'rb') as file:
#     try:
#         loaded_dict = pickle.load(file)
#     except:
#         loaded_dict = {}

# for item in temp_dict:
#     try:
#         loaded_dict[item] = list([temp_dict.get(150752538), temp_dict.get(178623840)])
#     except:
#         loaded_dict[item] = [temp_dict.get(item)]
#     print(item, ": ", loaded_dict.get(item))

# for item in loaded_dict:
#     print(loaded_dict.get(item))


my_dict = {}

my_dict[150752538] = [1583.0, 43375.0]
temp_list = my_dict[150752538]
temp_list.append(109433.0)
my_dict[150752538] = temp_list
print(my_dict)

# print([temp_dict.get(150752538), temp_dict.get(178623840)])

# with open('my_dict.pkl', 'wb') as file:
#     pickle.dump(loaded_dict, file)


x = [1, 2, 3]
y = my_dict[150752538]

plt.plot(x, y)
plt.show()
