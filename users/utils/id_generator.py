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
    with open('users/utils/bad-words.txt', 'r') as file:
        bad_words = file.readlines()
    all_letters = generator_letters()
    while True:
        random_string = generate_random_characters(k, all_letters)
        found_bad_word = False
        for word in bad_words:
            if word in random_string:
                found_bad_word = True
                break
        if not found_bad_word:
            id += random_string
            break
    return id
