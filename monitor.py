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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(URL, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        print(f"网页请求状态码: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        deals = []
        
        # 换用更通用的方式：抓取页面上所有的 a 标签，只要标题长度合适就收集
        for a_tag in soup.find_all('a'):
            title = a_tag.get_text(strip=True)
            link = a_tag.get('href')
            if title and len(title) > 8:  # 过滤掉太短的导航字样
                if link and not link.startswith('http'):
                    link = "https://www.51kanong.com" + (link if link.startswith('/') else '/' + link)
                deal_item = f"标题: {title}\n链接: {link}"
                if deal_item not in deals:
                    deals.append(deal_item)
                    
        print(f"成功抓取到链接数量: {len(deals)}")
        return deals[:15] # 取前 15 条
    except Exception as e:
        print(f"抓取网页失败: {e}")
        return []

def analyze_with_ai(deals):
    if not API_KEY or not deals:
        return "直接推送测试" # 如果没有配置 AI 密钥或者调试，直接把内容推过去测试
    
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.siliconflow.cn/v1"
    )
    
    text_content = "\n\n".join(deals)
    prompt = f"""
    下面是 51卡农 网站上的最新抓取内容，请帮我筛选出有价值的“羊毛”线报（如返利、优惠券、活动等）。
    如果里面有任何看起来像线报的内容，请提取并简单总结。如果全是无意义杂项，请直接回复“无”。

    内容列表：
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
        # 如果 AI 报错，保底直接把抓到的第一条内容推出去验证
        return deals[0] if deals else "无"

def send_wxpusher(content):
    if not WXPUSHER_TOKEN or not WXPUSHER_UID or not content or content.strip() == "无":
        print("没有有效内容或未配置推送")
        return
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": WXPUSHER_TOKEN,
        "content": f"🐑 51卡农最新监控通知\n\n{content}",
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
        print("开始进行内容分析...")
        result = analyze_with_ai(deals)
        print(f"最终推送内容结果: {result}")
        send_wxpusher(result)
    else:
        print("未抓取到内容。")
