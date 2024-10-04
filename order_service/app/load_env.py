from dotenv import load_dotenv

def load_environment():
    # set the current environment
    evn = 'development'

    # load the environment .env file
    if evn == 'development':
        load_dotenv('env/.env.dev')
    elif evn == 'production':
        load_dotenv('env/.env.pro')
    elif evn == 'testing':
        load_dotenv('env/.env.test')
