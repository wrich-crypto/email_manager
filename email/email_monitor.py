import json
from interface.email import *
from package.dingding import *

def read_accounts(file_path):
    accounts = []
    with open(file_path, 'r') as accounts_file:
        for line in accounts_file:
            email, password = line.strip().split()
            accounts.append((email, password))
    return accounts


def load_config(file_path):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data


def print_body(msg_body):
    email_client = Email(None, None)
    body = email_client.parse_body_to_string(msg_body)
    print(body)



def print_verification_code(msg_body):
    email_client = Email(None, None)
    body = email_client.parse_body_to_string(msg_body)
    code = email_client.get_verification_code(body)
    print(code)


def main():
    accounts = read_accounts('accounts.txt')
    config = load_config('config.json')
    interval = config['interval']
    ding_robot_id = config['ding_robot_id']
    ding_secret = config['ding_secret']

    dingding = DingDingInstance(robot_id=ding_robot_id, secret=ding_secret)

    def send_ding_notify(msg_body):
        email_client = Email(None, None)
        body = email_client.parse_body_to_string(msg_body)
        print(body)
        dingding.send_dingding_msg(body)

    for email, password in accounts:
        email_client = Email(email, password)

        # Define a custom monitor_new_emails function with the desired interval
        def custom_monitor_new_emails(self, folder='INBOX', callback=None):
            self.server.select_folder(folder)
            previous_messages = self.server.search('ALL')

            while True:
                print('custom_monitor_new_emails')
                time.sleep(interval)  # Use the interval value from config.json
                current_messages = self.server.search('ALL')

                if len(current_messages) > len(previous_messages):
                    new_message_id = list(set(current_messages) - set(previous_messages))[0]
                    msg_data = self.server.fetch([new_message_id], ['ENVELOPE', 'BODY[TEXT]'])
                    msg_body = msg_data[new_message_id][b'BODY[TEXT]']
                    if callback:
                        callback(msg_body)
                    return msg_body

                previous_messages = current_messages

        # Replace the original monitor_new_emails method with the custom one
        email_client.monitor_new_emails = custom_monitor_new_emails.__get__(email_client, Email)

        email_client.monitor_new_emails(
            callback=send_ding_notify)  # or use callback=print_verification_code for verification code


if __name__ == "__main__":
    main()
