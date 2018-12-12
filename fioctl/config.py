import os
import yaml

class Config():
    @property
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
        yaml.dump(config, open(self.filename, "w"))
    
    def fetch(self, scope, key=None):
        scope = self.config.get(scope, {})
        if not key:
            return scope
        
        return scope.get(key)

config = Config()

def nested_get(dic, mapList):    
    for k in mapList: 
      dic = dic[k]
    return dic

def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value