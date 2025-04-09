import msvcrt
import os

def mask_pin(length):
    os.system("cls")
    digits = []
    x=0
    for dig in range(length):
        
        print("Enter your 4-digit pin: ", "*" * x, end="", flush=True)
        key = msvcrt.getch()

        os.system("cls")
        digits.append(key.decode())
        x +=1
    print("Enter your 4-digit pin: ", "*" * x, end="", flush=True)

    pin = int("".join(digits))
    return pin

print(f"\n{mask_pin(4)}")

