import os
import requests
from datetime import datetime
from logger import LOG  # 导入日志模块


def unix_to_readable_time(unix_time):
    """将Unix时间戳转换为可读的日期时间格式"""
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')


class HackerNewsClient:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0/{}.json"
        self.item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"

    def fetch_hacker_news_items(self, items_type, items_num):
        LOG.debug(f"准备获取hacker news {items_type} {items_num}条item。")
        try:
            # 获取最新的新闻 ID 列表
            response = requests.get(self.base_url.format(items_type), timeout=10)
            response.raise_for_status()  # 如果响应代码不是200, 则抛出HTTPError异常
            story_ids = response.json()
        except requests.RequestException as e:
            LOG.error(f"获取hacker news失败: {e}")
            return []
        except ValueError:
            LOG.error("解析获取hacker news失败")
            return []

        top_stories = []

        # 获取前10个热门新闻的详细信息
        for story_id in story_ids[:items_num]:
            try:
                story_detail = requests.get(self.item_url.format(story_id), timeout=10)
                story_detail.raise_for_status()  # 检查请求是否成功
                story_data = story_detail.json()

                # 检查新闻数据是否完整
                title = story_data.get('title')
                score = story_data.get('score')
                time_unix = story_data.get('time')  # 获取Unix时间戳
                url = story_data.get('url')  # 获取新闻的实际URL
                if title is None or score is None or time_unix is None or url is None:
                    LOG.warning(f"Story {story_id} has missing data, skipping...")
                    continue

                readable_time = unix_to_readable_time(time_unix)  # 转换为可读时间

                top_stories.append({
                    'title': title,
                    'link': url,
                    'time': readable_time
                })

            except requests.RequestException as e:
                LOG.error(f"Error fetching story {story_id}: {e}")
            except ValueError:
                LOG.error(f"Error parsing story {story_id}, skipping...")
            except KeyError:
                LOG.error(f"Story {story_id} missing key data, skipping...")

        return top_stories

    def save_to_markdown(self, items, items_type):
        today = datetime.today().strftime('%Y-%m-%d')
        markdown_content = f"""# Hacker News {items_type}列表

## 时间：{today}

## 技术前沿与热点话题
"""
        for idx, story in enumerate(items, start=1):
            markdown_content += f"""
{idx}. {story['title']}
   Link：{story['link']}
"""
        md_dir = os.path.join("hacker_news_reports", items_type)
        os.makedirs(md_dir, exist_ok=True)  # 确保目录存在
        file_path = os.path.join(md_dir, f'{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(markdown_content)

        return file_path

    def export_daily_items(self, items_type, items_num):
        LOG.debug(f"准备导出hacker news {items_num}条{items_type} 的最新列表。")
        items = self.fetch_hacker_news_items(items_type, items_num)
        file_path = self.save_to_markdown(items, items_type)
        LOG.info(f"[Hacker News]每日列表文件生成： {file_path}")  # 记录日志
        return file_path


if __name__ == "__main__":
    client = HackerNewsClient()
    client.export_daily_items("beststories", 10)