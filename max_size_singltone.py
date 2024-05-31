class __Singltone(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
            return class_._instance


class MaxSize(__Singltone):
    max_size = 10 * 1024 * 1024 * 1024


class YTLink(__Singltone):
    yt_link = "https://youtu.be/"