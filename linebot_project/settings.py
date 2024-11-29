import os
from pathlib import Path
from dotenv import load_dotenv

# 加載 .env 文件
# 確保加載正確的 .env 文件
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 基本設定
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DJANGO_ENV") == "development"
ENVIRONMENT = os.getenv("DJANGO_ENV", "development")
# https://rainshine-grace.vercel.app/rainshinegrace/callback
if ENVIRONMENT == "production":
    ALLOWED_HOSTS = ["rainshine-grace.vercel.app"]
else:
    ALLOWED_HOSTS = ["*"]
# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("NEW_LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("NEW_LINE_CHANNEL_SECRET")

# 其他設定
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 應用程式和中介軟體
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.rainshinegrace.apps.RainshineGraceConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL 和 WSGI 設定
ROOT_URLCONF = "linebot_project.urls"
WSGI_APPLICATION = "linebot_project.wsgi.application"

# 模板設定
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 語言和時區
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# 靜態檔案（目前不需要）
STATIC_URL = "static/"
STATICFILES_DIRS = os.path.join(BASE_DIR, "static"),
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')
