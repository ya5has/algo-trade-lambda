def func1():
    print('hola')

def func2():
    print('hello')

commands = {
    'func1':func1,
    'func2':func2
}
commands['func2']()

if ('func1' in commands):
    print('true')