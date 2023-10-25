import telebot
from datetime import datetime,timedelta
import time
from telebot import types
import json
import asyncio
import threading
global scheduled_posts
#bot = telebot.TeleBot('6325448607:AAG1A6SrroRxRflwo0fPx5bW3ix0o3NA8pY') # avenues token
#bot = telebot.TeleBot('6590558087:AAHrxCBnqfl_YCO3F2Xz71kFo1f3dLfHfWY') # clients token
bot = telebot.TeleBot('6485397598:AAFhK43IdxrK6Dk3oTpruk-TFpNj2U9ULVk') # test token
#chat_ids = [-1001957519885] # clients chat
chat_ids = [-1001922928792] # test chat
#chat_ids = [-1001834326731] # avenues chat
superadmins = [919422317,1387957204,5016708080,810311297,6609142734]
scheduled_posts = []
now = datetime.now()
year = datetime.now().year
async def load_db():
    with open("db.json", "r") as read_file:
        db = json.load(read_file)
    for post in db:
        time_end = datetime.strptime(f"{year}.{post['time_end']}", '%Y.%d.%m %H:%M')
        if time_end > now:
            post['time_end'] = time_end
            scheduled_posts.append(post)

        thread1 = threading.Thread(target=schedule_message, args=(chat_ids[0], post["text"], post["photo"], post["time"],
                             post["time_delta"], post["time_end"], post["id"]))
        await thread1.start()
        thread1.join()
async def schedule_message(chat_id,text_spam,photo_id,post_time,time_delta,time_end,id):
    print("test23")
    year = datetime.now().year
    time_end = datetime.strptime(f"{year}.{time_end}", '%Y.%d.%m %H:%M')
    post_time = datetime.strptime(f"{post_time}", '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    while time_end > now:
        try:
            delta_time =post_time -datetime.now()
            await asyncio.sleep(delta_time.seconds+2)
            for target_chat_id in chat_ids:
                print('test1')
                print(scheduled_posts)
                for post in scheduled_posts:
                    if post["id"] == id:
                        print('test4')
                        break
                else:
                    return
                if photo_id:
                    bot.send_photo(target_chat_id, photo_id, caption=text_spam,parse_mode="HTML")
                else:
                    bot.send_message(target_chat_id, text_spam,parse_mode="HTML")
            post_time = post_time + timedelta(hours=time_delta)

        except Exception as e:
            print(e)
            bot.send_message(chat_id, "Произошла ошибка")
    print('While worked!')
@bot.message_handler(commands=['start'])
def start_message(message):
    if message.chat.type == "private" and message.chat.id in superadmins:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Запланировать пост")
        btn2 = types.KeyboardButton("Отменить пост")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(message.chat.id,
                         '''Добро пожаловать!''', reply_markup=markup)
@bot.message_handler(content_types=['text'])
def func(message):
    now = datetime.now()
    if message.chat.type == "private" and message.chat.id in superadmins:
        '''with open("posts.json", "r") as read_file:
            scheduled_posts = json.load(read_file)'''
        if message.text == "Запланировать пост":
            handle_schedule(message)
        if message.text == "Отменить пост":
            for post in scheduled_posts:
                if now>=post['time_end']:
                    scheduled_posts.remove(post)
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            for post in scheduled_posts:
                print(post)
                time_post= datetime.strptime(f"{post['time']}", '%Y-%m-%d %H:%M:%S')
                if time_post.minute < 10:
                    markup.add(types.InlineKeyboardButton(
                            text=f'Пост от {time_post.day}.{time_post.month} {time_post.hour}:0{time_post.minute}',
                            callback_data=f'post_{post["id"]}'))
                else:
                    markup.add(types.InlineKeyboardButton(
                            text=f'Пост от {time_post.day}.{time_post.month} {time_post.hour}:{time_post.minute}',
                            callback_data=f'post_{post["id"]}'))
            bot.send_message(message.chat.id,
                             '''Список всех постов:''', reply_markup=markup)
@bot.callback_query_handler(func=lambda call: True)
def podcategors(call):
    '''with open("posts.json", "r") as read_file:
        scheduled_posts = json.load(read_file)'''
    if call.data[:5] == 'post_':
        id = call.data[5:]
        for post in scheduled_posts:
            if post['id'] != int(id):
                continue
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton(text=f'Удалить пост',
                                           callback_data=f'delete_post_{post["id"]}'))
            time_post = datetime.strptime(f"{post['time']}", '%Y-%m-%d %H:%M:%S')
            minute = time_post.minute
            if minute < 10:
                minute = f"0{minute}"
            if post["photo"]:
                bot.send_photo(call.message.chat.id,
                               caption=f'''Пост от {time_post.day}.{time_post.month} {time_post.hour}:{minute}
Пост будет повторяться через {post['time_delta']}
Автопост заканчивается в  {post['time_end']}
Текст поста: {post["text"]}''', reply_markup=markup, photo=post['photo'])
            else:
                bot.send_message(call.message.chat.id,
                                 f'''Пост от {time_post.day}.{time_post.month} {time_post.hour}:{minute}
Пост будет повторяться через {post['time_delta']}
Автопост заканчивается в  {post['time_end']}
Текст поста: {post["text"]}''', reply_markup=markup)
    if call.data[:5] == 'page_':
        page = call.data[5:]
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        for i in range(10):
            i = i + (int(page)-1)*10
            time_post = scheduled_posts[i]['time']
            if i != len(scheduled_posts)-1:
                if time_post.minute < 10:
                    markup.add(types.InlineKeyboardButton(
                        text=f'Пост от {time_post.day}.{time_post.month} {time_post.hour}:0{time_post.minute}',
                        callback_data=f'post_{scheduled_posts[i]["id"]}'))
                else:
                    markup.add(types.InlineKeyboardButton(
                        text=f'Пост от {time_post.day}.{time_post.month} {time_post.hour}:{time_post.minute}',
                        callback_data=f'post_{scheduled_posts[i]["id"]}'))
            else:
                break
        amount_of_pages = len(scheduled_posts) // 10
        if len(scheduled_posts) % 10 != 0:
            amount_of_pages = amount_of_pages + 1
        if amount_of_pages != page and page != 1:
            markup.add(types.InlineKeyboardButton(
            types.InlineKeyboardButton(
                text=f'◀️️',
                callback_data=f'page_{page - 1}'),
                text=f'1/{amount_of_pages}',
                callback_data=f'nothing_to_do'), types.InlineKeyboardButton(
                text=f'▶️',
                callback_data=f'page_{page+1}'))
        elif amount_of_pages == page and page != 1:
            markup.add(types.InlineKeyboardButton(
                types.InlineKeyboardButton(
                    text=f'◀️️',
                    callback_data=f'page_{page - 1}'),
                text=f'1/{amount_of_pages}',
                callback_data=f'nothing_to_do'))
        elif amount_of_pages == page and page == 1:
            markup.add(types.InlineKeyboardButton(
                types.InlineKeyboardButton(
                text=f'1/{amount_of_pages}',
                callback_data=f'nothing_to_do')))
        elif amount_of_pages != page and page == 1:
            markup.add(types.InlineKeyboardButton(
                text=f'1/{amount_of_pages}',
                callback_data=f'nothing_to_do'), types.InlineKeyboardButton(
                text=f'▶️',
                callback_data=f'page_{page+1}'))
        bot.send_message(call.message.chat.id,
                     '''Список всех постов:''', reply_markup=markup)
    if call.data[:12] == 'delete_post_':
        id = call.data[12:]
        for post in scheduled_posts:
            if post['id'] != int(id):
                continue
            scheduled_posts.remove(post)
            bot.send_message(call.message.chat.id,
                             f'''Пост успешно удален!''')

@bot.message_handler(commands=['post'])
def handle_schedule(message):
    if message.chat.type == "private" and message.chat.id in superadmins:
        chat_id = message.chat.id
        handler_message = bot.send_message(chat_id, "Введите сообщение:\nПросто текст или текст с фото")
        bot.register_next_step_handler(handler_message, lambda msg: ask_for_text(msg, chat_id))
def ask_for_text(message, chat_id):
    photo_id = None
    try:
        text_spam = message.caption
        photo_id = message.photo[-1].file_id
        bot.send_message(chat_id, "Введите время для первой публикации:\nФормат: дд.мм 00:00")
        bot.register_next_step_handler(message, lambda msg: ask_for_time(msg, chat_id, text_spam, photo_id))
    except:
        text_spam = message.text
        bot.send_message(chat_id, "Введите время для первой публикации:\nФормат: дд.мм 00:00")
        bot.register_next_step_handler(message, lambda msg: ask_for_time(msg, chat_id, text_spam, photo_id))


def ask_for_time(message, chat_id, text,photo_id):
    try:
        year = datetime.now().year
        post_time = message.text
        post_time = datetime.strptime(f"{year}.{post_time}", '%Y.%d.%m %H:%M')
        bot.send_message(chat_id, "Введите через сколько часов будет опубликован следующий пост:")
        bot.register_next_step_handler(message, lambda msg: ask_for_time2(msg, chat_id, text, photo_id,post_time))
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "Произошла ошибка!")

def ask_for_time2(msg, chat_id, text,photo_id,post_time):
        time_delta = int(msg.text)
        bot.send_message(chat_id, "Введите время окончания публикаций:\nФормат: дд.мм 00:00")
        bot.register_next_step_handler(msg, lambda msg: ask_for_time3(msg, chat_id, text, photo_id,post_time,time_delta))
def ask_for_time3(message,chat_id, text_spam, photo_id,post_time,time_delta):
        year = datetime.now().year
        time_end_2 = message.text
        time_end = datetime.strptime(f"{year}.{time_end_2}", '%Y.%d.%m %H:%M')
        id = 0
        for i in scheduled_posts:
            if id < i['id']:
                id = i['id']
        id = id + 1
        last_post = {'text': text_spam, 'time': f"{post_time}", 'photo': photo_id, "id": id,
                     "chat_id": message.chat.id,"post_time":str(post_time),"time_delta":time_delta,"time_end":time_end_2}
        with open("posts.json", "w") as write_file:
            json.dump(last_post, write_file)
        send_post = schedule_message(last_post["chat_id"],last_post["text"],last_post["photo"],last_post["time"],last_post["time_delta"],last_post["time_end"],last_post["id"])
        scheduled_posts.append({'text': last_post['text'], 'time': datetime.strptime(f"{last_post['time']}", '%Y-%m-%d %H:%M:%S'),
                                'photo': last_post['photo'], "id": last_post['id'],
                                "time_delta": last_post['time_delta'], "time_end": time_end})
        bot.send_message(chat_id, "Пост успешно запланирован!")
        ioloop = asyncio.new_event_loop()
        tasks = [
            ioloop.create_task(send_post)]
        ioloop.run_until_complete(asyncio.wait(tasks))
        ioloop.close()
        with open("db.json", "r") as read_file:
            db = json.load(read_file)
        db.append({'text': text_spam, 'time': str(post_time), 'photo': photo_id, "id": id,"time_delta":time_delta,"time_end":time_end_2})
        with open("db.json", "w") as write_file:
            json.dump(db, write_file)



if __name__=='__main__':
    while True:
        try:
            load = load_db()
            load.send(None)
            bot.infinity_polling()
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
#bot.polling(non_stop=True, interval=0)