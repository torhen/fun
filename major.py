import random, os

dict = {
    '0':'Sau', '1':'Tee', '2':'Noah', '3':'Mai', '4':'Reh', '5':'Lee', '6':'Schuh', '7':'Kuh', '8':'Fee', '9':'Po'
}
keys = list(dict.keys())
k, k_old = None, None
while True:
    while k == k_old:
        k = random.choice(keys)
    k_old = k
    os.system("cls")
    while True:
        w = input(f'{k} ')
        if w == dict[k]:
            break