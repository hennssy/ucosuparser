import json
import config
import functions
from database import Database
from keyboards import Keyboard
from parses import parse_handler
from vk_api import VkApi

vk_session = VkApi(token = config.token)
vk = vk_session.get_api()
db = Database()

def auto_parse():
    date = functions.return_today_date()
    peers = db.get_peers()                
    for chat in peers:
        parse_handler(vk, chat['peer_id'], 0, date, 'group', chat['group'], auto = True)   

def event_handler(peer_id, cmid):
    payload = db.get_note(peer_id)['last_payload']
    
    if payload['type'] == 'date_menu':
        subtype = payload['subtype']
        if subtype == 'student':
            subtext = 'группы'
        elif subtype == 'teacher':
            subtext = 'преподавателя'
        elif subtype == 'auditory':
            subtext = 'аудитории'

        text = 'Хорошо, вы хотите получить расписание для ' + subtext + ', теперь нужно выбрать дату. Вы можете выбрать из предложенных мной' \
            ' или нажать «Другая дата» и прислать мне её самостоятельно 🙂'
        keyboard = Keyboard.init_date_menu(subtype)
        functions.edit_message(vk, peer_id, cmid, text, keyboard)

    elif payload['type'] == 'group_menu':
        if payload['date'] == 'chose_needed':
            functions.edit_message(vk, peer_id, cmid, 'Не понравились предложенные даты? 😐\nТогда напишите «/osu {твоя дата}»!')
        else:
            keyboard = Keyboard.init_group_menu(peer_id)
            text = f'Окей, вы выбрали дату {payload["date"]}. Теперь нужно выбрать группу 🙂'
            functions.edit_message(vk, peer_id, cmid, text, keyboard)
           
    elif payload['type'] == 'teacher_menu':
        if payload['date'] == 'chose_needed':
            functions.edit_message(vk, peer_id, cmid, 'Не понравились предложенные даты? 😐\nТогда напишите «/osu {твоя дата}»!')
        else:
            keyboard = Keyboard.init_teacher_menu(peer_id)
            text = f'Окей, вы выбрали дату {payload["date"]}. Теперь выберите преподавателя 🙂'
            functions.edit_message(vk, peer_id, cmid, text, keyboard)

    elif payload['type'] == 'auditory_menu':
        if payload['date'] == 'chose_needed':
            functions.edit_message(vk, peer_id, cmid, 'Не понравились предложенные даты? 😐\nТогда напишите «/osu {твоя дата}»!')
        else:
            keyboard = Keyboard.init_auditory_menu(peer_id)
            text = f'Окей, вы выбрали дату {payload["date"]}. Теперь выберите номер аудитории 🙂'
            functions.edit_message(vk, peer_id, cmid, text, keyboard)

    elif payload['type'] == 'pre_result_menu':
        if 'group' in payload:
            if payload['group'] == 'chose_needed':
                functions.edit_message(vk, peer_id, cmid, 'Не понравились предложенные группы? Ну и ладно, напишите «/osu {номер группы}» 😐')
            else:
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': None})
                parse_handler(vk, peer_id, cmid, payload['date'], 'group', payload['group'])

        elif 'teacher' in payload:
            if payload['teacher'] == 'chose_needed':
                functions.edit_message(vk, peer_id, cmid, 'Не понравились предложенные преподаватели? Напишите «/osu {фамилия преподавателя}» 😐')
            else:
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': None})
                parse_handler(vk, peer_id, cmid, payload['date'], 'teacher', payload['teacher'].split()[0])

        elif 'auditory' in payload:
            if payload['auditory'] == 'chose_needed':
                functions.edit_message(vk, peer_id, cmid, 'Не понравились предложенные мной аудитории? Напишите «/osu {номер аудитории}» 😐')
            else:
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': None})
                parse_handler(vk, peer_id, cmid, payload['date'], 'auditory', payload['auditory'])

    elif payload['type'] == 'links':
        keyboard = Keyboard.init_links_menu()
        functions.edit_message(vk, peer_id, cmid, 'В этом разделе вы можете перейти на страничку автора бота или открыть инструкцию по его использованию 🙂', keyboard)
        db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'links'})

    elif payload['type'] == 'settings_menu':
        settings = db.get_note(peer_id)['settings']

        if payload.get('subtype') == None:
            keyboard = Keyboard.init_settings_menu(peer_id)
            functions.edit_message(vk, peer_id, cmid, 'Тут вы можете включить автоматическое расписание и закрепление для него (если бот находится в беседе). Автоматическое расписание будет присылаться в субботу в 8 часов вечера!', keyboard)
            db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'settings_menu'})

        elif payload.get('subtype') == 'swap_autopin':
            try:
                members = vk.messages.getConversationMembers(peer_id = peer_id)
            except:
                functions.send_message(vk, peer_id, 'Для того, чтобы закреплять сообщения, мне нужны права администратора!')
                return
            
            settings['AutoPin'] = True if not settings['AutoPin'] else False
            db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'settings_menu'}, settings = settings)
            event_handler(peer_id, cmid)            

        elif payload.get('subtype') == 'swap_autosend':
            if payload.get('group', False):
                settings['Group'] = payload['group']
                settings['AutoSend'] = True if not settings['AutoSend'] else False
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'settings_menu'}, settings = settings)
                keyboard = Keyboard.init_settings_menu(peer_id)
                functions.edit_message(vk, peer_id, cmid, f'Авторасписание успешно настроено для группы «{payload["group"]}»!', keyboard = keyboard)
                return
            
            if not settings['AutoSend']:
                keyboard = Keyboard.init_settings_menu(peer_id)
                functions.edit_message(vk, peer_id, cmid, 'Отлично, теперь пришлите мне номер группы для включения авторасписания - «/osu {номер группы}»!', keyboard = keyboard)
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'settings_menu', 'subtype': 'swap_autosend'})
                return
            else:
                settings['AutoSend'] = False
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'settings_menu'}, settings = settings)
                event_handler(peer_id, cmid)
                return

    elif payload['type'] == 'main_menu':
        keyboard = Keyboard.init_main_menu()
        functions.edit_message(vk, peer_id, cmid, 'Привет, я занимаюсь воровством расписания с сайта колледжа :>\nКакое расписание вы хотите?\n\nUpd. Авторасписание и настройки 🙂', keyboard)
        db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'main_menu'})

def handle_process_event(event, context):
    if 'TimerMessage' in event['messages'][0]['event_metadata']['event_type']:
        auto_parse()
        return
    
    vk_request = json.loads(json.loads(event['messages'][0]['details']['message']['body'])['text']['body'])
    #print(vk_request)

    if vk_request['type'] == 'message_new':
        message_text = vk_request['object']['message']['text'].split()[1:]
        peer_id = vk_request['object']['message']['peer_id']
            
        if 'action' in vk_request['object']['message']:
            functions.send_message(vk, peer_id, 'Привет! Для моей корректной работы необходимо выдать мне права администратора, а чтобы открыть мое меню отправьте команду «/osu»!')
            return

        elif not message_text:
            keyboard = Keyboard.init_main_menu()
            cmid = functions.send_message(vk, peer_id, 'Привет, я занимаюсь воровством расписания с сайта колледжа :>\nКакое расписание вы хотите?\n\nUpd. Авторасписание и настройки 🙂', keyboard)
                    
            try:
                response = db.get_note(peer_id)
            except:
                db.create_note(chat_id = peer_id, start = True)
                response = db.get_note(peer_id)

            if len(response) < 7:
                db.create_note(chat_id = peer_id, start = True)

                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'main_menu'})

        elif len(message_text) == 1:
            response = db.get_note(peer_id)
            group, teacher, auditory, date = [None] * 4

            if response['last_payload'].get('type', None) == None:
                return

            if message_text[0].isdigit():
                auditory = message_text[0]
            elif message_text[0].isalpha():
                teacher = message_text[0]
            else:
                if message_text[0].count('-') + message_text[0].count('/') + message_text[0].count('.') == 2:
                    if message_text[0].count('-') == 2:
                        for elem in message_text[0].split('-'):
                            if not elem.isdigit():
                                group = message_text[0].upper()   
                        
                        if group == None:        
                            date = functions.date_check(message_text[0])
                            if not date:
                                functions.edit_message(vk, peer_id, response['last_cmid'], 'Вы ввели неправильную дату 😔')
                                return
                elif message_text[0].count('-') == 1:
                    group = message_text[0].upper()
                    
            if auditory != None:
                db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': response['last_payload']['date'], 'auditory': auditory})
            if teacher != None:
                db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': response['last_payload']['date'], 'teacher': teacher})
            if group != None:
                if response['last_payload']['type'] == 'settings_menu' and response['last_payload']['subtype'] == 'swap_autosend':
                    db.create_note(chat_id = peer_id, last_payload = {'type': 'settings_menu', 'subtype': 'swap_autosend', 'group': group})
                else:
                    db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': response['last_payload']['date'], 'group': group})
            if date != None and date != False:
                db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': date})
            event_handler(peer_id, response['last_cmid'])

    elif vk_request['type'] == 'message_event':
        if vk_request['object']['payload']['type'] == 'open_link':
            vk.messages.sendMessageEventAnswer(
                event_id = vk_request['object']['event_id'],
                user_id = vk_request['object']['user_id'],
                peer_id = vk_request['object']['peer_id'],
                event_data = json.dumps(vk_request['object']['payload'])
            )
            return

        db.create_note(chat_id = vk_request['object']['peer_id'], last_cmid = vk_request['object']['conversation_message_id'], last_payload = vk_request['object']['payload'])
        event_handler(vk_request['object']['peer_id'], vk_request['object']['conversation_message_id'])
