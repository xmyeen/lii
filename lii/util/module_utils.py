# -*- coding:utf-8 -*-
#!/usr/bin/env Python
"""
    module_utils.py - 包相关功能函数
"""
import logging,inspect,pkgutil
import importlib.util

def is_module(o):
    return inspect.ismodule(o)

def is_imported(self, module_name):
    spec = importlib.util.find_spec(module_name)
    return True if spec else False

# def import_thing(self, module_name, name):
#     module = importlib.import_module(module_name)
#     return getattr(module, name)

def get_module_info(func_or_method_or_type):
    return inspect.getmodule(func_or_method_or_type).__name__, func_or_method_or_type.__name__

def import_submodule_recursively(module, is_pkg_useable = False):
    submodules = dict()

    for loader, submodule_name, is_pkg in pkgutil.walk_packages(module.__path__, module.__name__ + "."):
        try:
            if is_pkg_useable or not is_pkg:
                submodule = loader.find_module(submodule_name).load_module(submodule_name)
                submodules.update({ submodule_name : submodule })
        except BaseException as ex:
            logging.exception(f"Got exception when load this module of '{submodule_name}'")
        # for name in dir(module):
        #     obj = getattr(module, name)
        #     if isinstance(obj, type) and issubclass(obj, unittest.case.TestCase):
        #         exec ('%s = obj' % obj.__name__)
    return submodules

def import_module(*module_names, **kwargs):
    modules = dict()
    for module_name in module_names:
        try:
            m = importlib.import_module(module_name, **kwargs)
            modules.update({ module_name : m})
        except BaseException as ex:
            logging.exception(f"Got exception when load this module of '{module_name}'")
    return modules

def scan_module(*module_names):
    for name, module in import_module(*module_names).items():
        logging.info(f"Import modules: {name}")
        submodules = import_submodule_recursively(module)
        logging.info(f"Import submodules: {','.join(submodules.keys())}")
