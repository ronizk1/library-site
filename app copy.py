from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Book, Customer, and Loan models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    book_type = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)

class Loan(db.Model):
    cust_id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

# Create tables in the database
with app.app_context():
    db.create_all()

# Routes for the RESTful API
@app.route('/')
def hello_world():
    return 'Hello, World!'


# # Add a new book
# @app.route('/add_book', methods=['POST'])
# def add_book():
#     data = request.get_json()

#     name = data.get('name')
#     author = data.get('author')
#     year_published = data.get('year_published')
#     book_type = data.get('book_type')

#     new_book = Book(name=name, author=author, year_published=year_published, book_type=book_type)
#     db.session.add(new_book)
#     db.session.commit()

#     return jsonify({'message': 'Book added successfully'})


@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        data = request.get_json()

        name = data.get('name')
        author = data.get('author')
        year_published = data.get('year_published')
        book_type = data.get('book_type')

        new_book = Book(name=name, author=author, year_published=year_published, book_type=book_type)
        db.session.add(new_book)
        db.session.commit()

        # Include a custom message in the response
        response_data = {'message': 'Book added successfully', 'toastify_type': 'success'}
        return jsonify(response_data)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error adding book: {e}")
        # Return an error message to the front end
        return jsonify({'message': 'Error adding book', 'toastify_type': 'error'})

# Add a new customer
@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.get_json()

    name = data.get('name')
    city = data.get('city')
    age = data.get('age')

    new_customer = Customer(name=name, city=city, age=age)
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({'message': 'Customer added successfully'})


# Loan a book
@app.route('/loan_book', methods=['POST'])
def loan_book():
    data = request.get_json()

    customer_name = data.get('customer_name')
    book_name = data.get('book_name')

    # Search for customer and book by name in the database
    customer = Customer.query.filter_by(name=customer_name).first()
    book = Book.query.filter_by(name=book_name).first()

    if customer and book:
        # Check if the book is already on loan
        existing_loan = Loan.query.filter_by(cust_id=customer.id, book_id=book.id, return_date=None).first()
        if existing_loan:
            return jsonify({'error': 'This book is already on loan'})

        # Perform necessary operations (e.g., update database)
        new_loan = Loan(cust_id=customer.id, book_id=book.id)
        db.session.add(new_loan)
        db.session.commit()

        return jsonify({'message': 'Book loaned successfully'})
    else:
        return jsonify({'error': 'Customer or book not found'})




# Return a book
@app.route('/return_book', methods=['POST'])
def return_book():
    data = request.get_json()

    customer_name_return = data.get('customer_name_return')
    book_name_return = data.get('book_name_return')

    # Search for customer and book by name in the database
    customer_return = Customer.query.filter_by(name=customer_name_return).first()
    book_return = Book.query.filter_by(name=book_name_return).first()

    if customer_return and book_return:
        # Check if the book is currently on loan to the specified customer
        existing_loan = Loan.query.filter_by(cust_id=customer_return.id, book_id=book_return.id, return_date=None).first()

        if existing_loan:
            # Perform necessary operations (e.g., update database)
            existing_loan.return_date = datetime.utcnow()
            db.session.commit()

            return jsonify({'message': 'Book returned successfully'})
        else:
            return jsonify({'error': 'This book is not currently on loan to the specified customer'})
    else:
        return jsonify({'error': 'Customer or book not found'})

# ... (Remaining code)

# Return a book using customer and book names

# # Return a book
# @app.route('/return_book', methods=['POST'])
# def return_book():
#     data = request.get_json()

#     customer_name_return = data.get('customer_name_return')
#     book_name_return = data.get('book_name_return')

#     # Search for customer and book by name in the database
#     customer_return = Customer.query.filter_by(name=customer_name_return).first()
#     book_return = Book.query.filter_by(name=book_name_return).first()

#     if customer_return and book_return:
#         # Check if the book is currently on loan to the specified customer
#         existing_loan = Loan.query.filter_by(cust_id=customer_return.id, book_id=book_return.id, return_date=None).first()

#         if existing_loan:
#             # Perform necessary operations (e.g., update database)
#             existing_loan.return_date = datetime.now(timezone.utc)
#             db.session.commit()

#             return jsonify({'message': 'Book returned successfully'})
#         else:
#             return jsonify({'error': 'This book is not currently on loan to the specified customer'})
#     else:
#         return jsonify({'error': 'Customer or book not found'})




# Get all books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    book_list = [{'id': book.id, 'name': book.name, 'author': book.author,
                  'year_published': book.year_published, 'book_type': book.book_type}
                 for book in books]
    return jsonify({'books': book_list})

# Get all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    customer_list = [{'id': customer.id, 'name': customer.name, 'city': customer.city,
                      'age': customer.age} for customer in customers]
    return jsonify({'customers': customer_list})

# Get all loans
# @app.route('/loans', methods=['GET'])
# def get_loans():
#     loans = Loan.query.all()
#     loan_list = [{'customer_name': Customer.query.get(loan.cust_id).name,
#                   'book_name': Book.query.get(loan.book_id).name,
#                   'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
#                   'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else None}
#                  for loan in loans]
#     return jsonify({'loans': loan_list})

@app.route('/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    loan_list = [{'customer_name': Customer.query.get(loan.cust_id).name,
                  'book_name': Book.query.get(loan.book_id).name,
                  'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                  'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else None}
                 for loan in loans]
    return jsonify({'loans': loan_list})



# Run the application
if __name__ == '__main__':
    app.run(debug=True)

