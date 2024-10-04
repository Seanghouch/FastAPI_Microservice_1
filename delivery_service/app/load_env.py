from dotenv import load_dotenv

def load_environment():
    # set the current environment
    evn = 'production'

    # load the environment .env file
    if evn == 'development':
        load_dotenv('env/.env')
    elif evn == 'production':
        load_dotenv('env/.env.pro')
    elif evn == 'testing':
        load_dotenv('env/.env.test')
