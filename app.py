from flask import Flask, render_template, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
# Import sys library to aid in debugging
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://my_user:my_pass4@localhost:5432/fswebdev_examples'
db = SQLAlchemy(app)

# Create class to get todo records from DB
class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)

  def __repr__(self):
      return f'<Todo: {self.id}, {self.description}>'

# Create tables for above declared db.Model(s) if tables do not yet exist in DB
db.create_all()
# MANUAL STEPS TO CREATE DB TABLE & SAMPLE RECORDS:
# Login to psql:
# > psql fswebdev_examples electro
# Verify table is created:
# > \dt
# Verified table exists, now verify columns were created correctly:
# > \d todos
# Verified columns created correctly, now insert sample data:
# > INSERT INTO todos (description) VALUES ('Do a thing 1');
# Reset DB if ever any issues or errors:
# > dropdb todoapp && createdb todoapp

# Define a listener route and method for the create new todo item form button on index.html
@app.route('/todos/create', methods=['POST'])
# Create a todo handler to handle requests coming into this route
def create_todo():
    # Create variable to track error condition state and set default to 'False'
    error = False
    # Create variable to contain response body element as library
    body = {}
    # Define default method to create a session, then submit data and close session if no errors encountered
    try:
        # Create a variable and assign value of submitted form data passed to AJAX request using 'get_json' method (make sure to import 'request' from flask first).
        # Fetches json body of request from form identified with key field 'description'
        description = request.get_json()['description']
        # Create a new 'todo' object so we can add it to DB transactions
        # NOTE: We can test for errors by temporarily changing the 'description' attribute below to something random
        todo = Todo(description=description)
        # Add submitted form data as pending change to DB
        db.session.add(todo)
        # Commit submitted form data as persistent change to DB
        db.session.commit()
        # Redefine the 'body' variable to value of submitted form data passed to AJAX request
        body['description'] = todo.description
    # If session error encountered, rollback and print exceptions
    except:
        # Redefine error variable value as 'True'
        error = True
        # Rollback any pending DB transactions
        db.session.rollback()
        # Print exception details to console
        print(sys.exc_info())
    # Close the session
    finally:
        db.session.close()

    # If error 'True'
    if error:
        # Use the Flask 'abort' method to raise an HTTPException for the given status code
        abort (400)
    # If error 'False'
    else:
        # Return the json object of the defined 'body' variable using jsonify method (import 'jsonify from flask first)
        return jsonify(body)

# Define a listener route for default app path
@app.route('/')
# Define content to be returned to view whenever route is invoked
def index():
    # Define the page to be displayed, run a default query and set a variable to contain query results to be passed to page
    return render_template('index.html', data=Todo.query.all()
    )

if __name__ == '__main__':
  app.run(debug=True)
