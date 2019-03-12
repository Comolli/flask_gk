# -*- codeing: utf-8 -*-
from flask import Flask, Response, request, url_for, json, session, make_response, redirect, send_from_directory
from werkzeug.utils import secure_filename
from os import path
from flask import render_template
from dateutil import tz
from datetime import datetime
import re
from gk import GK

app = Flask(__name__)
app.config.from_object('config')


# app.config.from_pyfile('config.py')


@app.template_global('str2tstamp')
def str2tstamp(time_str):
    time_str = str2time(time_str)
    parse_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    now_time = datetime.now()
    r = True if datetime.timestamp(parse_time) > datetime.timestamp(now_time) else False
    return r


@app.template_filter('dict2json')
def dict2json(d):
    return json.dumps(d, ensure_ascii=False)


@app.template_filter('str2time')
def str2time(time_str):
    """
        格式化时间方法：
        strftime
        解析时间方法：
        strptime
    :param time_str:
    :return: format_time
    """
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Shanghai')

    utc = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone).strftime('%Y-%m-%d %H:%M')
    return central


def send(username):
    gk = GK(username)
    gk.get_info()
    gk.get_act()
    return gk


@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html', path=request.path), 404


@app.errorhandler(500)
@app.route('/server_error')
def server_error():
    return render_template('server_error.html', path=request.path), 500


@app.errorhandler(405)
def method_not_allow(error):
    return render_template('method_not_allow.html', path=request.path), 405


def before_request():
    require_logged = [
        '/',
        '/sign',
        '/logout',
        '/cancel',
        '/enroll',
        '/sign_act',
        '/enroll_act',
        '/sign_in',
        '/sign_out_act',
        '/reward'
    ]
    require_logged_re = '^(/\w*)'
    match_result = re.match(require_logged_re, request.path)
    if hasattr(match_result, 'groups'):
        if not session.get('logged', None) and match_result.groups()[0] in require_logged:
            return redirect(url_for('login'))


app.before_request(before_request)


##########################################################################


@app.route('/')
def index():
    # if not session.get('logged', None):
    #     return redirect(url_for('login'))
    gk = send(session['u_name'])
    if gk.info_success():
        return render_template("index.html", actList=gk.act_list[::-1])
    return render_template('server_error.html', path=request.path), 500


@app.route('/login', methods=['GET'])
def login():
    if session.get('logged', None) is None:
        session['logged'] = False
    return render_template('login.html')


@app.route('/auth', methods=['POST'])
def login_auth():
    u_name = request.form.get('username', None)
    u_passwd = request.form.get('passwd', None)
    if u_name and u_passwd:
        gk = send(u_name)
        if gk.info_success():
            password = gk.stu_info['password']
            print(password)
            if password == u_passwd:
                session['logged'] = True
                session['name'] = gk.stu_info['name']
                session['u_id'] = gk.stu_info['_id']
                session['u_name'] = gk.stu_info['number']
                session['stu_info'] = gk.stu_info
                return 'Success'
            return 'Error'
        return 'Connection Error'
    return 'Error'


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return 'logout success'


@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    if session.get('logged', None):
        act_id = request.data
        cd = GK.enroll(act_id.decode(), session['u_id'])
        return Response(cd)

    return '''{"Error": "未登录"}''', 200, {'Content-Type': 'text/html;charset=UTF-8'}


@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if session.get('logged', None):
        act_id = request.data
        cd = GK.cancel(act_id.decode(), session['u_id'])
        # cd = 'success'
        return Response(cd)
    return '''{"Error": "未登录"}''', 200, {'Content-Type': 'text/html;charset=UTF-8'}


@app.route('/activity/<act_id>', methods=['GET', 'POST'])
def act_detail(act_id):
    act_list = GK.get_act_detail(act_id)
    act_info = GK.get_act_info(act_id)

    return render_template('act_detail.html', act_list=enumerate(act_list), act_info=act_info)


@app.route('/query')
def query():
    return render_template('query.html')


@app.route('/query/teacher/<u_id>')
def query_teacher(u_id):
    return json.dumps(GK.get_teacher(u_id), ensure_ascii=False)


@app.route('/sign_act', methods=['POST'])
def sign_in_act():
    if not session.get('logged', None):
        return redirect('/login')
    act_id = request.data
    enrolled = GK.get_act_detail(act_id.decode(), session['u_id'])
    if enrolled:
        GK.sign_activity(act_id.decode(), session['u_id'])
        rs = GK.get_act_detail(act_id.decode(), session['u_id'])
        return json.dumps(rs, ensure_ascii=False, indent=4)
    return json.dumps({'error': True}, ensure_ascii=False, indent=4)


@app.route('/sign_out_act', methods=['POST'])
def sign_out_act():
    act_id = request.data
    enrolled = GK.get_act_detail(act_id.decode(), session['u_id'])
    if enrolled:
        GK.sign_out_act(act_id.decode(), session['u_id'])
        rs = GK.get_act_detail(act_id.decode(), session['u_id'])
        return json.dumps(rs, ensure_ascii=False, indent=4)
    return json.dumps({'error': True}, ensure_ascii=False, indent=4)


@app.route('/act_detail/<act>', methods=['POST', 'GET'])
def act_detail_stu(act):
    # if not session.get('logged', None):
    #     return redirect('/login')
    act_id = request.data
    rs = GK.get_act_detail(act, session['u_id'])
    return json.dumps(rs, ensure_ascii=False, indent=4)


@app.route('/student')
def get_enroll_list():
    # if not session.get('logged', None):
    #     return redirect('/login')
    rs = GK.get_enroll_list(session['u_id'])
    return json.dumps(rs, ensure_ascii=False, indent=4)


@app.route('/enroll_act', methods=['POST'])
def enroll_act():
    # if not session.get('logged', None):
    #     return redirect('/login')
    act_id = request.data
    print(act_id)
    rs = GK.create_active(act_id.decode(), session['u_id'])
    print(rs)
    return json.dumps(rs, ensure_ascii=False, indent=4)


@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    # if not session.get('logged', None):
    #     return redirect('/login')

    file = request.files['file']

    base_path = path.abspath(path.dirname(__file__))
    file_path = path.join(base_path, 'file')
    filename = path.join(file_path, secure_filename(file.filename))
    file.save(filename)
    sign_info = GK.post('get_signin_by_student_opt', student=session['u_id'])
    sign_result = GK.sign_in(session['stu_info'], sign_info['_id'])

    sign_upload_result = GK.sign_upload(filename, session['stu_info'], sign_info)

    result = {
        'upload': sign_upload_result.strip('"'),
        'signIn': sign_result
    }

    return Response(json.dumps(result, ensure_ascii=False))


@app.route('/sign')
def sign():
    # if not session.get('logged', None):
    #     return redirect('/login')

    result = GK.post('get_signin_by_student_opt', student=session['u_id'])
    photo_list = None
    if result:
        photo_list = GK.post('get_partication_by_schedule', schedule=result['schedule']['_id'])

    # result = None
    # photo_list = GK.post('get_partication_by_schedule', schedule='5c22f4b1dbd73973b64b45a7')
    return render_template('sign_in.html', result=result, photo_list=photo_list)


@app.route('/reward')
def reward():
    rs = GK.get_reward(session['u_id'])
    reward_class = GK.get_rewards_statics(session['stu_info']['class']['_id'])

    reward_user = list(filter(lambda reward: reward['_id'] == session['u_id'], reward_class))[0]
    filter_list = ['tech', 'health', 'political', 'art', 'creative', 'volunteer', 'synthese']
    reward_list = {i: int(v) for i, v in reward_user.items() if i in filter_list}
    reward_count = sum(reward_list.values())
    return render_template('reward.html', reward_list=rs, reward_user=reward_user, reward_count=reward_count)


@app.route('/file/<filename>')
def get_file(filename):
    return Response(open('./file/%s' % filename, 'rb').read(), mimetype='image/jpg')


if __name__ == '__main__':
    # webbrowser.open('http://127.0.0.1:5000')
    app.run(host='0.0.0.0', port=5001)
