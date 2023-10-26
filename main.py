import telebot
from datetime import datetime,timedelta
import time
from telebot import types
import json
from apscheduler.schedulers.background import BackgroundScheduler

global scheduled_posts
scheduled_posts = []
bot = telebot.TeleBot('6485397598:AAFhK43IdxrK6Dk3oTpruk-TFpNj2U9ULVk') # test token
sched = BackgroundScheduler()
superadmins = [919422317,1387957204,5016708080,810311297,6609142734]
main_chat_id = -1001922928792 # test chat
delta_time = 1
#sched.add_job(bot.send_photo,"interval",hours=delta_time,args=(chat_id,text_to_spam,caption,"HTML"))
def refresh():
    now = datetime.now()
    for job in sched.get_jobs():
        id = job.id
        for post in scheduled_posts:
            if str(post['id']) == id:
                if post['time_end']<now:
                    sched.remove_job(job_id=id)
def schedule_message(text_spam, photo_id,id):
    if photo_id != None:
        bot.send_photo(main_chat_id, photo_id,text_spam, parse_mode='HTML')
        sched.add_job(bot.send_photo, "interval", hours=delta_time, args=(main_chat_id, photo_id, text_spam, "HTML"),
                      id=str(id))
    else:
        bot.send_message(main_chat_id,text_spam,parse_mode='HTML')
        sched.add_job(bot.send_message, "interval", hours=delta_time, args=(main_chat_id, text_spam, "HTML"), id=str(id))
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
Текст поста: {post["text"]}''', reply_markup=markup, photo=post['photo'])
            else:
                bot.send_message(call.message.chat.id,
                                 f'''Пост от {time_post.day}.{time_post.month} {time_post.hour}:{minute}
Пост будет повторяться через {post['time_delta']}
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
            sched.remove_job(job_id=id)
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
        time_end_2 = message.text
        id = 0
        for i in scheduled_posts:
            if id < i['id']:
                id = i['id']
        id = id + 1
        last_post = {'text': text_spam, 'time': f"{post_time}", 'photo': photo_id, "id": id,
                     "chat_id": message.chat.id,"post_time":str(post_time),"time_delta":time_delta,"time_end":time_end_2}
        with open("posts.json", "w") as write_file:
            json.dump(last_post, write_file)
        sched.add_job(schedule_message, "date", run_date=post_time, args=(text_spam, photo_id,id))
        bot.send_message(chat_id, "Пост успешно запланирован!")
        with open("db.json", "r") as read_file:
            db = json.load(read_file)
        db.append({'text': text_spam, 'time': str(post_time), 'photo': photo_id, "id": id,"time_delta":time_delta,"time_end":time_end_2})
        with open("db.json", "w") as write_file:
            json.dump(db, write_file)
if __name__=='__main__':
    while True:
        try:
            with open("db.json", "r") as read_file:
                db = json.load(read_file)
            for post in db:
                scheduled_posts.append(post)
                next_time_post = datetime.strptime(post['time'], '%Y-%m-%d %H:%M:%S')
                while next_time_post<datetime.now():
                    next_time_post = next_time_post + timedelta(hours=post['time_delta'])
                sched.add_job(schedule_message, "date", run_date=next_time_post, args=(post["text"],post["photo"],post['id']))
            sched.add_job(refresh, "interval", hours=1)
            sched.start()
            bot.infinity_polling()
        except Exception as e:
            print(e)
            time.sleep(5)
            continue