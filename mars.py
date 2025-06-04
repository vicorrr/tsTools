from common_utils import make_request

def get_app_url(id, cookies):
    """获取下载链接信息"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-planet/api/client-versions/?space=tutor&productId={id}"
        response = make_request(url, cookies)
        if response.status_code != 200:
            raise Exception(f"获取客户端信息失败: HTTP {response.status_code}")
        app_info = {
            'version': '',
            'url': '',
            'url64': ''
        }
        app_data = response.json()
        app_content = app_data.get('list', [])
        # 获取全量版本
        for item in app_content:
            if item.get('releaseState') == 'complete':
                app_info['version'] = item.get('current', '')  # ✅ 使用字符串键名
                app_info['url'] = item.get('url', '')
                app_info['url64'] = item.get('url64', '')
                break
        return app_info
    except Exception as e:
        print(f"获取客户端信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        raise

def get_app(cookies):
    # 猿辅导
    '''
    311		猿辅导 Android 版
    341		猿辅导 Android Pad 版
    301		猿辅导 iPhone 版
    331		猿辅导 iPad 版
    328	    猿辅导 Windows 版
    391	    猿辅导 Mac 版
    '''
    print("正在获取猿辅导客户端信息...")
    yfd_android = get_app_url(311, cookies)
    yfd_iphone = get_app_url(301, cookies)
    yfd_ipad = get_app_url(331, cookies)
    yfd_win = get_app_url(328, cookies)
    yfd_mac = get_app_url(391, cookies)

    # 素养课
    '''
    28000001    素养课 Android 版
    28000002    素养课 Android Pad 版
    28000003    素养课 iPhone 版
    28000004    素养课 iPad 版
    28000005	素养课 Mac 版
    28000006	素养课 win 版
    '''
    print("正在获取素养课客户端信息...")
    collie_android = get_app_url(28000001, cookies)
    collie_iphone = get_app_url(28000003, cookies)
    collie_ipad = get_app_url(28000004, cookies)
    collie_win = get_app_url(28000006, cookies)
    collie_mac = get_app_url(28000005, cookies)

    # 小猿优课
    '''
    37000001    小猿优课 Android 版
    37000002    小猿优课 Android Pad 版
    37000003	小猿优课 iPhone 版
    37000004	小猿优课 iPad 版
    37000005	小猿优课 Win 版
    37000006	小猿优课 Mac 版
    '''
    print("正在获取小猿优课客户端信息...")
    husky_android = get_app_url(37000001, cookies)
    husky_iphone = get_app_url(37000003, cookies)
    husky_ipad = get_app_url(37000004, cookies)
    husky_win = get_app_url(37000005, cookies)
    husky_mac = get_app_url(37000006, cookies)

    # 老师端
    '''
    316	小猿助手
    319 双设备
    332 老师端iPad
    3000007 老师端android
    344 跟课端
    '''
    print("正在获取老师客户端信息...")
    xyzs = get_app_url(316, cookies)
    ssb = get_app_url(319, cookies)
    teacher_ipad = get_app_url(332, cookies)
    teacher_android = get_app_url(3000007, cookies)
    genkeduan = get_app_url(344, cookies)

    # 管理员
    '''
    313 android
    303 ios
    343 win
    393 mac
    '''
    print("正在获取管理员客户端信息...")
    admin_android = get_app_url(313, cookies)
    admin_ios = get_app_url(303, cookies)
    admin_win = get_app_url(343, cookies)
    admin_mac = get_app_url(393, cookies)

    apps_info = {
        'success': True,
        'yfd_android': yfd_android,
        'yfd_iphone': yfd_iphone,
        'yfd_ipad': yfd_ipad,
        'yfd_win': yfd_win,
        'yfd_mac': yfd_mac,
        'collie_android': collie_android,      
        'collie_iphone': collie_iphone, 
        'collie_ipad': collie_ipad,
        'collie_win': collie_win,
        'collie_mac': collie_mac,
        'husky_android': husky_android,
        'husky_iphone': husky_iphone,
        'husky_ipad': husky_ipad,
        'husky_win': husky_win,
        'husky_mac': husky_mac,
        'xyzs': xyzs,
        'ssb': ssb,
        'teacher_ipad': teacher_ipad,
        'teacher_android': teacher_android,
        'genkeduan': genkeduan,
        'admin_android': admin_android,
        'admin_ios': admin_ios,
        'admin_win': admin_win,
        'admin_mac': admin_mac  
    }
    print("客户端信息获取完成")
    # print(apps_info)
    return apps_info
