import os

if __name__ == "__main__":
    os.system('rm -rf yodachannel/migrations')
    os.system('rm -rf db.sqlite3')
    os.system('python3 manage.py makemigrations yodachannel')
    os.system('python3 manage.py migrate')
    os.system('python3 manage.py runserver')
