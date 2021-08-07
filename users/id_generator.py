import random
import string


def generator_letters() -> str:
    return ''.join(string.ascii_letters + string.digits + '-')

def generate_random_characters(length: int, letters: str) -> str:
    return ''.join(random.choices(letters, k=length))

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
    allLeters = generator_letters()
    while True:
        randomString = generate_random_characters(k, allLeters)
        if randomString not in badWords:
            id += randomString
            break
    return id

