import requests
from requests.adapters import HTTPAdapter
from common_utils import make_request
import traceback


def get_lesson_info(lessonid, cookies):
    """获取班课信息"""
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-atm-lesson/api/v2/lessons/withSaleInfo/{lessonid}"

        response = make_request(url, cookies)

        if response.status_code != 200:
            raise Exception(f"获取班课信息失败: HTTP {response.status_code}")

        lesson_data = response.json()

        return {
            'id': lesson_data.get('id', ''),
            'name': lesson_data.get('name', ''),
            'semesterId': lesson_data.get('semester', {}).get('id', ''),
            'grades': lesson_data.get('grades', [{}])[0].get('id', '') if (grades := lesson_data.get('grades')) else '',
            'subjectId': lesson_data.get('subject', {}).get('id', ''),
            'period': lesson_data.get('period', '')
        }
    except Exception as e:
        print(f"获取班课信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        raise


def get_exam_list(lesson_info, cookies):
    """查询摸底测试"""
    # subjectId = lesson_info.get('subjectId', '')
    gradeId = lesson_info.get('grades', '')
    semesterId = lesson_info.get('semesterId', '')
    period = lesson_info.get('period', '')
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-atm-exercise/api/lesson-baseline-exams/ids?pageSize=20&page=0&gradeId={gradeId}&semesterId={semesterId}&period={period}&sheetStatus=published"
        print("获取摸底测试接口：", url)

        response = make_request(url, cookies)

        if response.status_code != 200:
            raise Exception(f"获取摸底测试信息失败: HTTP {response.status_code}")

        exam_list = response.json()
        if not exam_list.get('list') or len(exam_list['list']) == 0:
            raise Exception("未找到摸底测试数据")

        exam_list_result = exam_list.get('list')
        # 通过测试id，查询到baselineExamId
        baselineExamId = []
        for exam in exam_list_result:
            url = f'https://tutor.zhenguanyu.com/tutor-atm-exercise/api/lesson-baseline-exams/info/{exam}'
            response = make_request(url, cookies)
            if response.status_code != 200:
                raise Exception(f"获取摸底测试信息失败: HTTP {response.status_code}")
            exam_data = response.json()
            baselineExamId.append(exam_data.get('baselineExamId'))
        return exam_list_result, baselineExamId

    except Exception as e:
        print(f"获取课程信息时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        raise


def get_lesson_exam_info(baselineExamId, cookies):
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=3, pool_connections=50, pool_maxsize=50, pool_block=True))
    try:
        url = f"https://tutor.zhenguanyu.com/tutor-atm-lesson/api/lessons/baselineExamId/{baselineExamId}?pageSize=20&page=0"
        print(f"查询 {baselineExamId} 摸底测试绑定的班课")

        response = make_request(url, cookies)

        if response.status_code != 200:
            print(f"API响应内容: {response.text}")
            raise Exception(f"获取班课列表失败: HTTP {response.status_code}")

        lesson_response = response.json()
        lesson_list = []
        for item in lesson_response.get('list', []):
            lesson_list.append(item.get("id"))
        print(f"获取班课列表成功: {lesson_list}")
        return lesson_list
    except Exception as e:
        print(f"获取班课列表时发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
    finally:
        session.close()


def exam_search(lessonid, cookies):
    try:
        matches = []
        print("\n=== 开始新的查询 ===")
        if not lessonid:
            print("错误：未提供班课ID")
            return {'success': False, 'error': '请输入班课ID'}

        print(f"查询班课: {lessonid}")

        try:
            # 获取班课信息
            print("正在获取班课信息...")
            lesson_info = get_lesson_info(lessonid, cookies)
            print(f"班课信息获取成功: {lesson_info}")
        except Exception as e:
            print(f"获取班课信息失败: {e}")
            return {'success': False, 'error': f'获取班课信息失败: {str(e)}'}

        try:
            # 获取测试信息
            print("正在获取测试信息...")
            exam_info, examId_info = get_exam_list(lesson_info, cookies)
            print(f"测试信息获取成功: {exam_info}")
            print(f"测试ID获取成功: {examId_info}")
        except Exception as e:
            print(f"获取测试信息失败: {e}")
            return {'success': False, 'error': f'获取测试信息失败: {str(e)}'}

        try:
            # 获取绑定班课信息
            print("正在获取绑定班课信息...")
            for i, examId in enumerate(examId_info):
                lesson_list = get_lesson_exam_info(examId, cookies)
                for lesson_id in lesson_list:
                    if str(lesson_id) == str(lessonid):
                        print(f"找到匹配的班课: {lessonid}")
                        print(f"当前摸底测试为: {examId}")
                        print(f"当前摸底测试ID为: {exam_info[i]}")
                        url = f"https://amaze.zhenguanyu.com/#/jwc/baselineExams/baselineExam/{exam_info[i]}/lessons"
                        print(f"链接：{url}")
                        matches.append({
                            'exam_id': exam_info[i],
                            'link': url
                        })
            print(f"查询完成:",matches)
            return {
                'success': bool(matches),
                'lessonid': lessonid,
                'matches': matches,
                'count': len(matches)
            }
        except Exception as e:
            print(f"获取绑定班课失败: {e}")
            return {'success': False, 'error': f'获取绑定班课失败: {str(e)}'}

    except Exception as e:
        print(f"查询过程中发生错误: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}