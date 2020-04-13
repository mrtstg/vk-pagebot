# -*- coding: utf-8 -*-

# Импорт библиотек
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
import datetime
import time
import pytz
import random
import os


def reboot(is_trd_python):
    # функция перезагрузки бота
    # аругмент функции влияет на выбор команды для перезагрузки
    way = os.path.abspath(__file__)
    if is_trd_python != "-1":
        os.system("python " + way)
    else:
        os.system("python3 " + way)


def make_safe_string(string):
    # не позволяет писать ссылки, заменяет точки похожим символом
    return string.replace(".", " • ")


def begins_with(string, beginning):
    # начинается ли строка с какого-то набора символов
    if string.find(beginning) == 0:
        return True
    else:
        return False


def get_time():
    # возвращает время формата ДД.ММ.ГГ ЧЧ:ММ:СС (по МСК)
    # например, 01.01.01 13:37:00
    return datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Europe/Moscow')), "%d.%m.%Y %H:%M:%S")


def console_log(text, symbols_amount=30):
    # выводит данные в консоль с указанием времени и интервалом после
    print("[" + get_time() + "] " + text)
    print("-" * symbols_amount)


def give_words(text, start_index=1, end_index=None):
    # возвращает текст из слов, start_index - стартовый индекс сбора слов
    # в массиве слов(text.spilt()), end_index - конечный
    if end_index is None:
        return ' '.join(text.split(" ")[start_index::])
    else:
        return ' '.join(text.split(" ")[end_index::])


def send_msg(peer_id=None, domain=None, chat_id=None, text=None,
             sticker_id=None, user_id=None):
    vk.messages.send(
        user_id=user_id,
        random_id=random.randint(-2147483648, 2147483647),
        peer_id=peer_id,
        domain=domain,
        chat_id=chat_id,
        message=text,
        sticker_id=sticker_id,
    )


def message_log(text):
    if log_id != [0]:
        for i in log_id:
            send_msg(user_id=i, text=text)
            time.sleep(delay)


# получаем первичные параметры для запуска бота из файла config.txt(в той же папке, где и скрипт)
script_path = os.path.abspath(__file__).replace("main.py", "")
console_log("Получен путь к скрипту: " + script_path)
# считываем параметры
config_lines = open(script_path + "config.txt").readlines()
parameters_lines = [line[line.find("=") + 1:].replace("\n", "") for line in config_lines]
# обьявление базовых переменных, соединение с ВК
is_third_python, allowed_ids, allowed_chats, log_id, index, delay, cmd_prefix, cmd_eval, safe_eval, is_access_allowed \
    = "0", [0], [0], 0, 1, 1, "!", "/", "0", False
try:
    console_log("Начинаю получать параметры запуска...")
    is_third_python = parameters_lines[8]
    allowed_ids = [int(num) for num in parameters_lines[1].split(",")]
    allowed_chats = [int(num) for num in parameters_lines[2].split(",")]
    log_id = [int(num) for num in parameters_lines[3].split(",")]
    index = int(parameters_lines[4])
    delay = int(parameters_lines[5])
    cmd_prefix = parameters_lines[6]
    cmd_eval = parameters_lines[7]
    safe_eval = parameters_lines[9]
    vk_session = vk_api.VkApi(token=parameters_lines[0])
    long_poll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
except Exception as e:
    console_log("Во время подключения/получения параметров произошла ошибка: " + str(e))
    console_log("Произвожу попытку переподключения через 10 секунд...")
    time.sleep(10)
    reboot(is_third_python)


def main():
    try:
        for event in long_poll.listen():
            global delay, cmd_prefix, cmd_eval, safe_eval, is_access_allowed
            try:
                if event.type == VkEventType.MESSAGE_NEW:
                    if not event.from_group:
                        # определяем, будем ли отвечать человеку
                        is_access_allowed = True
                        if event.from_chat:
                            # если чат не среди разрешенных(и такие указаны вообще), то закрываем доступ
                            if event.chat_id not in allowed_chats and allowed_chats != [0]:
                                is_access_allowed = False
                                continue
                        # если пользователь не среди разрешенных и они указаны, то закрываем доступ
                        if event.user_id not in allowed_ids and allowed_ids != [0]:
                            is_access_allowed = False
                            continue
                        # если доступ есть, то
                        if is_access_allowed:
                            # получаем параметры события
                            message_text = event.text
                            # длина сообщения в словах(нужно для некоторых команд)
                            message_length = len(message_text.split())
                            # текст нижнего регистра
                            lower_text = event.text.lower()
                            # первое слово - команда
                            command = lower_text.split(" ")[0]
                            # peer_id для ответа
                            peer_id = event.peer_id
                            # шаблон префикса команды и индекса бота
                            cmd_with_index = cmd_prefix + str(index)

                            if command == cmd_prefix + "индекс" or command == cmd_with_index + "индекс":
                                # команда для отображения индекса
                                send_msg(peer_id=peer_id, text="Мой индекс: " + str(index))
                                time.sleep(delay)
                                log_txt = "*id" + str(event.user_id) + " вызвал команду 'индекс'"
                                console_log(log_txt)
                                message_log(log_txt)

                            if (command == cmd_prefix or command == cmd_with_index) and message_length > 1:
                                # команда для "повторения" сообщения
                                out_text = make_safe_string(give_words(message_text))
                                send_msg(peer_id=peer_id, text=out_text)
                                time.sleep(delay)
                                log_txt = "*id " + str(event.user_id) + " вызвал текст: " + out_text
                                if len(log_txt) > 3000:
                                    log_txt_parts = [log_txt[0:3000], log_txt[3000:]]
                                    for log_part in log_txt_parts:
                                        message_log(log_part)
                                else:
                                    message_log(log_txt)
                                console_log(log_txt)

                            if (command == cmd_eval or command == cmd_eval + str(index)) and message_length > 1:
                                # Выполнение запроса в eval, замер временени выполения и типа значения
                                out_text = ""
                                start_date = datetime.datetime.now()
                                request = give_words(message_text)
                                try:
                                    if safe_eval == '0':
                                        result = eval(request)
                                    else:
                                        result = eval(request, {'__builtins__': {}})
                                    result_type = str(type(result)).replace("<", "").replace(">", ""). \
                                        replace("class ", "").replace("'", "")
                                    out_text += "Результат: " + make_safe_string(str(result)) + "\n\n"
                                    out_text += "Тип: " + result_type + "\n\n"
                                except Exception as eval_error:
                                    out_text = "Ошибка: " + str(eval_error) + "\n\n"
                                    result = "Ошибка"
                                work_time = datetime.datetime.now() - start_date
                                out_text += "Общее время выполнения: " + str(work_time)
                                send_msg(peer_id=peer_id, text=out_text)
                                log_txt = "*id" + str(event.user_id) + " выполнил eval-запрос: " + \
                                          make_safe_string(request) + "\nРезультат: " + make_safe_string(str(result))
                                if len(log_txt) > 3000:
                                    log_txt_parts = [log_txt[0:3000], log_txt[3000:]]
                                    for log_part in log_txt_parts:
                                        message_log(log_part)
                                else:
                                    message_log(log_txt)
                                console_log(log_txt)

                            if (command == cmd_prefix + "задержка" or command == cmd_with_index + "задержка") and \
                                    message_length > 1:
                                # команда для смены задержки
                                # до этого пишем старую задержку
                                old_delay = str(delay)
                                # если второе слово - цифра, то
                                if message_text.split()[1].isdigit():
                                    delay = int(message_text.split[1])
                                    send_msg(peer_id=peer_id, text="Значение задержки изменено на " + str(delay))
                                    log_txt = "*id" + str(event.user_id) + " сменил или попытался изменить задержку. " \
                                              "Сейчас она равна " + str(delay) + "сек.\n" + \
                                              "Старая задержка - " + old_delay + " сек."
                                    message_log(log_txt)
                                    console_log(log_txt)
                                    # меняем конфиг
                                    config_lines[5] = 'delay=' + str(delay) + '\n'
                                    open('config.txt', 'w', encoding='utf-8').write(''.join(config_lines))
                                else:
                                    send_msg(peer_id=peer_id, text="Укажите числовое значение.")

                            if (command == cmd_prefix + "префикс" or command == cmd_with_index + "префикс") and \
                                    message_length > 1:
                                # меняем префикс обычных команд
                                old_prefix = cmd_prefix
                                config_lines[6] = "cmdprefix=" + lower_text.split()[1] + '\n'
                                cmd_prefix = lower_text.split()[1]
                                send_msg(peer_id=peer_id, text="Префикс изменен на " + cmd_prefix + "\n" +
                                         "Пример новой команды: '" + cmd_prefix + " [текст]'")
                                log_txt = "*id" + str(event.user_id) + " сменил префикс команды на " + cmd_prefix + \
                                          " с " + old_prefix
                                message_log(log_txt)
                                console_log(log_txt)
                                open('config.txt', 'w', encoding='utf-8').write(''.join(config_lines))

                            if (command == cmd_prefix + "евалпрефикс" or command == cmd_with_index + "евалпрефикс") and\
                                    message_length > 1:
                                # меняем eval-префикс
                                old_prefix = cmd_eval
                                config_lines[7] = "cmdeval=" + lower_text.split()[1] + "\n"
                                cmd_eval = lower_text.split()[1]
                                send_msg(peer_id=peer_id, text="Префикс eval изменен на " + cmd_eval +
                                         "\n Пример новой команды:'"
                                         + cmd_eval + " 1 + 1'.")
                                log_txt = '*id' + str(event.user_id) + " сменил префикс eval на " + cmd_eval + \
                                          " с " + old_prefix
                                message_log(log_txt)
                                console_log(log_txt)
                                open('config.txt', 'w', encoding='utf-8').write(''.join(config_lines))
            except Exception as message_error:
                console_log("Сообщение вызвало ошибку: " + str(event.text) + "\nОшибка: " + str(message_error))
                continue

    except Exception as vk_error:
        console_log("Ошибка: " + str(vk_error))
        reboot(is_third_python)


# сбор инфы и вывод конфига перед запуском
if __name__ == "__main__":
    params = "Бот запущен! Параметры: \n"
    if allowed_ids == [0]:
        params += "Бот открыт для всех.\n"
    else:
        params += "Айди тех, у кого есть доступ: " + str(allowed_ids) + "\n"
    if allowed_chats == [0]:
        params += "Бот работает во всех чатах.\n"
    else:
        params += "Айди чатов, где бот работает: " + str(allowed_chats) + "\n"
    if log_id == [0]:
        params += "Бот не отправляет никому логи.\n"
    else:
        params += "Бот отправляет логи в ЛС следующим людям: " + str(log_id) + ". " \
                  "Проследите, чтобы бот мог им писать.\n"
    params += "Задержка после сообщений: " + str(delay) + " сек.\n"
    params += "Индекс: " + str(index) + "\n"
    params += "Команда повторения ваших слов - " + cmd_prefix + " [после пишете что повторить]\n"
    params += "Команда выполенния запроса в eval - " + cmd_eval + " [после пишете, что выполнить, будьте осторожны]\n"
    params += "Примеры команд: '" + cmd_prefix + " Я повторяю за людьми. ';'" + cmd_eval + " 1 + 1'\n"
    params += "При перезапуске будет использована команда python"
    if is_third_python == "1":
        params += "3"
    if safe_eval == '0':
        params += "\nФункционал eval не ограничен."
    else:
        params += "\nФункционал eval ограничен."
    console_log(params)
    main()
