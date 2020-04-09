import mmh3



def rehash_baseh62(the_url_str):
    ls = [str(item) for item in range(10)]

    for item in range(65, 91):
        ls.append(chr(item))

    for item in range(97, 123):
        ls.append(chr(item))

    res = []
    import mmh3
    num = mmh3.hash(the_url_str, signed=False)
    while num:
        res.insert(0, ls[num%62])
        num = num // 62

    return ''.join(res)


txt = 'https://www.sogou.com/web?ie=UTF-8&query=flask+debug%3DTrue'
res = rehash_baseh62(txt)
print(txt)
print(res)



import random

txt += ('&randomk=' + str(random.random()))
print(txt)
res = rehash_baseh62(txt)
print(res)