from operator import truediv
from common_utils import make_request
import traceback

def get_teacher_info(phone, cookies):
    """获取老师信息"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-atm-user/api/teachers?&keyword={phone}"
        # print(f"请求URL: {url}")
        response = make_request(url, cookies)

        if response.status_code != 200:
            raise Exception(f"获取老师信息失败: HTTP {response.status_code}")

        teacher_data = response.json()
        teacher_list = teacher_data.get('list', [])
        
        if not teacher_list:
            raise ValueError(f"未找到手机号 {phone} 对应的老师信息")
        
        teacher_info = teacher_list[0]
        return {
            'id': teacher_info.get('id', ''),
            'status': teacher_info.get('status', ''),
            'nickname': teacher_info.get('nickname', ''),
            'ldap': teacher_info.get('ldap', '')  
        }
    except Exception as e:
        print(f"获取老师信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        raise

def restore_mentor_qualification(mentor_id, cookies):
    """恢复班主任资格"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-wb-poseidon/api/mentors/activation?mentorId={mentor_id}"
        print(f"恢复班主任资格接口：{url}")
        response = make_request(url, cookies, method='POST')  

        if response.status_code != 200:
            raise Exception(f"恢复失败: HTTP {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"恢复时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return None

def re_focus(phone_numbers, cookies):  
    try:
        result_text = []  
        print("\n=== 开始新的恢复流程 ===")

        if not phone_numbers:
            return {'success': False, 'error': '请输入手机号（每行一个）'}

        for phone_num in phone_numbers:
            # 手机号格式验证
            if not isinstance(phone_num, str) or not phone_num.isdigit() or len(phone_num) != 11:
                result_text.append(f"错误：{phone_num} 不是有效的手机号格式")
                continue

            print(f"处理手机号: {phone_num}")
            try:
                # 获取老师信息
                teacher_info = get_teacher_info(phone_num, cookies)
                result_text.append(f"{phone_num} 找到班主任信息：{teacher_info['ldap']}，{teacher_info['nickname']}")
                print(f"找到{phone_num}班主任信息：{teacher_info['ldap']}")

                # 状态检查
                if teacher_info['status'] == 'activated':
                    result_text.append(f"{phone_num} 已有班主任资格，无需恢复\n\n")
                    continue

                # LDAP检查
                if not teacher_info['ldap']:
                    result_text.append(f"{phone_num} 未找到对应的LDAP\n\n")
                    continue

                # 执行恢复操作
                restore_result = restore_mentor_qualification(teacher_info['id'], cookies)  
                if restore_result == 200:
                    result_text.append(f"{phone_num} 恢复班主任资格成功\n\n")
                else:
                    result_text.append(f"{phone_num} 恢复失败，操作返回状态码 {restore_result}\n\n")

            except Exception as e:
                result_text.append(f"{phone_num} 处理过程中发生错误 - {str(e)}")

        return {
            'success': True,
            'result': '\n'.join(result_text)
        }
    except Exception as e:
        print(f"整体流程发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return {'success': False, 'error': f"系统错误: {str(e)}"}

