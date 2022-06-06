# ======================================= Развлечения
import requests
import bs4  # BeautifulSoup4
from telebot import types
from io import BytesIO
import wikipedia
import re
import telebot

# -----------------------------------------------------------------------
from wiki import bot


def get_text_messages(bot, cur_user, message):
    chat_id = message.chat.id
    ms_text = message.text

    if ms_text == "Прислать собаку":
        bot.send_photo(chat_id, photo=get_dogURL(), caption="Вот тебе собачка!")

    elif ms_text == "Прислать лису":
        bot.send_photo(chat_id, photo=get_foxURL(), caption="Вот тебе лисичка!")

    elif ms_text == "Прислать анекдот":
        bot.send_message(chat_id, text=get_anekdot())

    elif ms_text == "Прислать фильм":
        send_film(bot, chat_id)

    elif ms_text == "Угадай кто?":
        get_ManOrNot(bot, chat_id)

    # elif ms_text == "Прислать курсы":
    #     bot.send_message(chat_id, text=get_cur())

    elif ms_text == "Вики":
        bot.send_message(chat_id)

    elif ms_text == "RU":
        msg = bot.send_message(chat_id,'Отправь мне слово и вы получите статью на русском языке ')
        bot.register_next_step_handler(msg, getwikiru)

    elif ms_text == "UA":
        msg = bot.send_message(chat_id,'Отправь мне слово и вы получите статью на украинском языке')
        bot.register_next_step_handler(msg, getwikieng)

# -----------------------------------------------------------------------
def send_film(bot, chat_id):
    film = get_randomFilm()
    info_str = f"<b>{film['Наименование']}</b>\n" \
               f"Год: {film['Год']}\n" \
               f"Страна: {film['Страна']}\n" \
               f"Жанр: {film['Жанр']}\n" \
               f"Продолжительность: {film['Продолжительность']}"
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Трейлер", url=film["Трейлер_url"])
    btn2 = types.InlineKeyboardButton(text="СМОТРЕТЬ онлайн", url=film["фильм_url"])
    markup.add(btn1, btn2)
    bot.send_photo(chat_id, photo=film['Обложка_url'], caption=info_str, parse_mode='HTML', reply_markup=markup)

# -----------------------------------------------------------------------
def get_anekdot():
    array_anekdots = []
    req_anek = requests.get('http://anekdotme.ru/random')
    if req_anek.status_code == 200:
        soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
        result_find = soup.select('.anekdot_text')
        for result in result_find:
            array_anekdots.append(result.getText().strip())
    if len(array_anekdots) > 0:
        return array_anekdots[0]
    else:
        return ""


# -----------------------------------------------------------------------
# def get_news():
#     array_anekdots = []
#     req_anek = requests.get('https://www.banki.ru/news/lenta')
#     if req_anek.status_code == 200:
#         soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
#         result_find = soup.select('.doFpcq')
#         for result in result_find:
#             print(result)
#
#             # array_anekdots.append(result.getText().strip())
#     if len(array_anekdots) > 0:
#         return array_anekdots[0]
#     else:
#         return ""


# -----------------------------------------------------------------------
def get_foxURL():
    url = ""
    req = requests.get('https://randomfox.ca/floof/')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['image']
        # url.split("/")[-1]
    return url


# -----------------------------------------------------------------------
def get_dogURL():
    url = ""
    req = requests.get('https://random.dog/woof.json').json()
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['url']
        # url.split("/")[-1]
    return url


# -----------------------------------------------------------------------
# def get_cur_pairs():
#     lst_cur_pairs = []
#     req_currency_list = requests.get(f'https://currate.ru/api/?get=currency_list&key=')
#     if req_currency_list.status_code == 200:
#         currency_list_json = req_currency_list.json()
#         for pairs in currency_list_json["data"]:
#             if pairs[3:] == "RUB":
#                 lst_cur_pairs.append(pairs)
#     return lst_cur_pairs


# -----------------------------------------------------------------------
# def get_cur():
#     txt_curses = ""
#     txt_pairs = ",".join(get_cur_pairs())
#     req_currency_rates = requests.get(f'https://currate.ru/api/?get=rates&pairs={txt_pairs}')
#     if req_currency_rates.status_code == 200:
#         currency_rates = req_currency_rates.json()
#         for pairs, rates in currency_rates["data"].items():
#             txt_curses += f"{pairs} : {rates}\n"
#     else:
#         txt_curses = req_currency_rates.text
#     return txt_curses


# -----------------------------------------------------------------------
def get_ManOrNot(bot, chat_id):

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Проверить", url="https://vc.ru/dev/58543-thispersondoesnotexist-sayt-generator-realistichnyh-lic")
    markup.add(btn1)

    req = requests.get("https://thispersondoesnotexist.com/image", allow_redirects=True)
    if req.status_code == 200:
        img = BytesIO(req.content)
        bot.send_photo(chat_id, photo=img, reply_markup=markup, caption="Этот человек реален?")


# ---------------------------------------------------------------------
def get_randomFilm():
    url = 'https://randomfilm.ru/'
    infoFilm = {}
    req_film = requests.get(url)
    soup = bs4.BeautifulSoup(req_film.text, "html.parser")
    result_find = soup.find('div', align="center", style="width: 100%")
    infoFilm["Наименование"] = result_find.find("h2").getText()
    names = infoFilm["Наименование"].split(" / ")
    infoFilm["Наименование_rus"] = names[0].strip()
    if len(names) > 1:
        infoFilm["Наименование_eng"] = names[1].strip()

    images = []
    for img in result_find.findAll('img'):
        images.append(url + img.get('src'))
    infoFilm["Обложка_url"] = images[0]

    details = result_find.findAll('td')
    infoFilm["Год"] = details[0].contents[1].strip()
    infoFilm["Страна"] = details[1].contents[1].strip()
    infoFilm["Жанр"] = details[2].contents[1].strip()
    infoFilm["Продолжительность"] = details[3].contents[1].strip()
    infoFilm["Режиссёр"] = details[4].contents[1].strip()
    infoFilm["Актёры"] = details[5].contents[1].strip()
    infoFilm["Трейлер_url"] = url + details[6].contents[0]["href"]
    infoFilm["фильм_url"] = url + details[7].contents[0]["href"]

    return infoFilm
def getwikiru(message):
    wikipedia.set_lang('ru')
    s = message.text
    try:
        ny = wikipedia.page(s)
        # Получаем первую тысячу символов
        wikitext=ny.content[:1000]
        # Разделяем по точкам
        wikimas=wikitext.split('.')
        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        print(wikimas)
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\{[^\{\}]*\}', '', wikitext2)

        # Возвращаем текстовую строку
        bot.send_message(message.chat.id,wikitext2)
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as s:
        return 'В энциклопедии нет информации об этом'

     # Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов

def getwikieng(message):
    wikipedia.set_lang('uk')
    s = message.text
    try:
        ny = wikipedia.page(s)
        # Получаем первую тысячу символов
        wikitext=ny.content[:1000]
        # Разделяем по точкам
        wikimas=wikitext.split('.')
        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        print(wikimas)
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\{[^\{\}]*\}', '', wikitext2)

        # Возвращаем текстовую строку
        bot.send_message(message.chat.id,wikitext2)
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as s:
        return 'В энциклопедии нет информации об этом'

        # Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
