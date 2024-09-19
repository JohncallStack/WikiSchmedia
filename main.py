
import mysql.connector
from mysql.connector import Error
from mysqlx import connection
from werkzeug.utils import redirect
import paramiko
from flask import Flask, render_template, request, url_for, flash

app = Flask(__name__)
app.config['ENV'] = "Development"
app.config['DEBUG'] = True

# Configuration to connect to SQL Database.
host = '192.168.56.10'
port = 7888
database = 'WIKICACHE'
user = 'root'
password = 'mypassword'


# renders search page html
@app.route('/')
def home():
    return render_template("index.html")


# Function to connect to SQL Database.
def connect_to_mysql():
    try:
        # Some code so I could track the connection in the terminal to troubleshoot.
        print("Connecting to MySQL server...")
        print(f"Host: {host}, Port: {port}, Database: {database}, User: {user}")
        # Connection code using the configuration written above.
        return mysql.connector.connect(host=host, port=port, database=database, user=user, password=password)
    except Error as e:
        print("Error while connecting to MySQL:", e)
        return None


# Main conditional search function.
@app.route('/search', methods=['POST'])
def search():
    searchTerm = request.form['search']
    result = None #Initialize result to prevent error

    # We need to first check if searched item has been inputted before.
    # First connect to MySQL on VM.
    connection = connect_to_mysql()
    if connection:
        try:
            #Check if the searchquery is present in the table SEARCHRESULTS.
            searchquery = "SELECT result FROM SEARCHRESULTS WHERE query = %s"
            print(searchquery)
            print("Checking Database for search query")
            cursor = connection.cursor()
            cursor.execute(searchquery, (searchTerm,))
            result = cursor.fetchone()  #Returns next row in the database of our searchterm/query, so the result of the search.
            cursor.close()
        except Error as e:
            print("Error executing query:", e)
        finally:
            connection.close()

    #Conditional statement to give a command on if the searched item is there or not.
    #If present render the SearchResults HTML with the cached item from the DB.
    if result:
        print("Query Found, return result from database")
        paragraphs = result[0].split('\n\n') # FOR FORMATTING: splits the resulting content into paragraphs where 2 new lines are present.
        return render_template("searchResults.html", output=paragraphs, search_term=searchTerm) # Pass variables to html searchResults.

    #If not launch the function perform-search with the searched term.
    else:
        print("Query not in database, use EC2 VM to perform wiki.py search")
        # Perform the search on the EC2 VM using perform_search() function.
        search_result = perform_search(searchTerm)

        if search_result:
            # Then save search result to database
            print("Save result to database")
            save_to_database(searchTerm, search_result)
            # And pass variable to html as above.
        print("Display new result on HTML")
        return render_template("searchResults.html", output=search_result, search_term=searchTerm)

def perform_search(search_term):
    instance_ip = "18.201.118.73" #Amazon EC2 public IP address NOTE will change everytime you shut down and launch instance.
    securityKeyFile = "/home/student/CT5169.pem" #Location of security key you use to access Amazon web services.
    searchTerm = request.form['search'] #searchterm inputted by the user.
    cmd = "python3 wiki.py" #this is the command that runs the python script - wiki.py.
    try:
        # Connect/ssh to an instance
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = paramiko.RSAKey.from_private_key_file(securityKeyFile)
        client.connect(hostname=instance_ip, username="ubuntu", pkey=key)

        # Execute a command(cmd) after connecting/ssh to an instance
        stdin, stdout, stderr = client.exec_command(cmd + " " + searchTerm)
        stdin.close()
        outerr = stderr.readlines()
        print("ERRORS: ", outerr)
        output = stdout.readlines()

        # Get/Use the result
        print("output:", output)
        result = ''.join(output)  # Convert list of lines to a single string, making data easier to manipulate.
        client.close()
        # Split the result into paragraphs as above.
        paragraphs = result.split('\n\n')
        return paragraphs

    except Exception as e:
        print("Error performing the search", e)
        return "Error performing the search"

# Fuction to save search term and resulting content to the database.
def save_to_database(search_term, search_result):
    try:
        # Calling previous function to connect to database.
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            # Insert the searched name and the result into the database. %s placeholders for searchTerm and results.
            insert_query = "INSERT INTO SEARCHRESULTS (query, result) VALUES (%s, %s)"
            # Turning result into single string, with two newlines between each paragraph to maintain formatting.
            result_string = '\n\n'.join(search_result)
            cursor.execute(insert_query, (search_term, result_string))
            connection.commit()
            cursor.close()
            connection.close()
    except Error as e:
        print("Error saving to database", e)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)

    # Unused Error Page from Part 1
    # @app.route('/indexAction', methods=['POST'])
    # def indexAction():
    #     search = request.form.get("search")
    #     print(search)
    #     return render_template("/error.html")