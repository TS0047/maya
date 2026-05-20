import random as rand
import time
def load_animation():
    for i in range(0,rand.randint(3,7)):
        print("\033[H\033[J", end="")
        num = (i%3)+1
        print("*"*num)
        time.sleep(rand.randint(1,3))