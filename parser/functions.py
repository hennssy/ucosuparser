from calendar import monthrange
from datetime import datetime, timedelta
from vk_api.utils import get_random_id

def date_check(date):
    date = date.replace('.', '-')
    date = date.replace(',', '-')
    date = date.replace('/', '-')
    dd = date.split('-')
    
    try:
        if len(dd) == 3:
            if int(dd[0]) > monthrange(int(dd[2]), int(dd[1]))[1] or len(dd[0]) > 2:
                raise Exception
            
            if int(dd[1]) > 12 or len(dd[1]) > 2:
                raise Exception
            
            if len(dd[2]) != 4:
                raise Exception
        else:
            raise Exception
    except Exception:
        return False
        
    return date

def return_date(date, offset):
    temp = datetime.strptime(date, '%d-%m-%Y')
    res = temp + timedelta(days = offset)
    day = f'0{res.day}' if res.day <= 9 else res.day
    month = f'0{res.month}' if res.month <= 9 else res.month
    year = res.year
    
    return f'{day}-{month}-{year}'

def send_message(vk, chat_id, text, keyboard = None):
    if keyboard != None:
        last_cmid = vk.messages.send(
            message = text,
            random_id = get_random_id(),
            peer_ids = [chat_id],
            keyboard = keyboard.get_keyboard(),
            v = '5.131'
        )
    else:
        last_cmid = vk.messages.send(
            message = text,
            random_id = get_random_id(),
            peer_ids = [chat_id],
            v = '5.131'
        )
    
    return last_cmid[0]['conversation_message_id']

def edit_message(vk, chat_id, cmid, text, keyboard = None, attachment = ''):
    if keyboard != None:
        vk.messages.edit(
            message = text,
            random_id = get_random_id(),
            peer_id = chat_id,
            keyboard = keyboard.get_keyboard(),
            conversation_message_id = cmid,
            attachment = attachment
        )
    else:
        vk.messages.edit(
            message = text,
            random_id = get_random_id(),
            peer_id = chat_id,
            conversation_message_id = cmid,
            attachment = attachment
        )
