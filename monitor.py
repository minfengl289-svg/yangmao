import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 读取 GitHub Secrets 环境变量
API_KEY = os.environ.get("AI_API_KEY")
WXPUSHER_TOKEN = os.environ.get("WXPUSHER_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")

URL = "https://www.51kanong.com/yh-169-1.htm"

def fetch_deals():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(URL, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        deals = []
        # 根据 51卡农 页面结构提取帖子标题和链接
        for item in soup.select('.fl.ilist ul li, .post-list li, .comwidth ul li'):
            a_tag = item.find('a')
            if a_tag and a_tag.get('href'):
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href')
                if title and len(title) > 5:
                    if not link.startswith('http'):
                        link = "https://www.51kanong.com/" + link.lstrip('/')
                    deals.append(f"标题: {title}\n链接: {link}")
        return deals[:10] # 获取前 10 条最新线报
    except Exception as e:
        print(f"抓取网页失败: {e}")
        return []

def analyze_with_ai(deals):
    if not API_KEY or not deals:
        return []
    
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.siliconflow.cn/v1"
    )
    
    text_content = "\n\n".join(deals)
    prompt = f"""
    下面是 51卡农 网站上的最新线报列表，请帮我筛选出有价值的“羊毛”线报（如充值返利、漏洞、有效优惠、大额优惠券等）。
    请过滤掉垃圾广告、无意义水贴。
    对于筛选出的优质线报，请给出简短的推荐理由和精炼摘要。
    如果全都没有价值，请直接回复“无”。

    线报列表：
    {text_content}
    """
    
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI 分析失败: {e}")
        return None

def send_wxpusher(content):
    if not WXPUSHER_TOKEN or not WXPUSHER_UID or not content or content.strip() == "无":
        print("没有有效内容或未配置推送")
        return
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": WXPUSHER_TOKEN,
        "content": f"🐑 51卡农最新优质线报通知\n\n{content}",
        "summary": "51卡农羊毛线报",
        "contentType": 1,
        "uids": [WXPUSHER_UID]
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print("微信推送结果:", res.text)
    except Exception as e:
        print(f"微信推送失败: {e}")

if __name__ == "__main__":
    print("开始抓取 51卡农...")
    deals = fetch_deals()
    if deals:
        print(f"成功抓取到 {len(deals)} 条线报，开始 AI 筛选...")
        result = analyze_with_ai(deals)
        if result and result.strip() != "无":
            print("发现有效线报，准备发送微信推送...")
            send_wxpusher(result)
        else:
            print("AI 筛选结果：暂无高价值羊毛。")
    else:
        print("未抓取到内容。")
