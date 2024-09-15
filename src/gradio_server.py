
import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from hackernews_client import HackerNewsClient
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
hackernews_client = HackerNewsClient()
llm = LLM()
hackernews_llm = LLM("hacker_news")
report_generator = ReportGenerator(llm)
hacker_report_generator = ReportGenerator(hackernews_llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)
hackernews_manager = SubscriptionManager(config.hackernews_file)

def export_daily_report(type):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = hackernews_client.export_daily_progress(type)  # 导出原始数据文件路径
    report, report_file_path = hacker_report_generator.generate_daily_report(raw_file_path)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def remove_subscription(repo):
    subscription_manager.remove_subscription(repo)
    return f"删除{repo}成功！", gr.update(choices=subscription_manager.list_subscriptions()), gr.update(choices=subscription_manager.list_subscriptions())

def add_subscription(repo):
    subscription_manager.add_subscription(repo)
    return f"增加{repo}成功！", gr.update(choices=subscription_manager.list_subscriptions()), gr.update(choices=subscription_manager.list_subscriptions())

# 创建Gradio界面
with gr.Blocks(title="GitHubSentinel", theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# GitHubSentinel")
    with gr.Tab("生成报告"):
        with gr.Row():
            with gr.Column():
                repo = gr.Dropdown(
                    subscription_manager.list_subscriptions(), label="GitHub订阅列表", info="已订阅GitHub项目"
                )  # 下拉菜单选择订阅的GitHub项目
                days = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期",
                                 info="生成项目过去一段时间进展，单位：天")  # 滑动条选择报告的时间范围
                submit_button = gr.Button("提交")

                type = gr.Dropdown(
                    hackernews_manager.list_subscriptions(), label="hacker news类型列表", info="hacker news"
                )  # 下拉菜单选择订阅的GitHub项目
                hacker_button = gr.Button("提交")
            with gr.Column():
                report = gr.Markdown()
                report_file_path = gr.File(label="下载报告")

    with gr.Tab("订阅管理"):
        with gr.Row():
            with gr.Column(scale=1):
                del_repo = gr.Dropdown(
                    subscription_manager.list_subscriptions(), label="选择要删除的订阅"
                )  # 下拉菜单选择订阅的GitHub项目
                del_button = gr.Button("删除订阅")
            with gr.Column(scale=1):
                add_repo = gr.Textbox(label="输入要添加的项目订阅", placeholder="请输入GitHub项目名称")
                add_button = gr.Button("添加订阅")
        result = gr.Markdown()

    submit_button.click(export_progress_by_date_range, inputs=[repo, days], outputs=[report, report_file_path])
    hacker_button.click(export_daily_report, inputs=[type], outputs=[report, report_file_path])
    del_button.click(remove_subscription, inputs=del_repo, outputs=[result, del_repo, repo])
    add_button.click(add_subscription, inputs=add_repo, outputs=[result, del_repo, repo])


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))