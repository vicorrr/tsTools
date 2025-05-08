from common_utils import make_request
import traceback

def get_teacher_info(ldap, cookies):
    """获取教师信息"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-wb-poseidon/api/user-department-record/{ldap}"

        response = make_request(url, cookies)

        if response.status_code != 200:
            raise Exception(f"获取教师信息失败: HTTP {response.status_code}")

        teacher_data = response.json()
        department_info = teacher_data.get('userDepartmentInfo', {})
        # 处理部门路径拼接
        absolute_path = ' / '.join(department_info.get('absolutePath', []))

        return {
            'name': teacher_data.get('fullName', ''),
            'phone': teacher_data.get('mentorAccount', ''),
            'departmentId': teacher_data.get('userDepartmentInfo', {}).get('id', ''),
            'absolutePath': absolute_path,
            'managerLdap': teacher_data.get('userDepartmentInfo', {}).get('managerLdap', ''),
            'managerFullName': teacher_data.get('userDepartmentInfo', {}).get('managerFullName', ''),
            'isGroup': teacher_data.get('userDepartmentInfo', {}).get('group', False)
        }
    except Exception as e:
        print(f"获取老师信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        raise

def get_lesson_info(ldap, cookies):
    """获取带班信息"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-atm-lesson/api/teams?pageSize=100&page=0&filterPseudoLesson=true&mentorKeyword={ldap}"
        print("获取带班信息接口：", url)

        response = make_request(url, cookies)

        if response.status_code != 200:
            raise Exception(f"获取带班信息失败: HTTP {response.status_code}")

        lesson_data = response.json()
        if not lesson_data.get('list') or len(lesson_data['list']) == 0:
            raise Exception("未找到带班数据")

        lesson_result = lesson_data['list'][0]
        lesson_info = {
            'lessonId': lesson_result.get('lessonId', ''),
            'lessonName': lesson_result.get('name', ''),
            'managerLdap': lesson_result.get('managerLdap', '')
        }
        return lesson_info
    except Exception as e:
        print(f"获取带班信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return None

def get_manager_info(phone, lesson_id, cookies):
    """获取主管信息"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-wb-poseidon/api/list-templates/detail?phone={phone}&lessonId={lesson_id}&_focusVersion=11.2.48"
        print("主管接口：", url)
        response = make_request(url, cookies)

        if response.status_code != 200:
            print(f"API响应内容: {response.text}")
            raise Exception(f"获取主管信息失败: HTTP {response.status_code}")

        manager_data = response.json()
        if not manager_data or 'staffDepartmentInfo' not in manager_data:
            raise Exception("主管数据格式不正确")

        manager_info = {
            'competentManagerLdap': manager_data.get('staffDepartmentInfo', {}).get('competentManagerLdap', ''),
            'departmentPath': manager_data.get('staffDepartmentInfo', {}).get('displayPaths', [])
        }
        return manager_info
    except Exception as e:
        print(f"获取主管信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return None

def mentor_search(ldap, cookies):
    try:
        print("\n=== 开始新的查询 ===")
        if not ldap:
            return {'success': False, 'error': '请输入LDAP'}

        print(f"查询LDAP: {ldap}")

        try:
            # 获取教师信息
            print("正在获取教师信息...")
            teacher_info = get_teacher_info(ldap, cookies)
            print(f"教师信息获取成功: {teacher_info}")
        except Exception as e:
            print(f"获取教师信息失败: {e}")
            return {'success': False, 'error': f'获取教师信息失败: {str(e)}'}

        # 初始化响应数据
        response_data = {
            'success': True,
            'display_text': "",
            'teacher_info': teacher_info,
            'lesson_info': None,
            'manager_info': None
        }

        # 构建基础显示文本
        display_text = "老师信息：\n"
        display_text += f"- 姓名：{teacher_info['name']}\n"
        display_text += f"- 电话：{teacher_info['phone']}\n"
        display_text += f"- LDAP：{ldap}\n\n"
        display_text += f"部门名称：{teacher_info['absolutePath']}\n\n"
        display_text += f"部门管理者：{teacher_info['managerLdap']}\n\n"

        error_messages = []

        try:
            # 获取课程信息
            print("正在获取带班信息...")
            lesson_info = get_lesson_info(ldap, cookies)
            if lesson_info:
                print(f"带班信息获取成功: {lesson_info}")
                response_data['lesson_info'] = lesson_info
            else:
                error_messages.append("获取带班信息失败")
        except Exception as e:
            print(f"获取带班信息失败: {e}")
            error_messages.append(f'获取带班信息失败: {str(e)}')

        try:
            # 获取主管信息
            print("正在获取主管信息...")
            manager_info = get_manager_info(teacher_info['phone'], lesson_info['lessonId'] if lesson_info else '', cookies)
            if manager_info:
                print(f"主管信息获取成功: {manager_info}")
                response_data['manager_info'] = manager_info
                display_text += f"主管LDAP：{manager_info['competentManagerLdap']}\n"
            else:
                error_messages.append("获取主管信息失败")
        except Exception as e:
            print(f"获取主管信息失败: {e}")
            error_messages.append(f'获取主管信息失败: {str(e)}')

        if error_messages:
            display_text += "\n".join([f"⚠️ {msg}" for msg in error_messages])

        response_data['display_text'] = display_text

        print("查询完成，返回结果")
        return response_data

    except Exception as e:
        print(f"查询过程中发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}