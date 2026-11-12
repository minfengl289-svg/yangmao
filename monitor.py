import os
import time
import requests
from bs4 import BeautifulSoup

URL = "https://www.51kanong.com/yh-169-1.htm"

def fetch_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.51kanong.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    session = requests.Session()
    try:
        # 第一次请求，获取带有 JS 挑战的页面
        res = session.get(URL, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        
        # 如果页面包含 JS 挑战跳转，我们模拟等待 1 秒后再次请求（通常服务器会种下 Cookie 放行）
        if "reload()" in res.text:
            print("检测到防爬 JS 挑战，正在模拟浏览器二次请求...")
            time.sleep(1.5)
            # 带上刚才种下的 Cookie 再次请求
            res = session.get(URL, headers=headers, timeout=10)
            res.encoding = 'utf-8'

        print(f"最终网页请求状态码: {res.status_code}")
        print(f"绕过后源码前 200 字符: {res.text[:200].strip()}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        deals = []
        
        for a in soup.find_all('a'):
            title = a.get_text(strip=True)
            href = a.get('href')
            if title and len(title) > 5 and href:
                if not href.startswith('http'):
                    href = "https://www.51kanong.com" + (href if href.startswith('/') else '/' + href)
                item = f"标题: {title}\n链接: {href}"
                if item not in deals:
                    deals.append(item)
                    
        print(f"成功抓取到的链接总数: {len(deals)}")
        return deals[:15]
    except Exception as e:
        print(f"抓取异常: {e}")
        return []

if __name__ == "__main__":
    print("开始执行 JS 绕过抓取...")
    deals = fetch_deals()
    if deals:
        print(f"成功突破！抓到条数: {len(deals)}")
    else:
        print("依然被拦截，准备启用备用方案。")
