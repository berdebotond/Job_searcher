import uvicorn


from modules.app.app import app
from modules.config.config import config


if __name__ == "__main__":

    uvicorn.run(app, host=config.HOST, port=config.PORT)
