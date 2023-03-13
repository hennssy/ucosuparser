import requests
import functions
import json
from datetime import datetime
from bs4 import BeautifulSoup as bs
from database import Database
from requests_futures import sessions

db = Database()

class Parse():
    def group_parse(vk, peer_id, cmid, date, group):
        text = f'Расписание для группы {group}\n\n'
        week_day = datetime.strptime(date, '%d-%m-%Y')
        week_day = datetime.isoweekday(week_day)
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

        if week_day == 7:
            functions.edit_message(vk, peer_id, cmid, text = 'Это выходной, отдохни. Уже совсем бошка не варит :|')
            return

        for i in range(week_day, 7, 1):         
            date_response = requests.post('https://www.uc.osu.ru/back_parametr.php', data = {'type_id': '1', 'data': date})
            try:
                date_response_dict = json.loads(date_response.text)
            except:
                date = functions.return_date(date, 1)
                continue
            
            if date_response_dict:
                for key, value in date_response_dict.items():
                    if value.lower() == group.lower():
                        group_id = key
                        db.create_note(chat_id = peer_id, groups = value.upper())
                
                response = requests.post('https://www.uc.osu.ru/generate_data.php', data = {'type': '1', 'data': date, 'id': group_id})
                result = bs(response.text, 'lxml')
            
                if len(result) == 0:
                    continue
                    
                subjects = result.find_all('td')
                
                if len(subjects) == 2:
                    continue

                text += f'{date.split("-")[0]}.{date.split("-")[1]} {days[i-1]}\n\n'  
                for j in range(2, len(subjects), 4):
                    text += f'{subjects[j].text}: {subjects[j+1].text} | {subjects[j+2].text} | {subjects[j+3].text}\n'
                
                text += '\n'
                date = functions.return_date(date, 1)
        
        if len(text.split('\n')) == 3:
            functions.edit_message(vk, peer_id, cmid, 'Пар на сайте нет, проверь введенную группу, дату или сайт колледжа, возможно он немножко споткнулся :(')     
        else:
            functions.edit_message(vk, peer_id, cmid, text, attachment = 'photo-219074729_457239017')

    def teacher_parse(vk, peer_id, cmid, date, teacher):
        text = f'Расписание для преподавателя '
        week_day = datetime.strptime(date, '%d-%m-%Y')
        week_day = datetime.isoweekday(week_day)
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        flag = False
        teacher_flag = False
        pos = 0

        if week_day == 7:
            functions.edit_message(vk, peer_id, cmid, text = 'Это выходной, отдохни. Уже совсем бошка не варит :|')
            return

        for i in range(week_day, 7, 1):
            date_response = requests.post('https://www.uc.osu.ru/back_parametr.php', data = {'type_id': '2', 'data': date})
            try:
                date_response_dict = json.loads(date_response.text)
            except:
                date = functions.return_date(date, 1)
                continue
            
            teacher_name = ''
            teacher_for_flag = ''

            if date_response_dict:
                for key, value in date_response_dict.items():
                    if teacher.upper() in value.upper():
                        teacher_name = value
                        
                        if not teacher_flag:
                            if ' ' not in value:
                                for j in range(1, len(value)):
                                    if value[j].isupper():
                                        pos = j
                                        break

                                value = value[:pos] + ' ' + value[pos:]     

                            db.create_note(chat_id = peer_id, teachers = value)
                            teacher_flag = True
                            teacher_for_flag = value
                                    
                if teacher_name == '':
                    date = functions.return_date(date, 1)
                    continue
                    
                if not flag:
                    text += f'{teacher_for_flag}\n\n'
                    flag = True

                response = requests.post('https://www.uc.osu.ru/generate_data.php', data = {'type': '2', 'data': date, 'id': teacher_name})
                result = bs(response.text, 'lxml')
                text += f'{date.split("-")[0]}.{date.split("-")[1]} {days[i-1]}\n\n'  
                
                if len(result) == 0:
                    text += 'Расписания на данную дату нет, возможно ошибка\n'
                    continue
                    
                subjects = result.find_all('td')
                
                for j in range(0, len(subjects), 4):
                    text += f'{subjects[j].text}: {subjects[j+1].text} | {subjects[j+2].text} | {subjects[j+3].text}\n'
                
                text += '\n'
                date = functions.return_date(date, 1)

        if len(text.split('\n')) == 1:
            functions.edit_message(vk, peer_id, cmid, 'Пар на сайте нет, проверь введенную фамилию преподавателя, дату или сайт колледжа, возможно он немножко споткнулся :(')
        else:     
            functions.edit_message(vk, peer_id, cmid, text, attachment = 'photo-219074729_457239017')

    def audit_parse(vk, peer_id, cmid, date, audit):
        date_response = requests.post('https://www.uc.osu.ru/back_parametr.php', data = {'type_id': '1', 'data': date})
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        
        try:
            date_response_dict = json.loads(date_response.text)
        except:
            functions.edit_message(vk, peer_id, cmid, 'Пар на сайте нет, проверь введенные номер аудитории, дату или сайт колледжа, возможно он немножко споткнулся :(')
            return
        
        db.create_note(chat_id = peer_id, auditories = str(audit))
        session = sessions.FuturesSession(max_workers=5)
        futures = [session.post('https://www.uc.osu.ru/generate_data.php', data = {'type': '1', 'data': date, 'id': key}) for key, value in date_response_dict.items()]
        s = []

        for f in futures:
            res = bs(f.result().text, 'lxml')
            subjects = res.find_all('td')

            for j in range(2, len(subjects), 4):
                if subjects[j+2].text == str(audit):
                    s.append(f'{subjects[j].text}: {subjects[j+1].text} | {subjects[1].text} | {subjects[j+3].text}')

        max = 1
        flag = False

        if len(s) == 0:
            functions.edit_message(vk, peer_id, cmid, 'В данном кабинете нет занятий на данную дату!')
            return

        text = f'Расписание для аудитории {str(audit)}\n\n{date.split("-")[0]}.{date.split("-")[1]} {days[datetime.weekday(datetime.strptime(date, "%d-%m-%Y"))]}\n\n'

        for i in range(6):
            for _ in s:
                flag = False
                for __ in s:
                    if __[0] == str(max) and flag == False:
                        text += f'{max}: {__[3:]}\n'
                        flag = True
                    elif __[0] == str(max) and flag:
                        text += f'   {__[3:]}\n'
                max += 1

        functions.edit_message(vk, peer_id, cmid, text, attachment = 'photo-219074729_457239017')
