import os
import stat
import yaml
from cached_property import cached_property

class Config():
    @cached_property
    def config(self):
        if self.exists:
            return yaml.load(open(self.filename))
        return {}

    @property
    def filename(self):
        return os.path.expanduser("~/.fioctl.yml")

    @property
    def exists(self):
        return os.path.isfile(self.filename)

    def set_config(self, scope, key, value):
        config = self.config
        nested_set(config, [scope, key], value)
        yaml.dump(config, open(self.filename, "w"), default_flow_style=False)
        os.chmod(self.filename, stat.S_IRWXU)
    
    def fetch(self, scope, key=None):
        scope = self.config.get(scope, {})
        if not key:
            return scope
        
        return scope.get(key)

config = Config()

def column_default(module, default):
    columns = config.fetch(module, 'columns') or default
    if isinstance(columns, list):
        return columns
    
    return [col.strip() for col in columns.split(",")]

def nested_get(dic, mapList):    
    for k in mapList: 
        dic = dic.get(k)
        if not dic:
            return dic

    return dic

def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def nested_move(dic, from_keys, move_keys):
    val = nested_get(dic, from_keys)
    if not val:
        return dic
    
    nested_set(dic, move_keys, val)
    return dic
    