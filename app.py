from flask import Flask, render_template, request, jsonify
from mentor import mentor_search  
from coupons_service import coupons_search
from materials_service import search_materials
from baseExam_service import exam_search
from common_utils import get_cookies
from saleStrategy import sale_to_User
from restore_focus import re_focus  # 新增导入恢复逻辑函数

app = Flask(__name__, template_folder='templates')  # 新增模板文件夹配置

# 路由定义
@app.route('/')
def home_page():
    return render_template('home.html')
    
@app.route('/mentor')
def mentor_page():
    return render_template('mentor.html')

@app.route('/materials')
def materials_page():
    return render_template('materials.html')

@app.route('/coupons')
def coupons_page():
    return render_template('coupons.html')

@app.route('/baseExam')
def exam_page():
    return render_template('baseExam.html')

@app.route('/saleStrategy')
def exasaleStrategy_page():
    return render_template('saleStrategy.html')

@app.route('/search_mentor', methods=['POST'])
def search_mentor_route():
    try:
        cookies = get_cookies()  
        ldap = request.form.get('ldap').strip()
        if not ldap:
            return jsonify({'success': False, 'error': '请输入LDAP'}), 400
        result = mentor_search(ldap, cookies)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/search_materials', methods=['POST'])
def search_materials_route():
    try:
        cookies = get_cookies() 
        userId = request.form.get('userId').strip()
        orderId = request.form.get('orderId').strip()
        result = search_materials(userId, orderId, cookies)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search_coupons', methods=['POST'])
def search_coupons_route():
    try:
        cookies = get_cookies()
        userId = request.form.get('userId').strip()
        couponId = request.form.get('couponId').strip()
        orderIds = request.form.get('orderIds', '').strip()
        lessonIds = request.form.get('lessonIds', '').strip()
        
        result = coupons_search(
            userId=userId,
            couponId=couponId,
            orderIds=orderIds if orderIds else None,
            lessonIds=lessonIds if lessonIds else None,
            cookies=cookies
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search_exam', methods=['POST'])
def search_exam():
    try:
        cookies = get_cookies()  
        lessonId = request.form.get('lessonId').strip()
        if not lessonId:
            return jsonify({'success': False, 'error': '请输入班课ID'}), 400
        result = exam_search(lessonId, cookies)
        return jsonify(result) if isinstance(result, dict) else jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/saleStrategy', methods=['POST'])
def saleStrategy():
    try:
        cookies = get_cookies()
        lessonId = request.form.get('lessonId').strip()
        userid = request.form.get('userId').strip()
        result = sale_to_User(lessonId, userid, cookies)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 新增恢复班主任资格页面路由
@app.route('/restoreFocus')
def restore_focus_page():
    return render_template('restoreFocus.html')

# 新增恢复操作处理路由
@app.route('/restore_focus', methods=['POST'])
def handle_restore_focus():
    try:
        cookies = get_cookies()  # 获取登录态
        phone_numbers = request.form.get('phoneNumbers', '').split('\n')  
        phone_numbers = [phone.strip() for phone in phone_numbers if phone.strip()]  
        
        result = re_focus(phone_numbers, cookies)  
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)