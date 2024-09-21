# src/report_generator.py
import os
from logger import LOG  # 导入日志模块，用于记录日志信息

class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm  # 初始化时接受一个LLM实例，用于后续生成报告

    def generate_report(self, report_type, markdown_file_path):
        prompts_path = os.path.join("prompts", f"{report_type}_prompt.txt")
        with open(prompts_path, 'r', encoding='utf-8') as file:
            system_content = file.read()
        # 读取Markdown文件并使用LLM生成日报
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_report(system_content, markdown_content)  # 调用LLM生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_" + self.llm.model + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 写入生成的报告

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path


if __name__ == '__main__':
    from llm import LLM
    from config import Config
    config = Config()
    # llm = LLM(config)
    # ReportGenerator(llm).generate_report("hacker_news", "hacker_news_reports/topstories/2024-09-21.md")
    config.llm_model_type = "deepseek"
    llm = LLM(config)
    ReportGenerator(llm).generate_report("hacker_news", "hacker_news_reports/beststories/2024-09-21.md")


