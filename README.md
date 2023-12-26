![image](https://github.com/CitoFly/parseWB/assets/74175035/096ab685-bcef-4761-80ca-9169736a296e)


### Программа предназначена для получения информации о товарах с сайта Wildberries.ru.
### Правила использования:
1) Скопируйте и вставьте ссылку на категорию товаров в адресную строку;
2) Нажмите кнопку 'Создать фильтр' и дождитесь его создания;
3) Выберите интересующие вас пункты;
4) Над фильтром укажите количество страниц, которые обработает программа;
5) Нажмите кнопку 'Начать парсинг' и дождитесь завершения.
После завершения автоматически создастся таблица с информацией о товарах и обновятся цены в файле 'price_history.pkl'
6) Для того, чтобы вывести график истории цен, выделите в таблице используя ЛКМ и нажмите кнопку 'Создать график'.
### Установка библиотек
python -m pip install -U pip setuptools\
python -m pip install matplotlib\
pip3 install -r requirements.txt

### Основные файлы
main.py\
parse.py\
csvHandler.py\
models.py\
wb_data.csv\
price_history.pkl
