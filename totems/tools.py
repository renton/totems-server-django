from random import randrange

def gen_random_long_lat():
    longitude = randrange(-180,180)
    latitude = randrange(-90,90)

    return (longitude,latitude)
