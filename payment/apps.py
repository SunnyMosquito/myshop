from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PaymentConfig(AppConfig):
    name = 'payment'
    verbose_name = _('Payment')

    def ready(self):
        # import signal handlers
        from payment import signals
