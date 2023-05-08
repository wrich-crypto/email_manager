import re
from imapclient import IMAPClient
from bs4 import BeautifulSoup
import time

class Email:
    def __init__(self, email, password, server_address='imap-mail.outlook.com'):
        self.email = email
        self.password = password
        self.server = self.connect_outlook(server_address)

    def connect_outlook(self, server_address):
        try:
            server = IMAPClient(server_address, ssl=True)
            server.login(self.email, self.password)
            return server
        except Exception as e:
            print(f"Error connecting to Outlook: {e}")
            return None

    def get_recent_email(self, folder='INBOX'):
        try:
            self.server.select_folder(folder)
            messages = self.server.search('ALL')
            msg_id = messages[-1]
            msg_data = self.server.fetch([msg_id], ['ENVELOPE', 'BODY[TEXT]'])
            msg_body = msg_data[msg_id][b'BODY[TEXT]']
            return msg_body
        except Exception as e:
            print(f"Error getting recent email: {e}")
            return None

    def monitor_new_emails(self, folder='INBOX', callback=None):
        self.server.select_folder(folder)
        previous_messages = self.server.search('ALL')

        while True:
            time.sleep(5)  # Wait for 5 seconds before checking for new emails
            current_messages = self.server.search('ALL')

            if len(current_messages) > len(previous_messages):
                new_message_id = list(set(current_messages) - set(previous_messages))[0]
                msg_data = self.server.fetch([new_message_id], ['ENVELOPE', 'BODY[TEXT]'])
                msg_body = msg_data[new_message_id][b'BODY[TEXT]']
                if callback:
                    callback(msg_body)
                return msg_body

            previous_messages = current_messages

    def parse_body_to_string(self, msg_body):
        try:
            soup = BeautifulSoup(msg_body, 'html.parser')
            text = soup.get_text()
            return text
        except Exception as e:
            print(f"Error parsing email body: {e}")
            return None

    def get_verification_code(self, text, pattern_type='digits'):
        #'digits': r'\b\d{6}\b'：这个正则表达式用于匹配一个字符串中的 6 位数字。\d 表示任意数字字符，\d{6} 表示连续的 6 个数字字符。\b 是一个单词边界，确保数字字符前后没有其他数字或字母。所以，这个正则表达式会匹配 6 位数字，例如 "123456"。
        #'alphanumeric': r'\b[a-zA-Z0-9]{6}\b'：这个正则表达式用于匹配一个字符串中的 6 个字母数字字符（包括大小写字母和数字）。[a-zA-Z0-9] 表示任意字母（大写或小写）或数字字符，[a-zA-Z0-9]{6} 表示连续的 6 个字母数字字符。\b 与上述相同，表示单词边界。所以，这个正则表达式会匹配 6 个字母数字字符，例如 "a1B2c3"。

        patterns = {
            'digits': r'\b\d{6}\b',
            'alphanumeric': r'\b[a-zA-Z0-9]{6}\b',
        }
        pattern = patterns.get(pattern_type, r'\b\d{6}\b')
        try:
            code = re.findall(pattern, text)
            if code:
                return code[0]
            else:
                return None
        except Exception as e:
            print(f"Error getting verification code: {e}")
            return None
