import boto3
import os
from botocore.exceptions import ClientError

class Database():
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url = os.environ.get('USER_STORAGE_URL'),
            region_name = 'us-east-1',
            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        )

    def get_note(self, chat_id):
        table = self.dynamodb.Table('hennssyparserydb1')
        
        try:
            response_get = table.get_item(Key = {'peer_id': str(chat_id)})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response_get['Item']

    def create_note(self, chat_id, last_cmid = None, groups = None, teachers = None, auditories = None, last_payload = None, start = False):
        if not start:
            response = self.get_note(chat_id)
            saved_groups = response['groups']
            saved_teachers = response['teachers']
            saved_auditories = response['auditories']
            last_saved_cmid = response['last_cmid']
            
            if last_cmid != None:
                last_saved_cmid = int(last_cmid)
            
            if groups != None:
                if len(saved_groups) == 3:
                    if groups.upper() in saved_groups:
                        del saved_groups[saved_groups.index(groups)]
                    else:
                        del saved_groups[2]
                elif len(saved_groups) < 3:
                    if groups.upper() in saved_groups:
                        del saved_groups[saved_groups.index(groups)]
                saved_groups.insert(0, groups.upper())

            if teachers != None:
                if len(saved_teachers) == 3:
                    if teachers in saved_teachers:
                        del saved_teachers[saved_teachers.index(teachers)]
                    else:
                        del saved_teachers[2]
                elif len(saved_teachers) < 3:
                    if teachers in saved_teachers:
                        del saved_teachers[saved_teachers.index(teachers)]
                saved_teachers.insert(0, teachers)

            if auditories != None:
                if len(saved_auditories) == 3:
                    if auditories in saved_auditories:
                        del saved_auditories[saved_auditories.index(auditories)]
                    else:
                        del saved_auditories[2]
                elif len(saved_auditories) < 3:
                    if auditories in saved_auditories:
                        del saved_auditories[saved_auditories.index(auditories)]
                saved_auditories.insert(0, str(auditories))
        else:
            last_saved_cmid = 0
            saved_groups = []
            saved_teachers = []
            saved_auditories = []

        table = self.dynamodb.Table('hennssyparserydb1')
        response = table.put_item(
            Item = {
                'peer_id': str(chat_id),
                'last_cmid': int(last_saved_cmid),
                'groups': saved_groups,
                'teachers': saved_teachers,
                'auditories': saved_auditories,
                'last_payload': last_payload if last_payload != None else {}
            }
        )
        
        return response
