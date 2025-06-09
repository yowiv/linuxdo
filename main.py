from curl_cffi import requests
import os
import json
import time
import random
from typing import Dict, Optional

def get_csrf_token(session, cf_clearance) -> str:
    """
    获取 CSRF token
    
    Args:
        session: session 对象，用于保持会话
        cf_clearance: CF_CLEARANCE值，必须提供
    
    Returns:
        CSRF token 字符串
    """
    url = "https://linux.do/session/csrf"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua-platform': '"Windows"',
        'x-csrf-token': "undefined",
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': "?0",
        'x-requested-with': "XMLHttpRequest",
        'discourse-present': "true",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://linux.do/login",
        'accept-language': "zh,zh-CN;q=0.9",
        'priority': "u=1, i"
    }
    
    # 必须设置cf_clearance
    session.cookies.set('cf_clearance', cf_clearance)
    
    try:
        response = session.get(url, headers=headers, verify=False, impersonate="chrome")
        if response.status_code == 200:
            data = response.json()
            csrf_token = data.get('csrf')
            if csrf_token:
                return csrf_token
            else:
                raise Exception("响应中未找到 CSRF token")
        else:
            raise Exception(f"获取 CSRF token 失败，状态码: {response.status_code}")
    except Exception as e:
        raise Exception(f"获取 CSRF token 异常: {str(e)}")

def login_linux_do(email: str = None, password: str = None, cf_clearance: str = None, csrf_token: str = None, auto_get_csrf: bool = True) -> Dict:
    """
    登录 linux.do 论坛
    
    Args:
        email: 邮箱地址，如果为空则从环境变量 LINUX_DO_EMAIL 获取
        password: 密码，如果为空则从环境变量 LINUX_DO_PASSWORD 获取
        cf_clearance: CF_CLEARANCE值，如果为空则从环境变量 CF_CLEARANCE 获取
        csrf_token: CSRF令牌，如果为空且 auto_get_csrf=True 则自动获取
        auto_get_csrf: 是否自动获取 CSRF token，默认为 True
    
    Returns:
        包含响应信息的字典，登录成功返回用户信息
    """
    # 从环境变量获取配置
    email = email or os.getenv('LINUX_DO_EMAIL')
    password = password or os.getenv('LINUX_DO_PASSWORD')
    cf_clearance = cf_clearance or os.getenv('CF_CLEARANCE')
    
    if not email or not password:
        return {"success": False, "error": "邮箱或密码未提供", "email": email}
    
    # 必须要有CF_CLEARANCE
    if not cf_clearance:
        return {
            "success": False, 
            "error": "必须提供CF_CLEARANCE！请在浏览器F12中找到'cdn-cgi/challenge-platform/h/b/rc/'接口响应的cookies值", 
            "email": email
        }
    
    # 创建会话对象以保持 Cookie
    session = requests.Session()
    
    # 获取 CSRF token
    if not csrf_token and auto_get_csrf:
        try:
            print("正在获取 CSRF token...")
            csrf_token = get_csrf_token(session, cf_clearance)
            print(f"✅ CSRF token 获取成功: {csrf_token[:20]}...")
        except Exception as e:
            return {"success": False, "error": f"获取 CSRF token 失败: {str(e)}", "email": email}
    elif not csrf_token:
        csrf_token = os.getenv('LINUX_DO_CSRF_TOKEN', '')
    
    url = "https://linux.do/session"
    
    payload = {
        'login': email,
        'password': password,
        'second_factor_method': "1",
        'timezone': "Asia/Shanghai"
    }
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'Accept-Language': "zh,zh-CN;q=0.9",
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': "?0",
        'x-requested-with': "XMLHttpRequest",
        'discourse-present': "true",
        'origin': "https://linux.do",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://linux.do/login",
        'priority': "u=1, i"
    }
    
    # 添加 CSRF 令牌
    if csrf_token:
        headers['x-csrf-token'] = csrf_token
    
    try:
        print("正在尝试登录...")
        response = session.post(url, data=payload, headers=headers, verify=False, impersonate="chrome")
        
        # 尝试解析JSON响应
        try:
            response_data = response.json()
            if response.status_code == 200 and 'user' in response_data:
                # 登录成功
                user_info = response_data['user']
                
                # 获取session cookies
                session_cookies = dict(session.cookies)
                
                # 构建标准格式的cookies字符串：_t=xxx; cf_clearance=xxx; _forum_session=xxx
                cookies_parts = []
                
                # 1. _t cookie (通常是认证token)
                if '_t' in session_cookies:
                    cookies_parts.append(f"_t={session_cookies['_t']}")
                
                # 2. cf_clearance (必须有，优先使用传入的参数)
                cookies_parts.append(f"cf_clearance={cf_clearance}")
                
                # 3. _forum_session (会话cookie)
                if '_forum_session' in session_cookies:
                    cookies_parts.append(f"_forum_session={session_cookies['_forum_session']}")
                
                # 拼接成最终的cookies字符串
                final_cookies = '; '.join(cookies_parts)
                
                print(f"✅ 构建cookies字符串: {final_cookies[:100]}...")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "email": email,
                    "username": user_info.get('username'),
                    "user_id": user_info.get('id'),
                    "trust_level": user_info.get('trust_level'),
                    "created_at": user_info.get('created_at'),
                    "last_seen_at": user_info.get('last_seen_at'),
                    "badge_count": user_info.get('badge_count'),
                    "gamification_score": user_info.get('gamification_score'),
                    "time_read": user_info.get('time_read'),
                    "csrf_token": csrf_token,
                    "session_cookies": session_cookies,
                    "cookies_string": final_cookies,
                    "cf_clearance": cf_clearance,
                    "response_data": response_data
                }
            else:
                error_msg = response_data.get('error', '登录失败')
                if isinstance(error_msg, list):
                    error_msg = ', '.join(error_msg)
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "email": email,
                    "error": error_msg,
                    "response": response.text
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "status_code": response.status_code,
                "email": email,
                "error": "响应不是有效的JSON格式",
                "response": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"请求异常: {str(e)}",
            "email": email
        }

def test_cookies_validity(cookies_string: str, csrf_token: str, username: str) -> Dict:
    """
    测试cookies有效性，访问用户徽章接口
    
    Args:
        cookies_string: 完整的cookies字符串
        csrf_token: CSRF token
        username: 用户名
    
    Returns:
        包含测试结果的字典
    """
    url = f"https://linux.do/user-badges/{username}.json?grouped=true"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua-platform': '"Windows"',
        'x-csrf-token': csrf_token,
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': "?0",
        'discourse-logged-in': "true",
        'x-requested-with': "XMLHttpRequest",
        'discourse-present': "true",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': f"https://linux.do/u/{username}/badges",
        'accept-language': "zh,zh-CN;q=0.9",
        'priority': "u=1, i",
        'Cookie': cookies_string
    }
    
    try:
        print(f"🧪 测试cookies有效性，访问用户 {username} 的徽章信息...")
        response = requests.get(url, headers=headers, verify=False)
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                badges = data.get('badges', [])
                
                # 查找"基本用户"徽章
                basic_user_badge = None
                for badge in badges:
                    if badge.get('name') == '基本用户':
                        basic_user_badge = badge
                        break
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "badge_count": len(badges),
                    "has_basic_user_badge": basic_user_badge is not None,
                    "basic_user_badge": basic_user_badge,
                    "response_data": data
                }
                
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": "响应不是有效的JSON格式",
                    "response_text": response.text[:500]
                }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": f"请求失败",
                "response_text": response.text[:500]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"请求异常: {str(e)}"
        }

def get_latest_topics(cookies_string: str, csrf_token: str, page: int = 1) -> Dict:
    """
    获取最新帖子列表
    
    Args:
        cookies_string: 完整的cookies字符串
        csrf_token: CSRF token
        page: 页码，默认为1
    
    Returns:
        包含帖子列表的字典
    """
    url = f"https://linux.do/latest.json?no_definitions=true&page={page}"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua-platform': '"Windows"',
        'x-csrf-token': csrf_token,
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': "?0",
        'discourse-logged-in': "true",
        'x-requested-with': "XMLHttpRequest",
        'discourse-present': "true",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://linux.do/",
        'accept-language': "zh,zh-CN;q=0.9",
        'priority': "u=1, i",
        'Cookie': cookies_string
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 获取到 {len(data.get('topic_list', {}).get('topics', []))} 个帖子")
            topics = data.get('topic_list', {}).get('topics', [])
            
            return {
                "success": True,
                "status_code": response.status_code,
                "topics_count": len(topics),
                "topics": topics,
                "response_data": data
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": "获取帖子列表失败",
                "response_text": response.text[:500]
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"请求异常: {str(e)}"
        }

def like_post(cookies_string: str, csrf_token: str, post_id: int, topic_id: int) -> Dict:
    """
    为帖子点赞
    
    Args:
        cookies_string: 完整的cookies字符串
        csrf_token: CSRF token
        post_id: 帖子ID
        topic_id: 话题ID
    
    Returns:
        包含点赞结果的字典
    """
    url = f"https://linux.do/discourse-reactions/posts/{post_id}/custom-reactions/heart/toggle.json"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'content-length': "0",
        'sec-ch-ua-platform': '"Windows"',
        'x-csrf-token': csrf_token,
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': "?0",
        'discourse-logged-in': "true",
        'x-requested-with': "XMLHttpRequest",
        'discourse-present': "true",
        'origin': "https://linux.do",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': f"https://linux.do/t/topic/{topic_id}",
        'accept-language': "zh,zh-CN;q=0.9",
        'priority': "u=1, i",
        'Cookie': cookies_string
    }
    
    try:
        response = requests.put(url, headers=headers, verify=False)
        
        result = {
            "success": response.status_code in [200, 201],
            "status_code": response.status_code,
            "post_id": post_id,
            "topic_id": topic_id,
            "response_text": response.text
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"点赞请求异常: {str(e)}",
            "post_id": post_id,
            "topic_id": topic_id
        }

def get_topic_first_post_id(cookies_string: str, csrf_token: str, topic_id: int) -> Optional[int]:
    """
    获取主题的第一个帖子ID（用于点赞）
    
    Args:
        cookies_string: 完整的cookies字符串
        csrf_token: CSRF token
        topic_id: 话题ID
    
    Returns:
        第一个帖子的ID，如果获取失败返回None
    """
    url = f"https://linux.do/t/{topic_id}"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua-platform': '"Windows"',
        'x-csrf-token': csrf_token,
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': "?0",
        'discourse-logged-in': "true",
        'x-requested-with': "XMLHttpRequest",
        'discourse-present': "true",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': f"https://linux.do/t/{topic_id}",
        'accept-language': "zh,zh-CN;q=0.9",
        'priority': "u=1, i",
        'Cookie': cookies_string
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            post_stream = data.get('post_stream', {})
            posts = post_stream.get('posts', [])
            
            if posts:
                # 返回第一个帖子的ID
                return posts[0].get('id')
        
        return None
        
    except Exception as e:
        print(f"   ⚠️ 获取帖子ID失败: {str(e)}")
        return None

def auto_like_topics(cookies_string: str, csrf_token: str, max_topics: int = 5, browse_count: int = None, delay_range: tuple = (1, 3)) -> Dict:
    """
    自动为最新帖子点赞
    
    Args:
        cookies_string: 完整的cookies字符串
        csrf_token: CSRF token
        max_topics: 最大点赞帖子数量
        browse_count: 浏览帖子数量，None表示浏览所有
        delay_range: 延迟范围（秒），避免请求过于频繁
    
    Returns:
        包含点赞结果的字典
    """
    print("🔍 正在获取最新帖子列表...")
    
    # 获取最新帖子
    topics_result = get_latest_topics(cookies_string, csrf_token)
    
    if not topics_result['success']:
        return {
            "success": False,
            "error": "获取帖子列表失败",
            "details": topics_result
        }
    
    all_topics = topics_result['topics']  # 获取所有帖子
    
    # 根据browse_count限制浏览数量
    if browse_count and browse_count < len(all_topics):
        browsed_topics = all_topics[:browse_count]
        print(f"📋 限制浏览前 {browse_count} 个帖子")
    else:
        browsed_topics = all_topics
        print(f"📋 浏览所有 {len(all_topics)} 个帖子")
    
    # 浏览帖子
    print("\n👀 浏览帖子:")
    for i, topic in enumerate(browsed_topics, 1):
        fancy_title = topic.get('fancy_title', '无标题')
        topic_id = topic.get('id')
        like_count = topic.get('like_count', 0)
        replies_count = topic.get('posts_count', 1) - 1  # 减去原帖
        
        print(f"{i:2d}. 📝 {fancy_title} (ID:{topic_id}, 👍:{like_count}, 💬:{replies_count})")
    
    # 随机选择要点赞的帖子（从浏览的帖子中选择）
    if len(browsed_topics) <= max_topics:
        selected_topics = browsed_topics
        print(f"\n🎯 浏览的帖子数量不超过{max_topics}个，将对所有浏览的帖子点赞")
    else:
        selected_topics = random.sample(browsed_topics, max_topics)
        print(f"\n🎯 从浏览的帖子中随机选择 {max_topics} 个进行点赞:")
        
        # 显示选中的帖子
        for i, topic in enumerate(selected_topics, 1):
            fancy_title = topic.get('fancy_title', '无标题')
            topic_id = topic.get('id')
            print(f"   {i}. {fancy_title} (ID:{topic_id})")
    
    print(f"\n🤖 开始点赞，每次点赞后随机延迟 {delay_range[0]} 到 {delay_range[1]} 秒...\n")
    
    results = []
    
    for i, topic in enumerate(selected_topics, 1):
        topic_id = topic.get('id')
        fancy_title = topic.get('fancy_title', '无标题')
        
        print(f"{i}. 正在处理帖子:")
        print(f"   📝 标题: {fancy_title}")
        print(f"   🆔 主题ID: {topic_id}")
        
        # 获取第一个帖子的真实ID
        print(f"   🔍 正在获取帖子详情...")
        first_post_id = get_topic_first_post_id(cookies_string, csrf_token, topic_id)
        
        if not first_post_id:
            print(f"   ❌ 无法获取帖子ID，跳过此帖子")
            results.append({
                "topic_id": topic_id,
                "fancy_title": fancy_title,
                "like_result": {
                    "success": False,
                    "error": "无法获取帖子ID"
                }
            })
            continue
        
        print(f"   📍 帖子ID: {first_post_id}")
        
        # 执行点赞
        like_result = like_post(cookies_string, csrf_token, first_post_id, topic_id)
        
        if like_result['success']:
            print(f"   ✅ 点赞成功! (状态码: {like_result['status_code']})")
        else:
            print(f"   ❌ 点赞失败! (状态码: {like_result.get('status_code', 'N/A')})")
            if like_result.get('error'):
                print(f"   错误: {like_result['error']}")
        
        results.append({
            "topic_id": topic_id,
            "post_id": first_post_id,
            "fancy_title": fancy_title,
            "like_result": like_result
        })
        
        # 添加随机延迟
        if i < len(selected_topics):  # 不是最后一个
            delay = random.uniform(delay_range[0], delay_range[1])
            print(f"   ⏳ 等待 {delay:.1f} 秒...\n")
            time.sleep(delay)
    
    success_count = sum(1 for r in results if r['like_result']['success'])
    
    return {
        "success": True,
        "total_topics_available": len(all_topics),
        "browsed_topics_count": len(browsed_topics),
        "selected_topics": len(selected_topics),
        "success_count": success_count,
        "fail_count": len(selected_topics) - success_count,
        "results": results
    }

def main_with_auto_like():
    """主函数 - 包含自动点赞功能"""
    print("=== Linux.do 论坛自动点赞工具 ===\n")
    
    # 检查CF_CLEARANCE（必须）
    cf_clearance = os.getenv('CF_CLEARANCE')
    if not cf_clearance:
        # 如果环境变量没有，使用硬编码的默认值
        cf_clearance = 'Ki7oQGgjT4OzwcWLK6TD767ckwlAlh9HoGRjdSA_5NY-1749460838-1.2.1.1-lepR0Dss2tD.94c3NTCUZ_tCBzrAR3s7IB5lt6VbSO1vpYeJuO8jhubTkE6gfLdtVwHSsAwHjE38bec_DlN6yMGItnmDGSzLpvRmzUFW1huW12bQ6qm4lsM7O_Jmj339gMYDTt1IYTyaYLug7m45JQebLVIl6p7HSO.gby6KkNEnzI3.vf6z4.GkmxfMlOrn.KSNOK60wUEOmjS_8cNHpbbwkEvwahB8VMlQYjHhOIxkX.2bhCui3NHREBQvoxZmmS6nSWVWUXEPmnvLlY8w8IqDhDQC7ppKtDtDHdE6RKgD1RW6MO6Ten.J6OQOjE.fllRohoxD44LTVor8C.hWu3UxYa6Ksas5JJ_gevDd7DXFm_5FImGgbQw9LT_QxpRc'
        print(f"⚠️ 未检测到CF_CLEARANCE环境变量，使用默认值")
    
    # 执行登录
    result = login_linux_do()
    
    if result['success']:
        print("✅ 登录成功!")
        print(f"用户名: {result['username']}")
        print(f"用户ID: {result['user_id']}")
        print(f"信任等级: {result['trust_level']}")
        
        # 读取环境变量配置
        enable_like = os.getenv('ENABLE_LIKE', 'true').lower() in ['true', '1', 'yes', 'on']
        like_count = max(1, int(os.getenv('LIKE_COUNT', '5')))  # 最小为1
        browse_count = os.getenv('BROWSE_COUNT')
        if browse_count:
            browse_count = max(1, int(browse_count))  # 最小为1
        
        print(f"\n🔧 配置信息:")
        print(f"   启用点赞: {'是' if enable_like else '否'}")
        if enable_like:
            print(f"   点赞数量: {like_count}")
        print(f"   浏览数量: {'全部' if browse_count is None else browse_count}")
        
        if not enable_like:
            print("\n⏸️ 点赞功能已禁用，仅浏览帖子...")
            # 只获取和显示帖子列表
            topics_result = get_latest_topics(result['cookies_string'], result['csrf_token'])
            if topics_result['success']:
                all_topics = topics_result['topics']
                
                # 根据browse_count限制浏览数量
                if browse_count and browse_count < len(all_topics):
                    browsed_topics = all_topics[:browse_count]
                    print(f"\n📋 浏览前 {browse_count} 个帖子:")
                else:
                    browsed_topics = all_topics
                    print(f"\n📋 浏览所有 {len(all_topics)} 个帖子:")
                
                for i, topic in enumerate(browsed_topics, 1):
                    fancy_title = topic.get('fancy_title', '无标题')
                    topic_id = topic.get('id')
                    like_count_topic = topic.get('like_count', 0)
                    replies_count = topic.get('posts_count', 1) - 1
                    print(f"{i:2d}. 📝 {fancy_title} (ID:{topic_id}, 👍:{like_count_topic}, 💬:{replies_count})")
                
                print(f"\n📊 浏览统计:")
                print(f"   可用帖子总数: {len(all_topics)}")
                print(f"   实际浏览数: {len(browsed_topics)}")
            else:
                print("❌ 获取帖子列表失败!")
            return
        
        # 开始自动点赞
        print("\n" + "="*50)
        print("🤖 开始自动点赞...")
        
        auto_like_result = auto_like_topics(
            cookies_string=result['cookies_string'],
            csrf_token=result['csrf_token'],
            max_topics=like_count,  # 使用环境变量设置的点赞数量
            browse_count=browse_count,  # 使用环境变量设置的浏览数量
            delay_range=(2, 5)  # 2-5秒随机延迟
        )
        
        if auto_like_result['success']:
            print(f"\n📊 统计信息:")
            print(f"   可用帖子总数: {auto_like_result['total_topics_available']}")
            print(f"   实际浏览数: {auto_like_result['browsed_topics_count']}")
            print(f"   选择点赞数: {auto_like_result['selected_topics']}")
            print(f"   点赞成功数: {auto_like_result['success_count']}")
            print(f"   点赞失败数: {auto_like_result['fail_count']}")
            if auto_like_result['selected_topics'] > 0:
                print(f"   点赞成功率: {auto_like_result['success_count']/auto_like_result['selected_topics']*100:.1f}%")
        else:
            print("❌ 自动点赞失败!")
            print(f"错误: {auto_like_result.get('error', '未知错误')}")
        
    else:
        print("❌ 登录失败!")
        print(f"错误信息: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main_with_auto_like()