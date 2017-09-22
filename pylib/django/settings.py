from django.conf import settings


__all__ = ['get_setting']


setting_pool = [settings]

if 'constance' in settings.INSTALLED_APPS:
    try:
        from constance import config as constance_config
        setting_pool.append(constance_config)
    except ImportError:
        pass


def get_setting(key, default=None):
    res = default
    for setting in setting_pool:
        if hasattr(setting, key):
            res = getattr(setting, key)
    return res
