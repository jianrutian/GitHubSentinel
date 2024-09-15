import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from logger import LOG  # 导入日志模块


class HackerNewsClient:
    def __init__(self):
        pass

    def fetch_hackernews_top_stories(self, type="highest"):
        LOG.debug(f"准备获取hacker news {type} 的 列表。")
        if type == "newest":
            url = 'https://news.ycombinator.com/newest'
        else:
            url = 'https://news.ycombinator.com/'
        try:
            response = requests.get(url)
        except Exception as e:
            LOG.error(f"从 hacker news 获取 列表 失败：{str(e)}")
            LOG.error(f"响应详情：{response.text if 'response' in locals() else '无响应数据可用'}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找包含新闻的所有 <tr> 标签
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                top_stories.append({'title': title, 'link': link})

        return top_stories

    def save_to_markdown(self, stories, type):
        today = datetime.today().strftime('%Y-%m-%d')
        markdown_content = f"""# Hacker News 每日{type}列表

## 时间：{today}

## 技术前沿与热点话题
"""
        for idx, story in enumerate(stories, start=1):
            markdown_content += f"""
{idx}. {story['title']}
   Link：{story['link']}
"""
        md_dir = os.path.join("daily_progress", "hacker_news")
        os.makedirs(md_dir, exist_ok=True)  # 确保目录存在
        file_path = os.path.join(md_dir, f'hackernews_daily_{type}_{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(markdown_content)

        return file_path

    def export_daily_progress(self, type="newest"):
        LOG.debug(f"准备导出hacker news {type} 的最新列表。")
        stories = self.fetch_hackernews_top_stories(type)
        file_path = self.save_to_markdown(stories, type)
        LOG.info(f"[Hacker News]每日列表文件生成： {file_path}")  # 记录日志
        return file_path


if __name__ == "__main__":
    scraper = HackerNewsClient()
    scraper.export_daily_progress("highest")