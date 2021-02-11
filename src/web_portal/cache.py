class CachedData:
    """
    A simple class that only
    stores a variable used as a cache
    """
    __cached = None

    def set_cache(self, new_data):
        self.__cached = new_data

    def get_cache(self):
        return self.__cached

    def reset_cache(self):
        self.__cached = None
