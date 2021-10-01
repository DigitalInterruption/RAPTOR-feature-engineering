import yaml
import os

outDict = {'done':True}
with open('control/scheduler.yaml', 'w') as file:
    dump = yaml.dump(outDict, file)
