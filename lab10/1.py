import psycopg2
import csv


con = psycopg2.connect(
    dbname='lesson_phone_book',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432'
)

cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS phone_book('
            'id SERIAL PRIMARY KEY,'
            'name VARCHAR(256),'
            'phone VARCHAR(256)'
            ');'
)

con.commit()

def insert(name, phone):
    cur.execute(
        'INSERT INTO phone_book(name, phone) VALUES (%s, %s)', (name, phone)
    )
    con.commit()

def update(id, name, phone):
    cur.execute(
        'UPDATE phone_book SET name=%s, phone=%s WHERE id=%s', (name, phone, id)
    )
    con.commit()


def getById(id):
    cur.execute(
        'SELECT * FROM phone_book WHERE id=%s', (id)
    )
    return cur.fetchone()

def getAll(asc = True):
    sortDir = 'ASC'
    if not asc:
        sortDir = 'DESC'

    cur.execute(
        'SELECT * FROM phone_book ORDER BY id ' + sortDir
    )
    return cur.fetchall()

def getByName(name):
    cur.execute(
        "SELECT * FROM phone_book WHERE name='"+ name + "'"
    )
    return cur.fetchone()

def getByPhone(phone):
    cur.execute(
        'SELECT * FROM phone_book WHERE phone=%s', (phone)
    )
    return cur.fetchone()

def delete(value):
    cur.execute(
        'DELETE FROM phone_book WHERE name=%s OR phone=%s' , (value, value)
    )
    con.commit()

def insertFromConsole():
    name = input("Enter name: ")
    phone = input("Enter phone number: ")
    insert(name, phone)
    print('New phone added to phone book!')


def insertFromCsv():
    with open('phones.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            insert(row[0], row[1])


def updateFromConsole():
    id = input("Enter id of row: ")
    row = getById(id)
    if row is None:
        print('No such phone row')
        return

    name = input("Enter name: ")
    if name == '':
        name = row[1]

    phone = input("Enter phone number: ")
    if phone == '':
        phone = row[2]
    update(id, name, phone)
    print('Row updated successfully!')

def printPhoneBook():
    user_input = int(input("Enter sorting direction (1-ASC,2-DESC): "))
    phone_book = None
    if user_input == 2:
        phone_book = getAll(asc=False)
    else:
        phone_book = getAll()

    for row in phone_book:
        print(f'ID: {row[0]}, Name: {row[1]}, Phone number: {row[2]}')

def deleteMenu():
    value = input("Enter name or phone to delete: ")
    delete(value)
    print('Successfully deleted!')


run = True

while run:
    user_input = int(input("Chose option: 1 - insert via console, 2 - insert via csv, 3 - update from console, 4 - print phone book, 5 - delete row, 0 - close program\n"))
    if user_input == 1:
        insertFromConsole()
    elif user_input == 2:
        insertFromCsv()
    elif user_input == 3:
        updateFromConsole()
    elif user_input == 4:
        printPhoneBook()
    elif user_input == 5:
        deleteMenu()
    elif user_input == 0:
        run = False
    else:
        print("Invalid option")