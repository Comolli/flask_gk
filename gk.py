import requests as rq
from requests.exceptions import ConnectionError, ConnectTimeout
import json
import pymongo
from config import API
from random import randint


class GK:
    headers = '''
                Content-Type: application/json;charset=UTF-8
                Host: sign.mybofeng.com
                Origin: http://sign.mybofeng.com
                token: yibanwang
                User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3573.0 Safari/537.36
            '''

    headers = {k.strip(): v for k, v in map(lambda x: x.split(': '), headers.strip().split('\n'))}

    def __init__(self, student_num):
        self.stu_num = student_num
        self.student = None
        self.school = None
        self.college = None
        self.stu_info = None
        self.act_list = None

    @staticmethod
    def post(url, **payload):

        api = API
        response = None

        try:
            if '_raw' in payload:
                payload = payload['_raw']

            response = rq.post(f"https://sign.mybofeng.com/{ url }",
                               data=json.dumps(payload),
                               headers=GK.headers)

        except ConnectTimeout:
            print('连接超时！')
        except ConnectionError:
            print('连接错误！')
        try:
            return json.loads(response.text)
        except:
            return response.text if response is not None else None

    # @staticmethod
    # def get_teacher(name):
    #     client = pymongo.MongoClient(host='14.119.123.236', port=8080)
    #     db = client.test
    #     collection = db.teachers
    #     result = collection.find_one({'name': name})
    #     print(result)
    #     return result

    def get_info(self):
        rp = self.post('get_student_by_number', number=self.stu_num)

        if rp:
            stu_info = rp
            self.student = stu_info['_id']
            self.college = stu_info['college']['_id']
            self.school = stu_info['school']['_id']
            self.stu_info = stu_info
            return stu_info

    def info_success(self):
        if not (self.student and self.school and self.college):
            return False
        return True

    @staticmethod
    def get_act_info(act_id):
        rp = GK.post('get_activity', _id=act_id)

        return rp

    def get_act(self):
        if not self.info_success():
            print('student info is None')
            return None

        rp = self.post('get_activity_list_by_student',
                       student=self.student,
                       school=self.school,
                       college=self.college)
        if rp:
            act_info = rp
            self.act_list = act_info
            return act_info

    @staticmethod
    def get_teacher(id):
        return GK.post('get_teacher_by_id', teacher=id)

    @staticmethod
    def enroll(act_id, student):
        return GK.post('enroll_activity_by_student', activity=act_id, student=student)

    @staticmethod
    def cancel(act_id, student):
        return GK.post('cancel_enroll_activity', activity=act_id, student=student)

    @staticmethod
    def get_act_detail(act_id, student=None):
        if student:
            return GK.post('get_activity_detail', activity=act_id, student=student)
        return GK.post('get_activity_details', activity=act_id)

    @staticmethod
    def sign_activity(act_id, student=None):
        return GK.post('sign_in_activity', activity=act_id, student=student)

    @staticmethod
    def create_active(act_id, student):
        enrolled = GK.get_act_detail(act_id, student)
        if enrolled:
            return enrolled

        act_info = GK.get_act_info(act_id)[0]

        rs = GK.post('create_activity_detail',
                     _raw=[{"student": "%s" % student,
                            "value": act_info['value'],
                            "activity": "%s" % act_id}]
                     )
        return GK.get_act_detail(act_id, student)

    @staticmethod
    def get_enroll_list(student):
        return GK.post('get_enrolled_activities_by_student', student=student)

    @staticmethod
    def get_reward(student):
        return GK.post('get_rewards_by_student', student=student)

    @staticmethod
    def sign_in(student, sign_id):
        sign_info = {"student": student['_id'],"signIn": sign_id,"class": student['class']['_id'],"number": student['number']}

        return GK.post('signIn_opt', **sign_info)

    @staticmethod
    def sign_upload(filename, student, sign):

        url = 'https://sign.mybofeng.com/sign_file_opt'

        headers = {**GK.headers}
        headers.pop('Content-Type')

        data = {
            'signId': sign['_id'],
            'type': '1',
            'time': str(randint(40, 200)),
            'uuid': student['uuid']
        }

        file = {
            'file': (
                student['number'],
                open(filename, 'rb'),
                'text/png'
            )
        }

        result = rq.post(url, data=data, files=file, headers=headers)

        return result.text

    @staticmethod
    def sign_out_act(act_id, student):
        return GK.post('random_sign_activity', activity=act_id, student=student)

    @staticmethod
    def get_rewards_statics(cl):
        request_param = {'class': cl}
        return GK.post('get_rewards_statics_by_class', **request_param)

