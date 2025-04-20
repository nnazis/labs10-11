import psycopg2
import csv
con = psycopg2.connect(
    dbname='phone_book_2',
    user='postgres',
    password='KBTU_naz2024',
    host='localhost',
    port='5432'
)
cur = con.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS phone_book(
        id SERIAL PRIMARY KEY,
        firstname VARCHAR(256),
        surname VARCHAR(256),
        phone VARCHAR(256)
    );
''')
cur.execute('''
    CREATE OR REPLACE FUNCTION search_by_pattern (pattern VARCHAR) 
RETURNS TABLE(id INTEGER, firstname VARCHAR, surname VARCHAR, phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT pb.id, pb.firstname, pb.surname, pb.phone
    FROM phone_book pb
    WHERE pb.firstname ILIKE '%' || pattern || '%' 
    OR pb.surname ILIKE '%' || pattern || '%' 
    OR pb.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

''')
cur.execute('''
    CREATE OR REPLACE PROCEDURE insert_phone (username VARCHAR, usersurname VARCHAR, userphone VARCHAR)
    AS $$
    BEGIN 
        IF EXISTS (SELECT 1 FROM phone_book WHERE firstname = username AND surname = usersurname) THEN 
            UPDATE phone_book 
            SET phone = userphone 
            WHERE firstname = username AND surname = usersurname;
        ELSE
            INSERT INTO phone_book (firstname, surname, phone) 
            VALUES (username, usersurname, userphone);
        END IF;
    END;
    $$ LANGUAGE plpgsql;
''')
cur.execute('''
    CREATE OR REPLACE PROCEDURE insert_many (usernames VARCHAR[], usersurnames VARCHAR[], userphones VARCHAR[])
    AS $$
    DECLARE 
        i INTEGER := 1;
    BEGIN 
        WHILE i <= array_length(usernames, 1) LOOP
            CALL insert_phone(usernames[i], usersurnames[i], userphones[i]);
            i := i + 1;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
''')
cur.execute('''
    CREATE OR REPLACE FUNCTION get_phones_with_pagination(lim INTEGER, off INTEGER) 
    RETURNS TABLE(id INTEGER, firstname VARCHAR, surname VARCHAR, phone VARCHAR)
    AS $$
    BEGIN
        RETURN QUERY
        SELECT * FROM phone_book ORDER BY id LIMIT lim OFFSET off;
    END;
    $$ LANGUAGE plpgsql;
''')
cur.execute('''
    CREATE OR REPLACE PROCEDURE delete_by_name_and_surname(username VARCHAR, usersurname VARCHAR)
    AS $$
    BEGIN
        DELETE FROM phone_book WHERE firstname = username AND surname = usersurname;
    END;
    $$ LANGUAGE plpgsql;
''')
con.commit()
def insert(name, surname, phone):
    cur.execute(
        'INSERT INTO phone_book(firstname, surname, phone) VALUES (%s, %s, %s)', (name, surname, phone)
    )
    con.commit()

def update(id, name, surname, phone):
    cur.execute(
        'UPDATE phone_book SET firstname=%s, surname=%s, phone=%s WHERE id=%s', (name, surname, phone, id)
    )
    con.commit()

def getById(id):
    cur.execute('SELECT * FROM phone_book WHERE id=%s', (id,))
    return cur.fetchone()

def getAll(asc=True):
    cur.execute('SELECT * FROM phone_book ORDER BY id ' + ('ASC' if asc else 'DESC'))
    return cur.fetchall()

def delete(value):
    cur.execute(
        'DELETE FROM phone_book WHERE firstname=%s OR phone=%s', (value, value)
    )
    con.commit()

def insertFromConsole():
    name = input("Enter first name: ")
    surname = input("Enter surname: ")
    phone = input("Enter phone number: ")
    insert(name, surname, phone)
    print('New phone added!')

def insertFromCsv():
    with open('phones.csv', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            insert(row[0], row[1], row[2])  # name, surname, phone

def updateFromConsole():
    id = input("Enter ID of the record to update: ")
    row = getById(id)
    if row is None:
        print('No such row')
        return
    name = input(f"Enter name [{row[1]}]: ") or row[1]
    surname = input(f"Enter surname [{row[2]}]: ") or row[2]
    phone = input(f"Enter phone [{row[3]}]: ") or row[3]
    update(id, name, surname, phone)
    print('Row updated!')

def printPhoneBook():
    user_input = int(input("Sort by: 1-ASC, 2-DESC: "))
    phone_book = getAll(asc=(user_input == 1))
    for row in phone_book:
        print(f'ID: {row[0]}, Name: {row[1]} {row[2]}, Phone: {row[3]}')

def deleteMenu():
    value = input("Enter name or phone to delete: ")
    delete(value)
    print('Deleted!')

def search_by_pattern():
    pattern = input("Enter search pattern: ")
    try:
        cur.execute('SELECT * FROM search_by_pattern(%s)', (pattern,))
        for row in cur.fetchall():
            print(f'ID: {row[0]}, Name: {row[1]} {row[2]}, Phone: {row[3]}')
    except Exception as e:
        print("Search failed:", e)
        con.rollback()

def insert_or_update():
    name = input("Enter first name: ")
    surname = input("Enter surname: ")
    phone = input("Enter phone number: ")
    cur.execute('CALL insert_phone(%s, %s, %s)', (name, surname, phone))
    con.commit()

def get_with_pagination():
    lim = int(input("Limit: "))
    off = int(input("Offset: "))
    cur.execute('SELECT * FROM get_phones_with_pagination(%s, %s)', (lim, off))
    for row in cur.fetchall():
        print(f'ID: {row[0]}, Name: {row[1]} {row[2]}, Phone: {row[3]}')

def delete_by_name_and_surname_menu():
    name = input("Enter first name: ")
    surname = input("Enter surname: ")
    try:
        cur.execute('CALL delete_by_name_and_surname(%s, %s)', (name, surname))
        con.commit()
        print('Successfully deleted using procedure!')
    except Exception as e:
        print("Delete failed:", e)
        con.rollback()
run = True
while run:
    try:
        user_input = int(input("""
Choose option:
1 - Insert via console
2 - Insert from CSV
3 - Update from console
4 - Print phone book
5 - Delete row
6 - Insert or update
7 - Search by pattern
8 - Paginated output
9 - Delete using procedure (name + surname)
0 - Exit
> """))
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
        elif user_input == 6:
            insert_or_update()
        elif user_input == 7:
            search_by_pattern()
        elif user_input == 8:
            get_with_pagination()
        elif user_input == 9:
            delete_by_name_and_surname_menu()
        elif user_input == 0:
            run = False
        else:
            print("Invalid option")
    except Exception as e:
        print("Error:", e)
        
cur.close()
con.close()