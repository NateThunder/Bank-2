import sqlite3
import datetime
import os
import time
#-------------- connect to databse ----------------------------
conn = sqlite3.connect("bankers.db")
cursor = conn.cursor()

#----------- Do you have an account? --------------------------
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
            pin = int(input("What is your 4 digit pin?: "))
        except:
            print("Big man, the pin has to be a 4 digit number bruv!")
        try:
            if len(str(pin))==4:
                print("My driller!")
                cursor.execute("SELECT pin FROM customer WHERE pin = ?", (pin,))
                break
            else:
                print("BIG MAN, 4 DIGIT PIN!")
                continue
        except:
            print("BIG MAN, 4 DIGIT PIN!")
    cursor.execute("INSERT INTO customer (name, pin) VALUES (?, ?)", (name, pin))
    conn.commit()

#----------- Lock account --------------------------------------
def account_lock(name):
    cursor.execute("SELECT attempts FROM customer WHERE name = ?", (name,))
    if cursor.fetchone()[0] >= 3:
        print("Account locked. Please contact customer service.")
        exit()

#----------- Log in -------------------------------------------
def login():
    while True:   
        name = input("What is your name?: ")
        cursor.execute("SELECT name FROM customer WHERE name = ?", (name,))
        if cursor.fetchone():
            break
        else:
            option = input("We dont have that username famalam, you wanna try again? Y for yes N for no?: ").capitalize()
            if option == "Y":
                pass
            elif option =="N":
                break
            else:
                print("That is not an option braaaaav! Stop taking the mick, end of programme.")
                break

    account_lock(name)           
    while True:
        pin = int(input("What is your pin?: ")) #ask for pin
        cursor.execute("SELECT pin FROM customer WHERE pin = ? AND name = ?", (pin, name)) #find pin
        if cursor.fetchone():
            account_lock(name)
            print("login succesful bruv!")
            cursor.execute("UPDATE customer SET attempts = ? WHERE name = ?", (0, name))
            conn.commit()
            return name
        else:
            print("wierdo! Wrong password")
        # Attempt counter
            cursor.execute("SELECT attempts FROM customer WHERE name = ?", (name,))
            result = cursor.fetchone()
            attempts = result[0]
            if attempts >= 3:
                print("Account locked")
                main()
            else:
                attempts += 1

        cursor.execute("UPDATE customer SET attempts = ? WHERE name = ?", (attempts, name))
        conn.commit()
        #return name

#-------------- show transactions -------------------------------
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
    
#------------------ time -----------------------------------------
def date():
    now = datetime.datetime.now()
    formatted = now.strftime("%d/%m/%Y %H:%M")
    return formatted

#------------------ transaction ------------------------------------
def transactions(name):
    cursor.execute("SELECT id FROM customer WHERE name = ?", (name,))

    while True:
        action =  input("Type W for withdraw, D for deposite, T for transactions: ").capitalize()
        if action == "W":
            amount = f"{float(input("How much would you like to withdraw?: ")):.2f}"

            withdrawal(float(amount), name)
            break
        elif action == "D":
            amount = f"{float(input("How much would you like to deposite?: ")):.2f}"
            deposite(float(amount), name)
            break
        elif action =="T":
            history(name)
            break
        else:
            option = input("Do you want to continue? Y for yes, other for no: ").capitalize()
            if option == "Y":
                continue
            else:
                break

#------------------ Deposite money ----------------------------        
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

#--------- Withdraw money --------------------------------
def withdrawal(amount, name):
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


def main():
    #os.system("cls")
#-------------------------------- Welcome message -------------------------------------------------------------------------
    print("Welcome to Dope A F bank. The home of your banking needs")
    name = login()
    while True:
        transactions(name)
        fin = input("Do you want this programme to end Y for yes and N for no: ").capitalize()
        if fin == "Y":
            break
        else:
            continue
    print("Thanks for usin Dope A F Bank! Bye!!!")
    time.sleep(2)

while True:

    os.system("cls")
    main()
