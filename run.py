from app import create_app
from app.config import DevConfig

app = create_app(DevConfig)

if __name__ == '__main__':
    app.run()