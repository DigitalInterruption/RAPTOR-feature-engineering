import yaml

initDict = {'done':False}
with open('control/scheduler.yaml', 'w') as file:
    params = yaml.dump(initDict, file)
