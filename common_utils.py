from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json
import pickle
import os
import requests
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta


# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 登录信息存储文件
LOGIN_INFO_FILE = os.path.join(BASE_DIR, 'login_info.pkl')

def load_login_info():
    """加载保存的登录信息"""
    if os.path.exists(LOGIN_INFO_FILE):
        try:
            with open(LOGIN_INFO_FILE, 'rb') as f:
                login_info = pickle.load(f)
                # 检查登录信息是否过期（240小时）
                if datetime.now() - login_info['timestamp'] < timedelta(hours=240):
                    return login_info['cookies']
        except Exception as e:
            print(f"加载登录信息失败: {e}")
    return None

def save_login_info(cookies):
    """保存登录信息"""
    try:
        login_info = {
            'cookies': cookies,
            'timestamp': datetime.now()
        }
        with open(LOGIN_INFO_FILE, 'wb') as f:
            pickle.dump(login_info, f)
    except Exception as e:
        print(f"保存登录信息失败: {e}")

def setup_chrome_driver():
    """设置Chrome驱动"""
    try:
        print("正在设置 Chrome 驱动...")
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--log-level=3')

        chromedriver_path = os.path.join(BASE_DIR, 'chromedriver')
        # 检查 chromedriver 文件是否存在
        if not os.path.exists(chromedriver_path):
            raise FileNotFoundError(f"未找到 chromedriver 文件: {chromedriver_path}")
        

        print("正在启动 Chrome...")
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome 启动成功")
        
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        return driver
    except Exception as e:
        print(f"设置 Chrome 驱动时发生错误: {e}")
        raise
        

def check_login_status(driver):
    """检查登录状态"""
    try:
        print("正在检查登录状态...")
        # 访问一个需要登录的页面
        driver.get("https://amaze-user.zhenguanyu.com/#/users")
        time.sleep(10)
        
        # 检查当前 URL，如果没有被重定向到登录页面，则表示已登录
        current_url = driver.current_url
        needs_login = 'login' in current_url.lower()
        
        print(f"登录状态检查完成: {'需要登录' if needs_login else '已登录'}")
        print(f"当前URL: {current_url}")
        return needs_login
    except Exception as e:
        print(f"检查登录状态失败: {e}")
        return True  # 如果检查失败，假设需要登录

def login_and_save_cookies():
    """登录并保存cookies"""
    driver = None
    try:
        print("开始登录流程...")
        driver = setup_chrome_driver()
        
        # 访问登录页面
        driver.get("https://tutor.zhenguanyu.com/login")
        print("请在浏览器中完成登录...")
        
        # 等待登录完成
        while check_login_status(driver):
            print("等待登录完成...")
            time.sleep(2)
        
        print("登录成功，正在保存cookies...")
        cookies = driver.get_cookies()
        
        # 保存cookies到文件
        save_login_info(cookies)
        
        # 确保在获取完cookies后再关闭浏览器
        print("保存cookies完成")
        driver.quit()
        print("关闭浏览器...")
        
        return cookies
    except Exception as e:
        print(f"登录过程中发生错误: {e}")
        if driver:
            driver.quit()
        raise

def get_cookies():
    """获取cookies，如果失效则重新登录"""
    print("正在获取cookies...")
    cookies = load_login_info()
    if not cookies:
        print("未找到有效的cookies，需要重新登录")
        cookies = login_and_save_cookies()
    else:
        print("使用已保存的cookies")
        # 验证 cookies 是否有效
        try:
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie.get('domain', 'tutor.zhenguanyu.com'),
                    path=cookie.get('path', '/')
                )
            
            # 尝试访问一个需要认证的接口来验证 cookies
            response = session.get(
                'https://tutor.zhenguanyu.com/tutor-atm-user/api/teachers',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Origin': 'https://tutor.zhenguanyu.com',
                    'Referer': 'https://tutor.zhenguanyu.com/'
                }
            )
            
            if response.status_code == 401:
                print("保存的cookies已失效，需要重新登录")
                cookies = login_and_save_cookies()
        except Exception as e:
            print(f"验证cookies时发生错误: {e}")
            cookies = login_and_save_cookies()
    
    return cookies


def make_request(url, cookies, method='GET'):
    """统一的请求处理函数"""
    session = requests.Session()
    
    # 设置所有必要的 cookies
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
    
    response = session.request(method, url, headers=headers)
    
    if response.status_code == 401:
        print("请求返回401，尝试重新登录...")
        # 这里可以添加重新登录逻辑
        raise Exception("登录已失效")
    
    return response