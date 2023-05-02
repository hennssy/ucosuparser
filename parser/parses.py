import requests
import functions
import json
from datetime import datetime
from bs4 import BeautifulSoup as bs
from database import Database
from requests_futures import sessions

db = Database()

errors = ['ConnectionError', 'ExpValueError', 'WeekendError']

def parse_handler(vk, peer_id, cmid, date, type_, data, auto = False):
    if type_ == 'auditory':
        text, tail = auditory_parse(date, data)
        if text in errors:
            handle_errors_answer(vk, peer_id, text, auto, 'номер аудитории', cmid if not auto else False)
        else:
            functions.edit_message(vk, peer_id, cmid, text, attachment = 'photo-219074729_457239017')
            db.create_note(chat_id = peer_id, auditories = tail)
    elif type_ == 'group':
        text, tail = group_parse(date, data)
        if text in errors:
            handle_errors_answer(vk, peer_id, text, auto, 'номер группы', cmid if not auto else False)
        else:
            if auto:
                functions.send_message(vk, peer_id, text, attachment = 'photo-219074729_457239017', pin = db.get_note(peer_id)['settings']['AutoPin'])
            else:
                functions.edit_message(vk, peer_id, cmid, text, attachment = 'photo-219074729_457239017')
            db.create_note(chat_id = peer_id, groups = tail)
    elif type_ == 'teacher':
        text, tail = teacher_parse(date, data)
        if text in errors:
            handle_errors_answer(vk, peer_id, text, auto, 'фамилию преподавателя', cmid if not auto else False)
        else:
            functions.edit_message(vk, peer_id, cmid, text, attachment = 'photo-219074729_457239017')
            db.create_note(chat_id = peer_id, teachers = tail)
    
def handle_errors_answer(vk, peer_id, text, auto, type_, cmid):
    if auto:
        if text == 'ConnectionError':
            functions.send_message(vk, peer_id, 'Сайт сейчас не работает. Повторите попытку самостоятельно немного позже 😔')
        elif text == 'ExpValueError':
            functions.send_message(vk, peer_id, 'Я не нашел пар на сайте колледжа. Попробуйте еще раз вызвать проверку, или самостоятельно зайдите на сайт колледжа 😔')
    else:
        if text == 'ConnectionError':
            functions.edit_message(vk, peer_id, cmid, 'Сайт сейчас не работает. Повторите попытку позже 😔')
        elif text == 'ExpValueError':
            functions.edit_message(vk, peer_id, cmid, f'Пар на сайте нет. Проверьте выбранные дату и {type_} 🙂')
        elif text == 'WeekendError':
            functions.edit_message(vk, peer_id, cmid, 'Пар на сайте нет, так как указанный вами день - выходной. Проверьте введенную дату 🙂')

def get_response(url, data, js = False):
    try:
        response = requests.post(url, data = data, timeout = 5)
        if js:
            response_dict = json.loads(response.text)
    except requests.exceptions.Timeout:
        return 'ConnectionError'
    except json.decoder.JSONDecodeError:
        return 'ExpValueError'
    
    return response if not js else response_dict

days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
def group_parse(date, group):
    text = f'Расписание для группы {group}\n\n'

    week_day = datetime.weekday(datetime.strptime(date, '%d-%m-%Y'))
    if week_day == 6:
        return 'WeekendError', ''

    flag = False
    for i in range(week_day, 6, 1):
        response = get_response('https://www.uc.osu.ru/back_parametr.php', {'type_id': '1', 'data': date}, js = True)
        if response == 'ConnectionError':
            return response, ''
        elif response == 'ExpValueError':
            date = functions.return_date(date, 1)
            continue
        
        group_id = ''
        for key, value in response.items():
            if value.lower() == group.lower():
                group_id = key

                if not flag:
                    db_group_name = value.upper()
                    flag = True

        if group_id == '':
            functions.return_date(date, 1)
            continue

        lessons_response = get_response('https://www.uc.osu.ru/generate_data.php', {'type': '1', 'data': date, 'id': group_id})
        page = bs(lessons_response.text, 'lxml')
        if len(page) == 0:
            continue

        lessons = page.find_all('td')
        if len(lessons) == 2:
            continue

        text += f'{date.split("-")[0]}.{date.split("-")[1]} {days[i]}\n\n'
        for j in range(2, len(lessons), 4):
            text += f'{lessons[j].text}: {lessons[j+1].text} | {lessons[j+2].text} | {lessons[j+3].text}\n'
        text += '\n'

        date = functions.return_date(date, 1)

    if len(text.split('\n')) == 3:
        return 'ExpValueError', ''
    
    return text, db_group_name

def teacher_parse(date, teacher):
    text = 'Расписание для преподавателя '

    week_day = datetime.weekday(datetime.strptime(date, '%d-%m-%Y'))
    if week_day == 6:
        return 'WeekendError', ''
    
    flag = False
    for i in range(week_day, 6, 1):
        response = get_response('https://www.uc.osu.ru/back_parametr.php', {'type_id': '2', 'data': date}, js = True)
        if response == 'ConnectionError':
            return response, ''
        elif response == 'ExpValueError':
            date = functions.return_date(date, 1)
            continue
        
        teacher_name = ''
        for key, value in response.items():
            if teacher.lower() in value.lower():
                teacher_name = value

                if ' ' not in value and not flag:
                    pos = [j for j in range(1, len(value)) if value[j].isupper()][0]
                    db_teacher_name = value[:pos] + ' ' + value[pos:]
                    flag = True

                if not flag:
                    db_teacher_name = value
                    flag = True

        if teacher_name == '':
            date = functions.return_date(date, 1)
            continue

        if text == 'Расписание для преподавателя ':
            text += f'{db_teacher_name}\n\n'
        
        lessons_response = get_response('https://www.uc.osu.ru/generate_data.php', data = {'type': '2', 'data': date, 'id': teacher_name})
        page = bs(lessons_response.text, 'lxml')
        if len(page) == 0:
            continue

        lessons = page.find_all('td')
        if len(lessons) == 2:
            continue
        
        text += f'{date.split("-")[0]}.{date.split("-")[1]} {days[i]}\n\n'
        for j in range(0, len(lessons), 4):
            text += f'{lessons[j].text}: {lessons[j+1].text} | {lessons[j+2].text} | {lessons[j+3].text}\n'
        text += '\n'
        
        date = functions.return_date(date, 1)

    if len(text.split('\n')) == 1:
        return 'ExpValueError', ''

    return text, db_teacher_name

def auditory_parse(date, auditory):
    response = get_response('https://www.uc.osu.ru/back_parametr.php', {'type_id': '1', 'data': date}, js = True)
    if response in errors:
        return response, ''
    
    session = sessions.FuturesSession(max_workers = 5)
    pages = [session.post('https://www.uc.osu.ru/generate_data.php', data = {'type': '1', 'data': date, 'id': key}) for key, value in response.items()]
    lessons_list = []
    for page in pages:
        lessons_page = bs(page.result().text, 'lxml')
        lessons = lessons_page.find_all('td')
        for j in range(2, len(lessons), 4):
                if lessons[j+2].text == str(auditory):
                    lessons_list.append(f'{lessons[j].text}: {lessons[j+1].text} | {lessons[1].text} | {lessons[j+3].text}')

    if len(lessons_list) == 0:
        return 'ExpValueError', ''

    text = f'Расписание для аудитории {str(auditory)}\n\n{date.split("-")[0]}.{date.split("-")[1]} {days[datetime.weekday(datetime.strptime(date, "%d-%m-%Y"))]}\n\n'
    max_lesson_number = 1

    for i in range(6):
        flag = False
        for lesson in lessons_list:
            if lesson[0] == str(max_lesson_number) and not flag:
                text += f'{max_lesson_number}: {lesson[3:]}\n'
                flag = True
            elif lesson[0] == str(max_lesson_number) and flag:
                text += f'   {lesson[3:]}\n'
        max_lesson_number += 1 

    return text, str(auditory)
