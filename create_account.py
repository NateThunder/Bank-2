import sqlite3
import datetime
import os
import time
import platform
import msvcrt
#-------------- connect to databse --------------------------------
conn = sqlite3.connect("bankers.db")
cursor = conn.cursor()

#----------- Do you have an account? ------------------------------
def create_account():
    while True:
        try:
            name = input("Please choose a username: ")
            cursor.execute("SELECT name FROM customer WHERE name = ?", (name,))
            if cursor.fetchone():
                print("Sorry broski, username is already chosen")
            else:
                break
        except:
            print("Sorry broski, username is already chosen")
    while True:
        try:
            pin = int(input("Choose your 4 digit pin fam: "))
        except:
            print("Big man, the pin has to be a 4 digit number bruv!")
        try:
            if len(str(pin))==4:
                print("My driller!")
                cursor.execute("SELECT pin FROM customer WHERE pin = ?", (pin,))
                clear_screen(2)
                break
            else:
                print("BIG MAN, 4 DIGIT PIN!")
                continue
        except:
            print("BIG MAN, 4 DIGIT PIN!")
    cursor.execute("INSERT INTO customer (name, pin) VALUES (?, ?)", (name, pin))
    conn.commit()

    cursor.execute("SELECT id FROM customer WHERE name = ?", (name,))
    customer_id = cursor.fetchone()
    #print(customer_id[0])
    cursor.execute("""
    INSERT INTO transactions (customer_id, deposite, withdrawal, balance, date)
    VALUES (?, ?, ?, ?, ?);
    """, (customer_id[0], 0.00, 0.000, 0.00, date()))
    conn.commit()
    
    print(f"Thanks for creating an account {name}")
    clear_screen(2)

#----------- Masked pin entry -------------------------------------
def mask_pin(length):
    os.system("cls")
    digits = []
    x=0
    for dig in range(length):
        
        print(f"Enter your {length}-digit pin: ", "*" * x, end="", flush=True)
        key = msvcrt.getch()

        os.system("cls")
        digits.append(key.decode())
        x +=1
    print("Enter your 4-digit pin: ", "*" * x, end="", flush=True)

    pin = int("".join(digits))
    return pin
#----------- Lock account -----------------------------------------
def account_lock(name):
    cursor.execute("SELECT attempts FROM customer WHERE name = ?", (name,))
    if cursor.fetchone()[0] >= 3:
        print("Account locked. Please contact customer service.")
        clear_screen(2)
        main()

#----------- Log in -----------------------------------------------
def login():
    while True:   
        name = input("What is your name?: ")
        cursor.execute("SELECT name FROM customer WHERE name = ?", (name,))
        if cursor.fetchone():
            break
        else:
            option = input("We dont have that username famalam, you wanna try again? Y for yes N for no?: ").capitalize()
            if option == "Y":
                clear_screen(2)
                pass
            elif option =="N":
                clear_screen(2)
                break
            else:
                print("That is not an option braaaaav! Stop taking the mick, end of programme.")
                clear_screen(2)
                main()

    account_lock(name)           
    while True:
        pin = mask_pin(4) #ask for pin
        cursor.execute("SELECT pin FROM customer WHERE pin = ? AND name = ?", (pin, name)) #find pin
        clear_screen(0)
        if cursor.fetchone():
            account_lock(name)
            print("login succesful bruv!")
            clear_screen(1)
            cursor.execute("UPDATE customer SET attempts = ? WHERE name = ?", (0, name))
            conn.commit()
            return name
        else:
            print("weirdo! Wrong password")
            clear_screen(1)
        # Attempt counter
            cursor.execute("SELECT attempts FROM customer WHERE name = ?", (name,))
            result = cursor.fetchone()
            attempts = result[0]
            if attempts >= 3:
                print("Account locked")
                clear_screen(2)
                main()
            else:
                attempts += 1

        cursor.execute("UPDATE customer SET attempts = ? WHERE name = ?", (attempts, name))
        conn.commit()

        #return name

#-------------- show transactions ---------------------------------
def history(name):
    # Get customer ID
    cursor.execute("SELECT id FROM customer WHERE name = ?", (name,))
    result = cursor.fetchone()

    customer_id = result[0]
    print(f"Customer ID: {customer_id}")

    # Fetch only this customer's transactions
    cursor.execute("""
    SELECT customer.name, transactions.*
    FROM transactions
    JOIN customer ON transactions.customer_id = customer.id
    WHERE customer.id = ?
    """, (customer_id,))

    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"Deposite: {row[3]} | Withdrawal: {row[4]:.2f} | Balance: {row[5]:.2f} | Time: {row[6]}")
    else:
        print("No transactions found for this user.")
    return
    
#------------------ time ------------------------------------------
def date():
    now = datetime.datetime.now()
    formatted = now.strftime("%d/%m/%Y %H:%M")
    return formatted

#--------------- clear screen -------------------------------------
def clear_screen(x):
    time.sleep(x)
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

#------------------ transaction ------------------------------------
def transactions(name):
    cursor.execute("SELECT id FROM customer WHERE name = ?", (name,))
    
    while True:
        action =  input("Type W for withdraw, D for deposite, T for transactions: ").capitalize()
        if action == "W":
            clear_screen(0)
            amount = f"{float(input("How much would you like to withdraw?: ")):.2f}"

            withdrawal(float(amount), name)
            break
        elif action == "D":
            clear_screen(0)
            amount = f"{float(input("How much would you like to deposite?: ")):.2f}"
            deposite(float(amount), name)
            break
        elif action =="T":
            clear_screen(0)
            history(name)
            break
        else:
            option = input("Do you want to continue? Y for yes, other for no: ").capitalize()
            clear_screen(0.2)
            if option == "Y":
                continue
            else:
                break

#------------------ Deposite money --------------------------------        
def deposite(amount, name):
    cursor.execute("SELECT id FROM customer WHERE name = ?", (name,))
    customer_result = cursor.fetchone()

#----------- geting latest balance amount ----------
    if customer_result:
        customer_id = customer_result[0]
        
        # Step 2: Get most recent transaction for this customer
        cursor.execute("""
            SELECT balance, date 
            FROM transactions 
            WHERE customer_id = ? 
            ORDER BY transaction_id DESC 
            LIMIT 1
        """, (customer_id,))
        
        latest_transaction = cursor.fetchone()
        #print(f"balance: £{latest_transaction[0]:.2f} | Time: {latest_transaction[1]}")
    else:
        latest_transaction = None
        print(latest_transaction)


#------------ updating table --------------------    
    total = latest_transaction[0] + amount
    cursor.execute("""
    INSERT INTO transactions (customer_id, deposite, balance, date)
    VALUES (?, ?, ?, ?);
    """, (customer_id, amount, total, date()))
    conn.commit()

    cursor.execute("""
        SELECT balance, date, deposite 
        FROM transactions 
        WHERE customer_id = ?
        ORDER BY transaction_id DESC 
        LIMIT 1 
    """, (customer_id,))
    latest_transaction = cursor.fetchone()
    print(f"You depositd: £{latest_transaction[2]:.2f} | balance: £{latest_transaction[0]:.2f} | Time: {latest_transaction[1]}")

#------------------- Withdraw money -------------------------------
def withdrawal(amount, name):
    cursor.execute("SELECT id FROM customer WHERE name = ?", (name,))
    customer_result = cursor.fetchone()

#----------- geting latest balance amount ---------------------------
    if customer_result:
        customer_id = customer_result[0]
        
        # Step 2: Get most recent transaction for this customer
        cursor.execute("""
            SELECT balance, date 
            FROM transactions 
            WHERE customer_id = ? 
            ORDER BY transaction_id DESC 
            LIMIT 1
        """, (customer_id,))
        
        latest_transaction = cursor.fetchone()
    else:
        latest_transaction = None
        print(latest_transaction)


#------------ updating table --------------------------------------------------    
    total = latest_transaction[0] - amount
    cursor.execute("""
    INSERT INTO transactions (customer_id, withdrawal, balance, date)
    VALUES (?, ?, ?, ?);
    """, (customer_id, amount, total, date()))
    conn.commit()

    cursor.execute("""
        SELECT balance, date, withdrawal 
        FROM transactions 
        WHERE customer_id = ?
        ORDER BY transaction_id DESC 
        LIMIT 1 
    """, (customer_id,))
    latest_transaction = cursor.fetchone()
    print(f"You withdrew: £{latest_transaction[2]:.2f} | balance: £{latest_transaction[0]:.2f} | Time: {latest_transaction[1]}")

#------------------ main programm ----------------------------------
def main():
    clear_screen(0)
#-------------------------------- Welcome message -------------------------------------------------------------------------
    choice = input("Welcome to Dope A F bank. The home of your banking needs. Do you have an account? (Y/N): ").capitalize()
    if choice == "Y":  
        name = login()
        while True:
            transactions(name)
            fin = input("Do you want something else?(Y/N): ").capitalize()
            clear_screen(0.1)
            if fin == "N":
                break
            else:
                continue
        print("Thanks for usin Dope A F Bank! Bye!!!")
        time.sleep(2)
    elif choice == "N":
        create_account()
    else:
        print("Hey buddy that is not a choice (Y/N)!")
        clear_screen(2)
        main()

while True:
    clear_screen(0)
    main()