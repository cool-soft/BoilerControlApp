__dependency_list = {}


def get_dependency(class_):
    if class_ in __dependency_list:
        return __dependency_list[class_]


def add_dependency(obj):
    __dependency_list[obj.__class__] = obj
