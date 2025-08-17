import random, os

dict = {
    '0':'Sau', '1':'Tee', '2':'Noah', '3':'Mai', '4':'Reh', '5':'Lee', '6':'Schuh', '7':'Kuh', '8':'Fee', '9':'Po'
}
keys = list(dict.keys())
k, k_old = None, None

ncount = 0
while True:
    ncount += 1
    while k == k_old:
        k = random.choice(keys)
    k_old = k
    os.system("cls")


    while True:
        if ncount // 10 % 2 == 0:
            r = input(f'{k} ')
            if r == dict[k]:
                break
        else:
            r = input(f'{dict[k]} ')
            if r == k:
                break        