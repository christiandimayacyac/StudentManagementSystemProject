from django.apps import AppConfig


class SmsMainConfig(AppConfig):
    name = 'sms_main'

    def ready(self):
        import sms_main.signals


