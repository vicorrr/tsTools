from common_utils import make_request
import traceback

def coupons_search(userId, couponId, orderIds=None, lessonIds=None, cookies=None):
    try:
        if not userId or not couponId:
            return {'success': False, 'error': '用户ID和优惠券ID为必填项'}
        if not orderIds and not lessonIds:
            return {'success': False, 'error': '请填写订单ID或班课ID'}

        if orderIds:
            # 处理多个订单ID
            orderId_list = [oid.strip() for oid in orderIds.split(',') if oid.strip()]
            apiUrl = f"https://tutor.zhenguanyu.com/tutor-uc-tool/api/users/{userId}/coupons/{couponId}/order-no-match-tips?orderIds={','.join(orderId_list)}"
            print(apiUrl)
        else:
            # 处理多个班课ID
            lessonId_list = [lid.strip() for lid in lessonIds.split(',') if lid.strip()]
            apiUrl = f"https://tutor.zhenguanyu.com/tutor-uc-tool/api/users/{userId}/coupons/{couponId}/lesson-no-match-tips?lessonIds={','.join(lessonId_list)}"

        response = make_request(apiUrl, cookies)
        
        data = response.json()
        
        if response.status_code != 200 or not data.get('success'):
            return {
                'success': False,
                'error': data.get('message', '接口请求失败')
            }

        if data and data.get('success') == True:
            # 处理订单接口返回格式
            if orderIds:
                tips = []
                order_tips = data.get('data', {}).get('orderId2Tips', {})
                for order_id, tip_text in order_tips.items():
                    # 分割提示为多条
                    tips.extend([f"订单 {order_id}: {t.strip()}" 
                               for t in tip_text.split('。') if t.strip()])
            else:
                # 处理班课接口返回格式
                lesson_tips = data.get('data', {}).get('tips', '')
                tips = [t.strip() for t in lesson_tips.split('。') if t.strip()]

            return {
                'success': True,
                'userId': userId,
                'couponId': couponId,
                'orderIds': orderId_list if orderIds else None,
                'lessonIds': lessonId_list if lessonIds else None,
                'tips': tips,
            }
        else:
            return {'success': False, 'error': data.get('message', '未找到相关信息')}
    except Exception as e:
        print(f"查询优惠券信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return {'success': False, 'error': f'查询过程中发生错误: {str(e)}'}