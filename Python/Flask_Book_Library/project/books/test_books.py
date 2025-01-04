import unittest
from project import app, db
from project.books.models import Book

class TestBookModel(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_book_creation(self):
        book = Book(name="Valid Book", author="Valid Author", year_published=2020, book_type="Fiction")
        db.session.add(book)
        db.session.commit()
        self.assertIsNotNone(book.id)
        self.assertEqual(book.name, "Valid Book")
        self.assertEqual(book.author, "Valid Author")
        self.assertEqual(book.year_published, 2020)
        self.assertEqual(book.book_type, "Fiction")
        self.assertEqual(book.status, "available")

    def test_invalid_book_creation(self):
        book = Book(name="", author="", year_published="invalid_year", book_type="")
        with self.assertRaises(ValueError):
            db.session.add(book)
            db.session.commit()

    def test_sql_injection(self):
        book = Book(name="Robert'); DROP TABLE books;--", author="Hacker", year_published=2020, book_type="Non-Fiction")
        db.session.add(book)
        db.session.commit()
        self.assertIsNotNone(book.id)
        self.assertNotIn("DROP TABLE", book.name)

    def test_javascript_injection(self):
        book = Book(name="<script>alert('Hacked');</script>", author="Hacker", year_published=2020, book_type="Non-Fiction")
        db.session.add(book)
        db.session.commit()
        self.assertIsNotNone(book.id)
        self.assertNotIn("<script>", book.name)

    def test_extreme_year_published(self):
        book = Book(name="Ancient Book", author="Old Author", year_published=-1000, book_type="History")
        db.session.add(book)
        db.session.commit()
        self.assertIsNotNone(book.id)
        self.assertEqual(book.year_published, -1000)

        book = Book(name="Future Book", author="Future Author", year_published=3000, book_type="Sci-Fi")
        db.session.add(book)
        db.session.commit()
        self.assertIsNotNone(book.id)
        self.assertEqual(book.year_published, 3000)

    def test_name_too_long(self):
        long_name = "A" * 65  # Assuming the max length is 64
        book = Book(name=long_name, author="Author", year_published=2020, book_type="Fiction")
        with self.assertRaises(ValueError):
            db.session.add(book)
            db.session.commit()

    def test_duplicate_book_name(self):
        book1 = Book(name="Unique Book", author="Author1", year_published=2020, book_type="Fiction")
        book2 = Book(name="Unique Book", author="Author2", year_published=2021, book_type="Non-Fiction")
        db.session.add(book1)
        db.session.commit()
        with self.assertRaises(Exception):
            db.session.add(book2)
            db.session.commit()

    def test_non_integer_year_published(self):
        book = Book(name="Book with Invalid Year", author="Author", year_published="Two Thousand Twenty", book_type="Fiction")
        with self.assertRaises(ValueError):
            db.session.add(book)
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
