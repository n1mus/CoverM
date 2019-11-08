



def dprint(*args, **kwargs):
    print('##############################################################', flush=True)
    if isinstance(args[0], dict):
        pprint.pprint(args[0])
    print(*args, flush=True, **kwargs)





print = functools.partial(print, flush=True)

