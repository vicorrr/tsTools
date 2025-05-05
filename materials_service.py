from common_utils import make_request
import traceback

def search_materials(userId, orderId, cookies):
    try:
        if not userId or not orderId:
            return {'success': False, 'error': '请输入完整的用户ID和订单ID'}

        apiUrl = f"https://tutor.zhenguanyu.com/tutor-uc-tool/api/users/{userId}/orders/{orderId}/no-shipment-tips"
        response = make_request(apiUrl, cookies)

        if response.status_code != 200:
            raise Exception(f"HTTP错误，状态码: {response.status_code}")

        data = response.json()
        if data and data.get('success') == True:
            # 格式化返回数据
            formatted_data = {
                'success': True,
                'userId': data.get('data', {}).get('userId'),
                'orderId': data.get('data', {}).get('orderId'),
                'tips': list(data.get('data', {}).get('orderItemId2NoShipmentTips', {}).values()),
                'othersInfo': data.get('data', {}).get('othersInfo')
            }
            return formatted_data
        else:
            return {'success': False, 'error': data.get('message', '未找到相关随材信息')}
    except Exception as e:
        print(f"查询随材信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return {'success': False, 'error': f'查询过程中发生错误: {str(e)}'}