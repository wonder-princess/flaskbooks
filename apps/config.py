from pathlib import Path

basedir = Path(__name__).parent.parent

class BaseConfig:
    SECRET_KEY = "pass8888"
    WTF_CSRF_SECRET_KEY="pass8888"
    UPLOAD_FOLDER = str(Path(basedir, "apps", "images"))

class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(__file__).parent.parent / 'test.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

config = {
    "testing": TestingConfig,
    "local": LocalConfig,
}
