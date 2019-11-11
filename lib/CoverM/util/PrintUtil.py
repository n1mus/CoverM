import functools



def dprint(*args, **kwargs):
    print('##############################################################', flush=True)
    if isinstance(args[0], dict):
        pprint.pprint(*args, width=99999, **kwargs)
    print(*args, flush=True, **kwargs)
    print('--------------------------------------------------------------', flush=True)





print = functools.partial(print, flush=True)

