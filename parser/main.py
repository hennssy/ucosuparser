import json
import config
import functions
from database import Database
from keyboards import Keyboard
from parses import Parse
from vk_api import VkApi

vk_session = VkApi(token = config.token)
vk = vk_session.get_api()
db = Database()

def event_handler(peer_id, cmid):
    payload = db.get_note(peer_id)['last_payload']
    
    if payload['type'] == 'date_menu':
        subtype = payload['subtype']

        if subtype == 'student':
            subtext = 'студента'
        elif subtype == 'teacher':
            subtext = 'преподавателя'
        elif subtype == 'auditory':
            subtext = 'аудитории'

        text = 'Хорошо, ты хочешь получить расписание для ' + subtext + ', теперь нужно выбрать дату. Ты можешь выбрать из предложенных мной' \
            ' или нажать "другая" и прислать мне её самостоятельно.'
        keyboard = Keyboard.init_date_menu(subtype)
        functions.edit_message(vk, peer_id, cmid, text, keyboard)

    elif payload['type'] == 'group_menu':
        if payload['date'] == 'chose_needed':
            functions.edit_message(vk, peer_id, cmid, 'Тебе не понравились предложенные даты :|\nТогда напиши /osu со своей датой!')
        else:
            keyboard = Keyboard.init_group_menu(peer_id)
            text = f'Окей, ты выбрал дату {payload["date"]}. Теперь нужно выбрать группу.'
            functions.edit_message(vk, peer_id, cmid, text, keyboard)
           
    elif payload['type'] == 'teacher_menu':
        if payload['date'] == 'chose_needed':
            functions.edit_message(vk, peer_id, cmid, 'Тебе не понравились предложенные даты :|\nТогда напиши /osu со своей датой!')
        else:
            keyboard = Keyboard.init_teacher_menu(peer_id)
            text = f'Окей, ты выбрал дату {payload["date"]}. Теперь выбери преподавателя.'
            functions.edit_message(vk, peer_id, cmid, text, keyboard)

    elif payload['type'] == 'auditory_menu':
        if payload['date'] == 'chose_needed':
            functions.edit_message(vk, peer_id, cmid, 'Тебе не понравились предложенные даты :|\nТогда напиши /osu со своей датой!')
        else:
            keyboard = Keyboard.init_auditory_menu(peer_id)
            text = f'Окей, ты выбрал дату {payload["date"]}. Теперь выбери номер аудитории.'
            functions.edit_message(vk, peer_id, cmid, text, keyboard)

    elif payload['type'] == 'pre_result_menu':
        if 'group' in payload:
            if payload['group'] == 'chose_needed':
                functions.edit_message(vk, peer_id, cmid, 'Тебе не понравились предложенные группы? Ну и ладно, напиши /osu с нужным номером :|')
            else:
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {}, groups = payload['group'])
                Parse.group_parse(vk, peer_id, cmid, payload['date'], payload['group'])

        elif 'teacher' in payload:
            if payload['teacher'] == 'chose_needed':
                functions.edit_message(vk, peer_id, cmid, 'Тебе не понравились предложенные преподаватели! Два тебе, напиши /osu с фамилией преподавателя :|')
            else:
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {})
                Parse.teacher_parse(vk, peer_id, cmid, payload['date'], payload['teacher'].split()[0])

        elif 'auditory' in payload:
            if payload['auditory'] == 'chose_needed':
                functions.edit_message(vk, peer_id, cmid, 'Тебе не понравились предложенные мной аудитории? Напиши /osu с номером аудитории, или будешь на улице учиться :|')
            else:
                db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {})
                Parse.audit_parse(vk, peer_id, cmid, payload['date'], payload['auditory'])

    elif payload['type'] == 'links':
        keyboard = Keyboard.init_links_menu()
        functions.edit_message(vk, peer_id, cmid, 'В этом разделе ты можешь перейти на страничку автора бота или открыть инструкцию по его использованию :)', keyboard)
        db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'links'})

    elif payload['type'] == 'main_menu':
        keyboard = Keyboard.init_main_menu()
        functions.edit_message(vk, peer_id, cmid, 'Привет, я занимаюсь воровством расписания с сайта колледжа :>\nКакое расписание ты хочешь?', keyboard)
        db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'main_menu'})

def handle_process_event(event, context):
    vk_request = json.loads(json.loads(event['messages'][0]['details']['message']['body'])['text']['body'])
    print(vk_request)

    if 'parserosu' in vk_request['secret']:
        if vk_request['type'] == 'message_new':
            message_text = vk_request['object']['message']['text'].split()
            peer_id = vk_request['object']['message']['peer_id']
            
            if 'action' in vk_request['object']['message']:
                if vk_request['object']['message']['action']['type'] == 'chat_invite_user' and str(vk_request['object']['message']['action']['member_id']) == '-215604995':
                    functions.send_message(vk, peer_id, 'Привет! Для моей корректной работы нужно выдать мне права администратора, а чтобы открыть мое меню отправь команду /osu')
                    return
            
            if len(message_text) == 0:
                return
            
            elif len(message_text) == 1:
                if message_text[0] == '/osu' or '@ucosuraspisanie' in message_text[0]:
                    keyboard = Keyboard.init_main_menu()
                    cmid = functions.send_message(vk, peer_id, 'Привет, я занимаюсь воровством расписания с сайта колледжа :>\nКакое расписание ты хочешь?', keyboard)
                    
                    try:
                        response = db.get_note(peer_id)
                    except:
                        db.create_note(chat_id = peer_id, start = True)
                    
                    db.create_note(chat_id = peer_id, last_cmid = cmid, last_payload = {'type': 'main_menu'})

            elif len(message_text) == 2:
                if message_text[0] == '/osu' or '@ucosuraspisanie' in message_text[0]:
                    response = db.get_note(peer_id)

                    if str(message_text[1]).isdigit():
                        db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': response['last_payload']['date'], 'auditory': str(message_text[1])})
                        event_handler(peer_id, response['last_cmid'])

                    elif str(message_text[1]).isalpha():
                        db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': response['last_payload']['date'], 'teacher': str(message_text[1]).upper()})
                        event_handler(peer_id, response['last_cmid'])

                    else:
                        if message_text[1].count('-') + message_text[1].count('/') + message_text[1].count('.') == 2:
                            if message_text[1].count('-') == 2:
                                for elem in message_text[1].split('-'):
                                    if not elem.isdigit():
                                        db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': response['last_payload']['date'], 'group': str(message_text[1]).upper()})
                                        event_handler(peer_id, response['last_cmid'])
                                        return
                                
                                date = functions.date_check(message_text[1])

                                if date:
                                    db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': date})
                                    event_handler(peer_id, response['last_cmid'])
                                else:
                                    functions.edit_message(vk, peer_id, response['last_cmid'], 'Ты ввёл неправильную дату :(')
                            else:
                                date = functions.date_check(message_text[1])
                                
                                if date:
                                    db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': date})
                                    event_handler(peer_id, response['last_cmid'])
                                else:
                                    functions.edit_message(vk, peer_id, response['last_cmid'], 'Ты ввёл неправильную дату :(')
                        elif message_text[1].count('-') == 1:
                            db.create_note(chat_id = peer_id, last_payload = {'type': response['last_payload']['type'], 'date': response['last_payload']['date'], 'group': str(message_text[1]).upper()})
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
