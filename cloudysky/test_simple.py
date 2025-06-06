#!/usr/bin/env python3

import unittest
import subprocess
from subprocess import check_output
import requests
import socket
from time import sleep
from os import path
import zoneinfo
import random
from bs4 import BeautifulSoup
from gradescope_utils.autograder_utils.decorators import weight, number

AG = "."
if path.exists("manage.py"):
    AG = ".."
if path.exists("cloudysky/manage.py"):
    AG = "."
if path.exists("/autograder/submission/cloudysky/manage.py"):
    AG = "/autograder/submission"

# DEsired tests:
# /app/new_course  (HTML form/view to submit to createPost) PROVIDED
# /app/new_lecture (HTML form/view to submit to createComment) PROVIDED
# /app/dumpUploads   !!

# /app/createPost   (API endpoint for  new_course)
# /app/createComment  (API endpoint for  new_lecture)
# /app/DumpFeed      (diagnostic endpoint)
# TESTS FOR HTTP  200 or 201 response...  (4)
# TEST that row is actually added with valid input  (3)
# three tests with invalid input, something essential not defined (3)



CDT = zoneinfo.ZoneInfo("America/Chicago")
admin_data = {
                "email": "autograder_test@test.org",
                "is_admin": "1",
                "user_name": "Autograder Admin",
                "password": "Password123"
                }
user_data = {
                "email": "user_test@test.org",
                "is_admin": "0",
                "user_name": "Tester Student",
                "password": "Password123"
                }

bunnytweets = [
    "A bunny in your lap = therapy.", "A bunny is a cloud with ears.", "Adopt a bunny, gain calm.", "Anxious but adorable: the bunny way.", "Baby bunny yawns cure sadness.", "Bunnies are living plush toys.", "Bunnies don't bite, they bless.", "Bunnies nap like tiny gods.", "Bunny feet are pure poetry.", "Bunny loaf = floof perfection.", "Bunny silence speaks comfort.", "Ears up, stress down.", "Flop = bunny trust unlocked.", "Floppy ears fix bad moods.", "Fuzzy bunnies are peace in tiny, hopping form.", "Holding a bunny resets your soul.", "Hops heal hearts.", "Nose wiggles say 'I love you.'", "One bunny = less chaos.", "Quiet, cute, and salad-powered.", "Rabbits know the secret to rest.", "Snuggle-powered peace generator.", "Soft bunny = instant calm.", "Soft, silent, and perfect.", "Tiny paws, huge joy."
]



class TestDjangoHw5simple(unittest.TestCase):
    '''Test functionality of cloudysky API'''
    server_proc = None

    @classmethod
    def wait_for_server(cls):
        for _ in range(100):
            try:
                r = requests.get("http://localhost:8000/", timeout=1)
                if r.status_code < 500:
                    return
            except:
                sleep(0.2)
        raise RuntimeError(f"Server did not start within 20 seconds")


    @classmethod
    def start_server(cls):
        if cls.server_proc and cls.server_proc.poll() is None:
            return  # Already running

        print("Starting Django server...")
        cls.server_proc = subprocess.Popen(
            ['python3', AG + '/cloudysky/manage.py',
                      'runserver', '--noreload'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        cls.wait_for_server()
   
    @classmethod
    def setUp(cls):
        cls.start_server()  # start or restart if needed
        cls.wait_for_server()  # confirm it's responsive
 
    @classmethod
    def get_csrf_login_token(self, session=None):
        if session is None:
            session = requests.Session()
        response0 = session.get("http://localhost:8000/accounts/login/")
        csrf = session.cookies.get("csrftoken")
        if csrf:
            csrfdata = csrf
        else:
            print("ERROR: Can't find csrf token in accounts/login/ page")
            csrfdata = "BOGUSDATA"
        self.csrfdata = csrfdata
        self.loginheaders = {"X-CSRFToken": csrfdata, "Referer":
                "http://localhost:8000/accounts/login/"}
        return session, csrfdata   # session

    @classmethod
    def setUpClass(cls):
        '''This class logs in as an admin, and sets
        cls.session  to have the necessary cookies to convince the
        server that we're still logged in.
        '''
        print("starting server")
        try:
            cls.start_server()
        # Make sure server is still running in background, or error
            cls.wait_for_server()
            if cls.server_proc.poll() is not None:  # if it has terminated
                stdout, stderr = cls.server_proc.communicate()
                message = ("Django server crashed on startup.\n\n" +
                   f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
                if "already in use" in message:
                    message =  ("Django server crashed on startup. " +
                       f"{stderr.split('\n')[1]}")
                raise RuntimeError(message)
        except Exception as e:
              assert False, str(e)

        def login(data):
            response = requests.post("http://localhost:8000/app/createUser",
                                     data=data,
                                     )
            print("CreateUser status", response.status_code)
            session, csrfdata = cls.get_csrf_login_token()
            logindata = {"username": data["user_name"],
                     "password": data["password"],
                     "csrfmiddlewaretoken": csrfdata}
            loginheaders = {"X-CSRFToken": csrfdata, "Referer":
                            "http://localhost:8000/accounts/login/"}
            response1 = session.post("http://localhost:8000/accounts/login/",
                        data=logindata,
                        headers=loginheaders)
            print("LOGINDATA", logindata)
            print("LOGINHEADERS", loginheaders)
            print("LOGINCODE", response1.status_code)
            print("LOGINRESPNSE", response1.text)
            if "Please enter a correct username" in response1.text:
                print("Oh, this is bad, login failed")
            return session, loginheaders, csrfdata
#       Now we can use self.session  as a logged-in requests object.
        cls.session_admin, cls.headers_admin, cls.csrfdata_admin = login(admin_data)
        cls.session_user, cls.headers_user, cls.csrfdata_user = login(user_data)

    @classmethod
    def tearDownClass(cls):
        print("Stopping Django server...")
        proc = getattr(cls, 'server_proc', None)
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Server did not terminate in time; killing it.")
                proc.kill()
                proc.wait()


    def count_app_rows(self):
        '''Counts all the rows in sqlite tables beginning
        with "app", to confirm that rows are being added.
        '''
        if not path.exists("cloudysky/db.sqlite3") and not path.exists('db.sqlite3'):
            raise AssertionError("Cannot find cloudysky/db.sqlite3 or db.sqlite3, this test isn't going to work")
        if path.exists("db.sqlite3"):
            db_location = "db.sqlite3"
        elif path.exists("cloudysky/db.sqlite3"):
            db_location = "cloudysky/db.sqlite3"
        else:
            self.assertionError("Can't find cloudysky/db.sqlite3, this test won't work")
        print("LOOKING AT", db_location) 
        tables = check_output(["sqlite3", db_location,
            "SELECT name FROM sqlite_master WHERE type='table';"]).decode().split("\n")
        print("TABLES", tables)
        apptables = [str(table) for table in tables if table[0:3] == 'app']
        print("APPTABLES", apptables)
        n = 0
        for apptable in apptables:
            contents = check_output(["sqlite3", db_location,
                "SELECT * from " + apptable]).decode().split()
            n += len(contents)
            print("Apptable", apptable, len(contents), "rows")
        return n

    # ... (rest of the test class as provided) ... 