import requests
from requests.adapters import HTTPAdapter
from common_utils import make_request
import traceback


def get_saleStrategy(lessonid, cookies):
    """获取班课售卖策略"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-product-gateway/api/sale-strategies/{lessonid}/saleStrategy"
        print("获取售卖策略接口：", url)
        response = make_request(url, cookies)
        
        # 增加响应内容检查
        if not response.text.strip():
            print("接口返回空响应内容")
            return None
            
        response_data = response.json()  # 统一解析JSON

        userMatcherId_display = response.json().get('channelSaleStrategies', {})[0].get('userMatcherId', '')
        userMatcherId_display_include = response.json().get('channelSaleStrategies', {})[0].get('userMatcherIdInclude', '')
        userMatcherId_sale = response.json().get('channelSaleStrategies', {})[1].get('userMatcherId', '')
        userMatcherId_sale_include = response.json().get('channelSaleStrategies', {})[1].get('userMatcherIdInclude', '')

        return {
            'id': response_data.get('id'),
            'name': response_data.get('name'),
            'ldap': response.json().get('ldap'),
            'userMatcherId_display': userMatcherId_display,
            'userMatcherId_display_include': userMatcherId_display_include,
            'userMatcherId_sale': userMatcherId_sale,
            'userMatcherId_sale_include': userMatcherId_sale_include,
        }
    except requests.exceptions.JSONDecodeError as e:
        print(f"接口返回非JSON数据：{response.text[:200]}")  # 截取前200字符用于调试
        return None
    except Exception as e:
        print(f"获取售卖策略时发生错误: {str(e)}")
        return None

def match_user(user, userMatcherId, cookies):
    """查询用户群组是否匹配"""
    try:
        url = "https://tutor.zhenguanyu.com/tutor-user-group/admin/api/user-group/match-user-matcher-by-user"
        payload = {
            "user": user,
            "userMatcherId": userMatcherId
        }

        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie.get('domain', 'tutor.zhenguanyu.com'),
                path=cookie.get('path', '/')
            )

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://tutor.zhenguanyu.com',
            'Referer': 'https://tutor.zhenguanyu.com/',
            'Connection': 'keep-alive'
        }

        response = session.post(url, json=payload, headers=headers, timeout=10)

        match_info = response.json()
        # print(f"接口响应状态码: {response.status_code}")
        # print(f"接口响应内容: {match_info}")

        data = match_info.get('data') or {}
        # 在match_user函数中添加异常处理
        return {
            'success': True if response.status_code == 200 else False,
            'statusCode': response.status_code,
            'matched': data.get('matched', False),
            'reason': data.get('unMatchedReason', '')
        }
    except Exception as e:
        print(f"获取匹配用户群组时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        raise
    
def sale_to_User(lessonid, user, cookies):
    saleStrategy = get_saleStrategy(lessonid, cookies)
    if not saleStrategy:
        return {
            'success': False,
            'error': '未找到售卖策略'
        }
    else:
        userMatcherId_display = saleStrategy.get('userMatcherId_display')
        match_display = match_user(user, userMatcherId_display, cookies)
        if match_display['matched']:
            if saleStrategy['userMatcherId_display_include']:
                display_text = f'用户符合{userMatcherId_display}群组，对该用户可见'
            else:
                display_text = f'用户符合{userMatcherId_display}群组，对该用户不可见'
        else:
            if saleStrategy['userMatcherId_display_include']:
                display_text = f'用户不符合{userMatcherId_display}群组，对该用户不可见'
            else:
                display_text = f'用户不符合{userMatcherId_display}群组，对该用户可见'

        userMatcherId_sale = saleStrategy.get('userMatcherId_sale')
        match_sale = match_user(user, userMatcherId_sale, cookies)
        if match_sale['matched']:
            if saleStrategy['userMatcherId_sale_include']:
                sale_text = f'用户符合{userMatcherId_sale}群组，该用户可购买'
            else:
                sale_text = f'用户符合{userMatcherId_sale}群组，该用户不可购买' 
        else:
            if saleStrategy['userMatcherId_sale_include']:
                sale_text = f'用户不符合{userMatcherId_sale}群组，该用户不可购买'
            else:
                sale_text = f'用户不符合{userMatcherId_sale}群组，该用户可购买'

        # 在sale_to_User函数返回结构中
        return {
            'success': True,
            'saleStrategyId': saleStrategy.get('id', 'N/A'),
            'saleStrategyName': saleStrategy.get('name', '未命名策略'),
            'saleStrategyLdap': saleStrategy.get('ldap', '未知负责人'),
            'saleStrategy_display': saleStrategy.get('userMatcherId_display'),
            'saleStrategy_display_include': saleStrategy.get('userMatcherId_display_include'),
            'saleStrategy_sale': saleStrategy.get('userMatcherId_sale'),
            'saleStrategy_sale_include': saleStrategy.get('userMatcherId_sale_include'),
            'displayStatus': display_text,
            'saleStatus': sale_text,
            'displayReason': match_display.get('reason', '').replace('\n', '<br/>'),
            'saleReason': match_sale.get('reason', '').replace('\n', '<br/>')
        }


        


        
