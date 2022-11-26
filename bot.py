import os
import random
import subprocess
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ContentType
from aiogram.utils.callback_data import CallbackData
import ffmpeg
from random import choice

from tokens import token
import pandas as pd
from datetime import datetime
from states import Help, Tech
from asyncio import create_task
import speech_recognition as speech_recog

bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
recog = speech_recog.Recognizer()

callback_numbers = CallbackData("fabnum", "action")


def problem(call):
    dic = {}
    with open('problems.txt', encoding='utf-8') as file:
        for word in file.readlines():
            word, problem_name = word.rstrip('\n').split(' = ')
            dic[problem_name] = word
    data = pd.read_csv("Analytics.csv")
    new_col = pd.DataFrame({'Problem': dic[call.data], 'Time': datetime.now()}, index=[0])
    data = pd.concat([data, new_col], axis=0, ignore_index=True)[['Problem', 'Time']]
    data.to_csv("Analytics.csv")


def get_keyword(file_text):
    with open(file_text, 'r', encoding='utf-8') as file:
        keyboard = types.InlineKeyboardMarkup()
        for word in file.readlines():
            word, problem_name = word.rstrip('\n').split(' = ')
            if word.lower() != 'еще':
                keyboard.add(types.InlineKeyboardButton(text=word, callback_data=problem_name))
            else:
                keyboard.add(types.InlineKeyboardButton(text=word, url=problem_name))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    return keyboard


@dp.message_handler(commands='start', state='*')
async def start(message: types.Message):
    keyboard = get_keyword('problems.txt')
    await message.answer("Привет, я помощник сервиса Wink. Если у вас возникли проблемы, можете спрашивать у меня. \n"
                         "Полную информацию вы можете узнать https://wink.ru/faq?selected=0",
                         reply_markup=keyboard)


@dp.callback_query_handler(text=['inst', 'reg', 'prom', 'sub'])
async def callbacks_inst(call: types.CallbackQuery):
    problem(call)
    keyboard = types.InlineKeyboardMarkup()
    for button in ['Android', 'IOS', 'AndroidTV', 'Apple TV', 'Smart TV Samsung', 'Smart TV LG']:
        keyboard.add(
            types.InlineKeyboardButton(text=button, callback_data=callback_numbers.new(action=f"{call.data}_{button}")))
    if call.data in ['reg', 'prom', 'sub']:
        keyboard.add(
            types.InlineKeyboardButton(text='Сайт', callback_data=callback_numbers.new(action=f"{call.data}_Сайт")))
        if call.data in ['prom', 'sub']:
            keyboard.add(
                types.InlineKeyboardButton(text='ТВ приставка Wink',
                                           callback_data=callback_numbers.new(action=f"{call.data}_ТВ приставка Wink")))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text("Можете подробнее рассказать о своей проблеме?", reply_markup=keyboard)


@dp.callback_query_handler(text=['pay'])
async def callbacks_pay(call: types.CallbackQuery):
    problem(call)
    keyboard = types.InlineKeyboardMarkup()
    for button in ['Способы оплаты Wink', 'Play Market', 'App Store']:
        keyboard.add(
            types.InlineKeyboardButton(text=button, callback_data=callback_numbers.new(action=f"{call.data}_{button}")))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text("Можете подробнее рассказать о своей проблеме?", reply_markup=keyboard)


@dp.callback_query_handler(text=['nas'])
async def callbacks_pay(call: types.CallbackQuery):
    problem(call)
    keyboard = types.InlineKeyboardMarkup()
    for i, button in enumerate(
            ['Настройка DNS на Android TV', 'Настройка DNS на Apple TV', 'Настройка DNS на Smart TV Samsung',
             'Настройка DNS на Smart TV LG', 'Настройка DNS на приставке Wink+',
             'Сброс настроек и сброс SmartHUB на Smart TV Samsung', 'Сброс настроек до заводских Smart TV LG',
             'Удаление Root прав']):
        keyboard.add(
            types.InlineKeyboardButton(text=button, callback_data=callback_numbers.new(action=f"{call.data}_{i}")))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text("Можете подробнее рассказать о своей проблеме?", reply_markup=keyboard)


@dp.callback_query_handler(text=['fun'])
async def callbacks_pay(call: types.CallbackQuery):
    problem(call)
    keyboard = types.InlineKeyboardMarkup()
    for i, button in enumerate(
            ['Screen Sharing', 'Управление просмотром', 'Мультискрин с приставкой Wink', 'Качество видео',
             'Загрузка фильмов и сериалов на мобильные устройства',
             'Изменение региона вещания вручную на сайте wink.ru']):
        keyboard.add(
            types.InlineKeyboardButton(text=button, callback_data=callback_numbers.new(action=f"{call.data}_{i}")))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text("Можете подробнее рассказать о своей проблеме?", reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"inst_{button}" for button in
                                                           ['Android', 'IOS', 'AndroidTV', 'Apple TV',
                                                            'Smart TV Samsung', 'Smart TV LG']]))
async def callbacks_inst_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {
        'Android': "1) Открой приложение Play Маркет \n"
                   "2) Введи в поисковой строке Wink и нажми на найденное приложение\n"
                   "3) Нажми кнопку Установить и Дождитесь установки",
        'IOS': "1) Открой приложение App Store \n "
               "2) Введи в поисковой строке Wink и нажми на найденное приложение\n"
               "3) Нажми кнопку Установить и Дождитесь установки",
        'AndroidTV': "1) Открой приложение Google Play Store \n "
                     "2) Введи в поисковой строке Wink и нажми на найденное приложение\n"
                     "3) Нажми кнопку Установить и Дождитесь установки",
        'Apple TV': "1) Открой приложение App Store \n "
                    "2) Введи в поисковой строке Wink и нажми на найденное приложение\n"
                    "3) Нажми кнопку Установить и Дождитесь установки",
        'Smart TV Samsung': "1) Войди на домашний экран телевизора, нажав кнопку на ПДУ с рисунком Дома\n"
                            "2) Открой приложение Samsung Apps \n "
                            "3) Введи в поисковой строке Wink и нажми на найденное приложение\n"
                            "4) Нажми кнопку Установить и Дождитесь установки",
        'Smart TV LG': "1) Нажми кнопку с изображением Дома на ПДУ и выбери LG Content Store в списке быстрого доступа\n"
                       "2) После запуска LG Content Store выбери Поисквверху экрана \n "
                       "3) В поисковой строке введи Winkи нажми Search (Поиск)\n"
                       "4) Нажми кнопку Установить и Дождитесь установки"}
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[callback_data['action'].split('_')[-1]]}. \nЕсли хотите узнать подробнее, пройдите по ссылке https://wink.ru/faq?selected=0",
        reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"reg_{button}" for button in
                                                           ['Android', 'IOS', 'AndroidTV', 'Apple TV',
                                                            'Smart TV Samsung', 'Smart TV LG', 'Сайт']]))
async def callbacks_reg_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {
        'Android': "1) Нажми кнопку Ещё\n"
                   "2) Нажми кнопку Войти или зарегистрироваться\n"
                   "3) Введи номер мобильного телефона и нажми Далее\n"
                   "4) Введи 4-значный код из SMS\n"
                   "5) Нажми кнопку Завершить в случае авторизации или Регистрация в случае регистрации",
        'IOS': '1) Нажми кнопку Ещё\n'
               '2) Выбери пункт Войти или зарегистрироваться\n'
               '3) Введи номер мобильного телефона и нажми Далее\n'
               '4) Введи 4-значный код из SMS\n'
               '5) Нажми кнопку Войти в случае авторизации или Регистрация в случае регистрации',
        'AndroidTV': '1) Выбери пункт Моё\n'
                     '2) Перейди стрелкой вниз из верхнего раздела (Моя коллекция, Управление подписками, Родительский контроль) в нижний раздел\n'
                     '3) Выбери пункт Вход или регистрация\n'
                     '4) Нажми кнопку Войти и введи номер телефона и нажми кнопку Далее\n'
                     '5) Введи 4-значный код из SMS\n'
                     '6) Проверка кода из SMS происходит автоматически и если код корректный, регистрация / авторизация завершается и выходит сообщение.\n'
                     '7) Нажми кнопку Далее',
        'Apple TV': '1) Открой раздел Моё и выбери пункт Войти или зарегистрироваться\n'
                    '2) Нажми на кнопку Войти по номеру телефона для авторизации или нажми на кнопку У меня нет аккаунта для регистрации\n'
                    '3) Введи номер телефона и нажми Готово\n'
                    '4) Введи 4-значный код из SMS и нажми кнопку Готово',
        'Smart TV Samsung': '1) Открой раздел Моё\n'
                            '2) Выбери пункт Войти или зарегистрироваться\n'
                            '3) Нажми на кнопку Войти по номеру телефона для авторизации или У меня нет аккаунта для регистрации\n'
                            '4) Для авторизации или регистрации введи номер телефона, нажми Далее\n'
                            '5) Введи код из смс и нажми Зарегистрироваться или Авторизоваться',
        'Smart TV LG': '1) Открой раздел Моё\n'
                       '2) Выбери пункт Войти или зарегистрироваться\n'
                       '3) Нажми на кнопку Войти по номеру телефона для авторизации или У меня нет аккаунта для регистрации\n'
                       '4) Для авторизации или регистрации введи номер телефона, нажми Далее\n'
                       '5) Введи код из смс и нажми Зарегистрироваться или Авторизоваться',
        'Сайт': '1) Нажми кнопку Вход | Регистрация\n'
                '2) Введи номер телефона и нажми кнопку Далее\n'
                '3) Введи 4-значный код из SMS и нажми кнопку Далее\n'
                '4) После успешного входа в учётную запись кнопка Вход | Регистрация поменяется на кнопку Моё'}
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[callback_data['action'].split('_')[-1]]}. \nЕсли хотите узнать подробнее, "
        f"пройдите по ссылке https://wink.ru/faq?selected=1",
        reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"prom_{button}" for button in
                                                           ['Android', 'IOS', 'AndroidTV', 'Apple TV',
                                                            'Smart TV Samsung', 'Smart TV LG', 'Сайт']]))
async def callbacks_prom_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    with open('prom.txt', 'r', encoding='utf-8') as file:
        for word in file.readlines():
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[callback_data['action'].split('_')[-1]]}. \nЕсли хотите узнать подробнее, "
        f"пройдите по ссылке https://wink.ru/faq?selected=2",
        reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"sub_{button}" for button in
                                                           ['Android', 'IOS', 'AndroidTV', 'Apple TV',
                                                            'Smart TV Samsung', 'Smart TV LG', 'Сайт']]))
async def callbacks_sub_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    with open('sub.txt', 'r', encoding='utf-8') as file:
        for word in file.readlines():
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[callback_data['action'].split('_')[-1]]}. \nЕсли хотите узнать подробнее, "
        f"пройдите по ссылке https://wink.ru/faq?selected=3",
        reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"nas_{button}" for button in
                                                           range(8)
                                                           ]))
async def callbacks_nas_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    names = {}
    with open('nas.txt', 'r', encoding='utf-8') as file:
        for i, word in enumerate(file.readlines()):
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
            names[i] = name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    print(names)
    await call.message.edit_text(
        f"{dic[names[int(callback_data['action'].split('_')[-1])]]}. \nЕсли хотите узнать подробнее,"
        f" пройдите по ссылке https://wink.ru/faq?selected=7",
        reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"fun_{button}" for button in
                                                           range(6)
                                                           ]))
async def callbacks_fun_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    names = {}
    with open('fun.txt', 'r', encoding='utf-8') as file:
        for i, word in enumerate(file.readlines()):
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
            names[i] = name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[names[int(callback_data['action'].split('_')[-1])]]}. \nЕсли хотите узнать подробнее,"
        f" пройдите по ссылке https://wink.ru/faq?selected=6",
        reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"pay_{button}" for button in
                                                           ['Способы оплаты Wink', 'Play Market', 'App Store']]))
async def callbacks_pay_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    with open('pay.txt', 'r', encoding='utf-8') as file:
        for word in file.readlines():
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[callback_data['action'].split('_')[-1]]}. \nЕсли хотите узнать подробнее, "
        f"пройдите по ссылке https://wink.ru/faq?selected=4",
        reply_markup=keyboard)


@dp.callback_query_handler(text=['cv'])
async def cv(call: types.CallbackQuery):
    problem(call)
    keyboard = types.InlineKeyboardMarkup()
    for name in ['Ростелеком', 'Теле2']:
        keyboard.add(
            types.InlineKeyboardButton(text=name,
                                       callback_data=callback_numbers.new(action=f"{call.data}_{name}")))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text("Вы пользуетесь Ростелекомом или Теле2?", reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"cv_{button}" for button in
                                                           ['Ростелеком', 'Теле2']]))
async def callbacks_cv(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    cal = call.data.split('_')[-1]
    if cal == 'Ростелеком':
        for i, button in enumerate(
                ['Кому доступна Опция Wink?', 'Что означает Опция Wink и что в нее входит?',
                 'В каких регионах доступна Акция?', 'Что я могу смотреть и как платить?',
                 'Как я могу оплатить за покупки платных Пакетов в приложении Wink при включенной Опции Wink?',
                 'Как я могу пополнять баланс лицевого счета?', 'Как я могу оформлять платные подписки?',
                 'Какие команды управления через USSD запросы?',
                 'Если у меня на счете Мобильной связи недостаточно денег для оплаты очередной подписки, что-то останется мне доступным?',
                 'Если у меня нет денег для оплаты подписок и опция будет заблокирована, что будет с номером Мобильной связи?',
                 'У меня уже установлено Приложение Wink и в нем оформлены платные подписки. Что будет с ним?']):
            keyboard.add(
                types.InlineKeyboardButton(text=button,
                                           callback_data=callback_numbers.new(action=f"cv_Ростелеком_{i}")))
    else:
        for i, button in enumerate(
                ['Что это за опция?', 'Как это работает?', 'Как подключить и как платить?', 'Как тарифицируется?',
                 'Особенности и ограничения']):
            keyboard.add(
                types.InlineKeyboardButton(text=button,
                                           callback_data=callback_numbers.new(action=f"cv_Теле2_{i}")))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    await call.message.edit_text("Можете подробнее рассказать о своей проблеме?", reply_markup=keyboard)


@dp.callback_query_handler(callback_numbers.filter(action=[f"cv_Ростелеком_{button}" for button in
                                                           range(11)]))
async def callbacks_roc_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    names = {}
    with open('cv_roc.txt', 'r', encoding='utf-8') as file:
        for i, word in enumerate(file.readlines()):
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
            names[i] = name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[names[int(callback_data['action'].split('_')[-1])]]}. \nЕсли хотите узнать подробнее,"
        f" пройдите по ссылке https://wink.ru/faq?selected=9")


@dp.callback_query_handler(callback_numbers.filter(action=[f"cv_Теле2_{button}" for button in
                                                           range(11)]))
async def callbacks_tele_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    names = {}
    with open('cv_tele2.txt', 'r', encoding='utf-8') as file:
        for i, word in enumerate(file.readlines()):
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
            names[i] = name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        f"{dic[names[int(callback_data['action'].split('_')[-1])]]}. \nЕсли хотите узнать подробнее, "
        f"пройдите по ссылке https://wink.ru/faq?selected=10",
        reply_markup=keyboard)


@dp.message_handler(state=Help.start_help)
async def help_start(message: types.Message, state: FSMContext):
    if message.text.lower().strip() in 'даконечноугуагапомогитесрочнопомощьверно':
        await create_task(start(message))
        await state.finish()
    elif message.text.lower().strip() in 'нетнеане':
        await message.answer("Хорошо, но если у вас появятся проблемы обязательно пишите")
        await state.finish()
    else:
        await message.answer("Не понял вас")


@dp.callback_query_handler(callback_numbers.filter(action=[f"pris_{button}" for button in
                                                           range(9)]))
async def callbacks_pris_finish(call: types.CallbackQuery, callback_data: dict):
    dic = {}
    names = {}
    with open('wink+.txt', 'r', encoding='utf-8') as file:
        for i, word in enumerate(file.readlines()):
            name, answer = word.rstrip('\n').split('$$$')
            answer = answer.replace('___', '\n')
            dic[name] = answer
            names[i] = name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    print(names)
    await call.message.edit_text(
        f"{dic[names[int(callback_data['action'].split('_')[-1])]]}. \nЕсли хотите узнать подробнее, "
        f"пройдите по ссылке https://wink.ru/faq?selected=14",
        reply_markup=keyboard)


@dp.callback_query_handler(text=['pris'])
async def callbacks_pris(call: types.CallbackQuery):
    problem(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    for i, button in enumerate(
            ['Смена размера шрифта', 'Сброс приставки Wink+ до заводских настроек',
             'Как установить приложение на Wink+', 'Центр уведомлений на Wink+', 'Активные приложения',
             'Режим ожидания', 'Автозапуск Wink', 'Как свернуть приложение', 'Диагностика сети']
    ):
        keyboard.add(
            types.InlineKeyboardButton(text=button, callback_data=callback_numbers.new(action=f"{call.data}_{i}")))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='end'))
    await call.message.edit_text("Можете подробнее рассказать о своей проблеме?", reply_markup=keyboard)


@dp.callback_query_handler(text=['end'])
async def end(call: types.CallbackQuery):
    with open('problems.txt', 'r', encoding='utf-8') as file:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
        for word in file.readlines():
            word, problem_name = word.rstrip('\n').split(' = ')
            if word.lower() != 'еще':
                keyboard.add(types.InlineKeyboardButton(text=word, callback_data=problem_name))
            else:
                keyboard.add(types.InlineKeyboardButton(text=word, url=problem_name))
    keyboard.add(types.InlineKeyboardButton(text='Написать в тех. поддержку', callback_data='tech'))
    await call.message.edit_text(
        'Уточните вашу проблему. \n Полную информацию вы можете узнать https://wink.ru/faq?selected=0',
        reply_markup=keyboard)


@dp.callback_query_handler(text=['tech'])
async def tech(call: types.CallbackQuery):
    await call.message.edit_text("Напишите о вашей проблеме")
    await Tech.answer.set()


@dp.message_handler(state=Tech.answer)
async def tech_answer(message: types.Message, state: FSMContext):
    buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(
        *[KeyboardButton(i) for i in ['Да', 'Нет']])
    await message.answer(
        "В ближайшее время с вами свяжется наша поддержка. Ожидайте. А пока не могли бы вы написать отзыв про нас?",
        reply_markup=buttons)
    await Tech.feedback.set()
    await state.update_data(answer=message.text.lower())


@dp.message_handler(state=Tech.feedback)
async def tech_feedback(message: types.Message, state: FSMContext):
    await bot.send_message(1000646952, f"Техническая проблема - {message.text.capitalize()}\n"
                           f"Пользователь - {message.from_user.username}")
    if message.text.lower() in 'даконечнодавайугуага':
        await Tech.result.set()
        await message.answer("Я рад, что вы согласились на мою просьбу, пожалуйста, напишите ваше мнение о нас")
    else:
        data = await state.get_data()
        new_col = pd.DataFrame(
            {'Id': message.from_user.id, 'Answer': data['answer'], 'Feedback': None, 'Time': datetime.now()}, index=[0])
        df = pd.read_csv('feedback.csv')
        df = pd.concat([df, new_col], axis=0, ignore_index=True)[['Id', 'Answer', 'Feedback', 'Time']]
        df.to_csv('feedback.csv')
        await message.answer('Спасибо за честный ответ')
        await state.finish()


@dp.message_handler(state=Tech.result)
async def tech_result(message: types.Message, state: FSMContext):
    await message.answer("Спасибо за ваш отзыв. Каждое ваше слово важно для нас")
    data = await state.get_data()
    new_col = pd.DataFrame(
        {'Id': message.from_user.id, 'Answer': data['answer'], 'Feedback': message.text.capitalize(),
         'Time': datetime.now()}, index=[0])
    df = pd.read_csv('feedback.csv')
    df = pd.concat([df, new_col], axis=0, ignore_index=True)[['Id', 'Answer', 'Feedback', 'Time']]
    df.to_csv('feedback.csv')
    await state.finish()


@dp.message_handler(content_types=[types.ContentType.VOICE, 'text'])
async def get_audio(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        if message.content_type == types.ContentType.VOICE:
            file_id = message.voice.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            file_on_disk = Path("", f"{file_id}.mp3")
            await bot.download_file(file_path, file_on_disk)
            subprocess.call(
                ['C:\\Users\\Zoizi\\PycharmProjects\\pythonProject4\\ffmpeg\\bin\\ffmpeg.exe', '-i', str(file_on_disk),
                 f"{file_id}.wav"])
            with speech_recog.AudioFile(f"{file_id}.wav") as source:
                audio_content = recog.record(source)
                text = recog.recognize_google(audio_content, language='ru')
            os.remove(file_on_disk)
            os.remove(f"{file_id}.wav")
        else:
            text = message.text
        text = ''.join([i for i in text if i.isalpha() or i == ' '])

        if text.lower() in ['помогите', 'мне нужна помощь', 'у меня проблема', 'помоги', 'срочно ответь', 'спаси',
                            'поддержи',
                            'позвать оператора'] or any([i in text.lower() for i in
                                                         ['помогите', 'мне нужна помощь', 'у меня проблема', 'помоги',
                                                          'срочно ответь', 'поддержи',
                                                          'позвать оператора']]):
            keyboard = get_keyword('problems.txt')
            await message.answer(
                f'Уточните вашу проблему. \n Полную информацию вы можете узнать https://wink.ru/faq?selected=0',
                reply_markup=keyboard)
            await state.update_data(action=0, error=0)
        elif text.lower() in ['привет', 'салам', 'здравствуйте', 'здрасте', 'здраствуй', 'здравсвуй'] or \
                any([i in text.lower() for i in
                     ['привет', 'салам', 'здравствуйте', 'здрасте', 'здраствуй', 'здравствуй']]):
            await message.answer(
                choice(["Здравствуйте", f'Привет, {message.from_user.first_name}', 'Приветик',
                        'Ой, привет', 'Давно не виделись']))
            await state.update_data(action=0, error=0)
        elif text.lower() in ['спасибо'] or \
                any([i in text.lower() for i in
                     ['спасибо']]):
            await message.answer(
                choice(["Рад помочь!", 'Всегда пожалуйста!', 'Не за что!', 'Всегда обращайтесь!']))
            await state.update_data(action=0, error=0)
        elif text.lower() in ['как дела', 'как ты', 'что нового', 'как настроение'] or \
                any([i in text.lower() for i in
                     ['как дела', 'как ты', 'что нового', 'как настроение']]):
            await message.answer(choice(["У меня все хорошо, чувствую себя замечательно. У вас как?",
                                         'Сейчас стало грустно, но думаю скоро станет лучше. Как ваше настроние',
                                         'Очень весело, у вас как?',
                                         "Сегодня я как обычно сидел дома, как обычно. У вас все в порядке?",
                                         'Чувствую себя прекрасно, надеюсь, вам так же хорошо, как и мне, так же?',
                                         'Хорошо, вы как?',
                                         'Ой, я рад, что вы поинтересовались, у меня все хорошо, как ваше настроение?']))
            await state.update_data(action=1, error=0)
        elif text.lower() in ['замечательно', 'хорошо', 'супер', 'классно', 'лучше всех', 'кайф', 'прекрасно', 'неплохо'] or \
                any([i in text.lower() for i in
                     ['замечательно', 'хорошо', 'супер', 'классно', 'лучше всех', 'кайф', 'прекрасно', 'неплохо']]) and data['action'] == 1:
            await message.answer(choice(['Рад за вас', 'Приятно слышать',
                                         'Надеюсь, что такое настроение останется у вас о конца этого дня',
                                         'Это прекрасно']))
            await state.update_data(action=0, error=0)
        elif text.lower() in ['плохо', 'мерзко', 'отвратительно', 'так себе', 'такое', 'не очень', 'могло быть лучше'] or \
                 any([i in text.lower() for i in
                      ['замечательно', 'хорошо', 'супер', 'классно', 'лучше всех', 'кайф', 'прекрасно']]) and data[
                     'action'] == 1:
            await message.answer(choice(['Может я смогу вам помочь?',
                                         'Печально, но не расстраивайтесь, посмотрите на фотографию котят,'
                                         ' и вам сразу станет лучше', 'Надеюсь, оно изменится',
                                         'Я с вами, мы справимся с вашим плохим настроением']))
            await state.update_data(action=0, error=0)
        elif text.lower() in ['что делаешь', 'делаешь'] or \
                 any([i in text.lower() for i in
                      ['что делаешь', 'делаешь']]):
            movies = ['1 + 1 == https://wink.ru/media_items/76303979', 'Волна == https://wink.ru/media_items/55097624',
                      'Звездные войны: Скайуокер. Восход 2019 == https://wink.ru/media_items/95181208',
                      'Зеленая книга == https://wink.ru/media_items/75532283',
                      'Гарри Поттер и Дары Смерти: Часть 2 == https://wink.ru/media_items/55005002',
                      'Бамблби 2018 == https://wink.ru/media_items/76504594']
            movie, url = choice(movies).split(' == ')
            await message.answer(choice(['Я общаюсь с самым лучшим человеком в этом мире',
                                         f'Пересматриваю {movie}. Если хотите посмотреть со мной, то перейдите по ссылке {url}',
                                         'Пока что я отдыхаю', 'На данный момент я ничего не делаю']))
            await state.update_data(action=0, error=0)
        elif text.lower() in ['да', 'нет'] and data['action'] == 2:
            await state.update_data(action=0, error=0)
            keyboard = get_keyword('problems.txt')
            await message.answer(
                f'Уточните вашу проблему. \n Полную информацию вы можете узнать https://wink.ru/faq?selected=0',
                reply_markup=keyboard)
        elif text.lower() in ['фильм', 'сериал', 'кино'] or any([i in text.lower() for i in
                     ['фильм', 'сериал', 'кино']]):
            movies = ['1 + 1 == https://wink.ru/media_items/76303979', 'Волна == https://wink.ru/media_items/55097624',
                      'Звездные войны: Скайуокер. Восход 2019 == https://wink.ru/media_items/95181208',
                      'Зеленая книга == https://wink.ru/media_items/75532283',
                      'Гарри Поттер и Дары Смерти: Часть 2 == https://wink.ru/media_items/55005002',
                      'Бамблби 2018 == https://wink.ru/media_items/76504594']
            movie, url = choice(movies).split(' == ')
            await message.answer(choice([f"Недавно сново пересматривал {movie}", f"Советую посмотреть {movie}",
                                         f"Посмотрите {movie}", f"{movie} - фильм, который должен увидеть каждый"]) + f'Можете посмотреть его по ссылке {url}')
            await state.update_data(action=0, error=0)
        else:
            await state.update_data(action=0, error=data['error'] + 1 if 'error' in list(data) else 1)
            if data['error'] + 1 > 3:
                buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(
                    *[KeyboardButton(i) for i in ['Да', 'Нет']])
                await message.answer("Извините, я вас не понял. Вам нужна помощь?", reply_markup=buttons)
                await state.update_data(action=2)
            else:
                await message.answer("Извините, но я не понял вас")
    except Exception:
        buttons = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(
            *[KeyboardButton(i) for i in ['Да', 'Нет']])
        await message.answer("Извините, я вас не понял. Вам нужна помощь?", reply_markup=buttons)
        await state.update_data(action=2)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
