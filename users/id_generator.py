import random
import string

def id_generator(user, k) -> str:
    id = str()
    if user.first_name:
        id += user.first_name
    if id != '' and id is not None and user.last_name:
        id += user.last_name
    print(id)
    file = open('users/bad-words.txt', 'r')
    badWords = file.readlines()
    file.close()
    allLeters = ''.join(string.ascii_letters + string.digits + '-')
    while True:
        randomString = ''.join(random.choices(allLeters, k=k))
        if randomString not in badWords:
            id += randomString
            break
    return id

