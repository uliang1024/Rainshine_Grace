from django.apps import AppConfig

class RainshineGraceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rainshinegrace"

    def ready(self):
        # 在這裡放置初始化代碼
        print("RainshineGrace 應用程式已啟動")
