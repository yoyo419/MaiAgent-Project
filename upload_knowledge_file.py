from utils import MaiAgentHelper
from config import API_KEY, CHATBOT_ID
API_KEY = API_KEY

CHATBOT_ID = CHATBOT_ID
FILE_PATH = 'DP0001.txt'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CHATBOT_ID != '<your-chatbot-id>', 'Please set your chatbot id'
assert FILE_PATH != '<your-file-path>', 'Please set your file path'


def main():
    maiagent_helper = MaiAgentHelper(
        api_key=API_KEY,
        base_url='http://140.119.63.98:443/api/v1/',
        storage_url='https://nccu-ici-rag-minio.jp.ngrok.io/magt-bkt'
    )

    response = maiagent_helper.upload_knowledge_file(CHATBOT_ID, FILE_PATH)
    print(response)

if __name__ == '__main__':
    main()