DEBUG = True
BCRYPT_LEVEL = 13
MAIL_FROM_EMAIL = "zq2640710087@gmail.com"
SECRET_KEY = "0102170333"
HOST = "0.0.0.0"
PORT = "50001"
SESSION_COOKIE_HTTPONLY = False
API = {
    'get_info': {
        'url': 'get_student_by_number',
        'payload': '{"number": "%s"}'
    },
    'get_act': {
        'url': 'get_activity_list_by_student',
        'payload': '{"student": "%s", "school": "%s", "college": "%s"}'
    },
    'enroll': {
        'url': 'enroll_activity_by_student',
        'payload': '{"activity": "%s","student": "%s"}'
    },
    'cancel': {
        'url': 'cancel_enroll_activity',
        'payload': '{"activity": "%s","student": "%s"}'
    },
    'get_act_detail': {
        'url': 'get_activity_details',
        'payload': '{"activity": "%s"}'
    },
    'get_act_info': {
        'url': 'get_activity',
        'payload': '{"_id": "%s"}'
    },
    'get_teacher': {
        'url': 'get_teacher_by_id',
        'payload': '{"teacher": "%s"}'
    },
    'sign_act': {
        'url': '',
        'payload': '{"activity":"%s","student":"%s"}'
    }
}
