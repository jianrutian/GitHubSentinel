import json
import os

class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        # 尝试从环境变量获取配置或使用 config.json 文件中的配置作为回退
        with open('config.json', 'r') as f:
            config = json.load(f)
            
            # 使用环境变量或配置文件的 GitHub Token
            github_config = config.get('github', {})
            self.github_token = os.getenv('GITHUB_TOKEN', github_config.get('token'))
            self.github_subscriptions_file = github_config.get('subscriptions_file', "subscriptions.json")
            self.github_freq_days = github_config.get('progress_frequency_days', 1)
            # 默认早上8点更新 (操作系统默认时区是 UTC +0，08点刚好对应北京时间凌晨12点)
            self.github_exec_time = github_config.get('progress_execution_time', "08:00")

            hn_config = config.get('hacker_news', {})
            self.hn_items_types = hn_config.get('items_types', ["topstories"])
            self.hn_freq_days = hn_config.get('progress_frequency_days', 1)
            # 默认早上8点更新 (操作系统默认时区是 UTC +0，08点刚好对应北京时间凌晨12点)
            self.hn_exec_time = hn_config.get('progress_execution_time', "08:00")
            self.hn_items_nums = hn_config.get('items_nums', 10)

            # 初始化电子邮件设置
            self.email = config.get('email', {})
            # 使用环境变量或配置文件中的电子邮件密码
            self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))

            # 加载 LLM 相关配置
            llm_config = config.get('llm', {})
            self.llm_model_type = llm_config.get('model_type', 'openai')
            self.openai_model_name = llm_config.get('openai_model_name', 'gpt-4o-mini')
            self.ollama_model_name = llm_config.get('ollama_model_name', 'llama3')
            self.deepseek_model_name = llm_config.get('deepseek_model_name', 'deepseek-chat')
            self.ollama_api_url = llm_config.get('ollama_api_url', 'http://localhost:11434/api/chat')