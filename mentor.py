# 按展示部门路径，查找上级
from os import name
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

def get_department(id, cookies):
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-hermes-gateway/api/department/{id}"
        response = make_request(url, cookies)
        if response.status_code != 200:
            raise Exception(f"获取部门信息失败: HTTP {response.status_code}")
        department_data = response.json()
        absolutePath = department_data.get('absolutePath','')
        manager = department_data.get('manager','')
        department = {
            'manager': manager,
            'absolutePath': absolutePath
        }
        return department
    except Exception as e:
        print(f"获取部门信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        raise


def get_mentor_info(ldap, cookies):
    """获取上级信息"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-hermes-gateway/api/staffs/info/{ldap}"
        # print("获取上级接口：", url)

        response = make_request(url, cookies)

        if response.status_code != 200:
            raise Exception(f"获取上级信息失败: HTTP {response.status_code}")

        mentor_data = response.json()
        mentor_info = {
            'positionLevels': mentor_data.get('positionLevels',[]),
            'mentor_ldap': mentor_data.get('directLeaderLdap',''),
            'mentor_path': mentor_data.get('displayAbsolutePath','')
        }
        return mentor_info
    except Exception as e:
        print(f"获取+1信息时发生错误: {e}")
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
            teacher_info = get_teacher_info(ldap, cookies)
            print(f"教师信息获取成功: {teacher_info}")
        except Exception as e:
            print(f"获取教师信息失败: {e}")
            return {'success': False, 'error': f'获取教师信息失败: {str(e)}'}

        # 初始化响应数据
        response_data = {
            'success': True,
            'teacher_text': "",
            'mentor_text': "",
            'teacher_info': teacher_info,
            'lesson_info': None,
            'manager_info': None
        }

        # 构建基础显示文本
        teacher_text = "老师信息：\n"
        teacher_text += f"- 姓名：{teacher_info['name']}\n"
        teacher_text += f"- 电话：{teacher_info['phone']}\n"
        teacher_text += f"- LDAP：{ldap}\n\n"
        mentor_text = f"部门名称：{teacher_info['absolutePath']}\n\n"
        mentor_text += f"部门管理者：{teacher_info['managerLdap']}"

        
        if teacher_info['isGroup']:
            mentor_text += "（组长）"
        else:
            mentor_text += f"({mentor_1_info['positionLevels'][0].get('name','')})"
        
        departmentId = teacher_info['departmentId']
        department_info = get_department(departmentId, cookies)
        parent_department = department_info['absolutePath'][-2]
        print(f'上级部门ID:{parent_department}')
        parent_department_info = get_department(parent_department, cookies)
        parent_manager = parent_department_info['manager']["ldap"]
        print(f"+2信息获取成功: {parent_manager}")
        mentor_text += f"\n\n直属上级：{parent_manager}"
        parent_manager_info = get_mentor_info(parent_manager, cookies)
        print(f"+2信息: {parent_manager_info}")
        position_levels = parent_manager_info.get('positionLevels', [])
        level_name = position_levels[0].get('name', '') if position_levels else ''
        if level_name:
            mentor_text += f" ({level_name})\n\n"

        response_data['teacher_text'] = teacher_text
        response_data['mentor_text'] = mentor_text

        return response_data

    except Exception as e:
        print(f"查询过程中发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}