import functions
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime
from database import Database

db = Database()

class Keyboard():
    def init_main_menu():
        keyboard = VkKeyboard(one_time = False, inline = True)
        keyboard.add_callback_button(label = 'Студент', color = VkKeyboardColor.PRIMARY, payload = {'type': 'date_menu', 'subtype': 'student'})
        keyboard.add_callback_button(label = 'Кабинет', color = VkKeyboardColor.PRIMARY, payload = {'type': 'date_menu', 'subtype': 'auditory'})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Преподаватель', color = VkKeyboardColor.PRIMARY, payload = {'type': 'date_menu', 'subtype': 'teacher'})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Ссылки', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'links'})
        
        return keyboard

    def init_links_menu():
        keyboard = VkKeyboard(one_time = False, inline = True)
        keyboard.add_callback_button(label = 'Автор', color = VkKeyboardColor.PRIMARY, payload = {'type': 'open_link', 'link': 'https://vk.com/pussydaddy'})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Инструкция', color = VkKeyboardColor.PRIMARY, payload = {'type': 'open_link', 'link': 'https://vk.com/@ucosuraspisanie-polzovanie-botom'})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'main_menu'})

        return keyboard

    def init_date_menu(subtype):
        keyboard = VkKeyboard(one_time = False, inline = True)
        offset = 0
        
        if datetime.now().weekday() != 0:
            date = functions.return_date(datetime.strftime(datetime.now(), '%d-%m-%Y'), -datetime.now().weekday())
        else:
            date = datetime.strftime(datetime.now(), '%d-%m-%Y')

        if subtype == 'student':
            subtext = 'group'
        elif subtype == 'teacher':
            subtext = 'teacher'
        elif subtype == 'auditory':
            subtext = 'auditory'

        if subtype in ['student', 'teacher']:
            for _ in range(3):
                keyboard.add_callback_button(label = functions.return_date(date, offset), color = VkKeyboardColor.PRIMARY, payload = {'type': f'{subtext}_menu', 'date': functions.return_date(date, offset)})
                keyboard.add_line()
                offset += 7

        elif subtype == 'auditory':
            for _ in range(3):
                keyboard.add_callback_button(label = functions.return_date(datetime.strftime(datetime.now(), '%d-%m-%Y'), offset), color = VkKeyboardColor.PRIMARY, payload = {'type': f'{subtext}_menu', 'date': functions.return_date(datetime.strftime(datetime.now(), '%d-%m-%Y'), offset)})
                keyboard.add_line()
                offset += 1

        keyboard.add_callback_button(label = 'Другая дата', color = VkKeyboardColor.PRIMARY, payload = {'type': f'{subtext}_menu', 'date': 'chose_needed'})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'main_menu'})

        return keyboard

    def init_group_menu(peer_id):
        keyboard = VkKeyboard(one_time = False, inline = True)
        response = db.get_note(peer_id)
        date = response['last_payload']['date']

        if len(response['groups']) == 0:
            keyboard.add_callback_button(label = 'Другая группа', color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'group': 'chose_needed', 'date': date})
            keyboard.add_line()
            keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'date_menu', 'subtype': 'student'})
            return keyboard

        for idx, group in enumerate(response['groups']):
            keyboard.add_callback_button(label = group, color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'group': group, 'date': date})
            keyboard.add_line()

            if idx == 2:
                break

        keyboard.add_callback_button(label = 'Другая группа', color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'group': 'chose_needed', 'date': date})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'date_menu', 'subtype': 'student'})
        
        return keyboard

    def init_teacher_menu(peer_id):
        keyboard = VkKeyboard(one_time = False, inline = True)
        response = db.get_note(peer_id)
        date = response['last_payload']['date']

        if len(response['teachers']) == 0:
            keyboard.add_callback_button(label = 'Другой преподаватель', color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'teacher': 'chose_needed', 'date': date})
            keyboard.add_line()
            keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'date_menu', 'subtype': 'teacher'})
            return keyboard

        for idx, teacher in enumerate(response['teachers']):
            keyboard.add_callback_button(label = teacher, color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'teacher': teacher, 'date': date})
            keyboard.add_line()

            if idx == 2:
                break

        keyboard.add_callback_button(label = 'Другой преподаватель', color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'teacher': 'chose_needed', 'date': date})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'date_menu', 'subtype': 'teacher'})

        return keyboard

    def init_auditory_menu(peer_id):
        keyboard = VkKeyboard(one_time = False, inline = True)
        response = db.get_note(peer_id)
        date = response['last_payload']['date']

        if len(response['auditories']) == 0:
            keyboard.add_callback_button(label = 'Другая аудитория', color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'auditory': 'chose_needed', 'date': date})
            keyboard.add_line()
            keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'date_menu', 'subtype': 'auditory'})
            return keyboard

        for auditory in response['auditories']:
            keyboard.add_callback_button(label = auditory, color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'auditory': str(auditory), 'date': date})
            keyboard.add_line()

        keyboard.add_callback_button(label = 'Другая аудитория', color = VkKeyboardColor.PRIMARY, payload = {'type': 'pre_result_menu', 'auditory': 'chose_needed', 'date': date})
        keyboard.add_line()
        keyboard.add_callback_button(label = 'Назад', color = VkKeyboardColor.NEGATIVE, payload = {'type': 'date_menu', 'subtype': 'auditory'})
        
        return keyboard
