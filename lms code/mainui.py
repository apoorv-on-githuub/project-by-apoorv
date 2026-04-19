import tkinter as tk
from tkinter import messagebox

from scanning import Scan
from library import Library
from database import Matching_QR


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        self.student_database = Matching_QR()
        self.library = Library()

        self.header_frame = tk.Frame(self.root, padx=15, pady=10)
        self.header_frame.pack(fill="x")

        self.content_frame = tk.Frame(self.root, padx=15, pady=10)
        self.content_frame.pack(fill="both", expand=True)

        self.reset_session()
        self.show_start_screen()

    # ---------------- STATE ----------------
    def reset_session(self):
        self.user_data = None
        self.role = None
        self.user_barcode = None

    # ---------------- UI HELPERS ----------------
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def clear_content(self):
        self.clear_frame(self.content_frame)

    def show_top_bar(self, title):
        self.clear_frame(self.header_frame)

        row = tk.Frame(self.header_frame)
        row.pack(fill="x")

        tk.Button(row, text="Home", width=10, command=self.go_home).pack(side="left", padx=5)
        tk.Button(row, text="Back", width=10, command=self.show_main_screen).pack(side="left", padx=5)

        tk.Label(row, text=title, font=("Arial", 22, "bold")).pack(side="left", padx=15)

        tk.Label(
            self.header_frame,
            text=f"Role: {self.role.title() if self.role else 'Unknown'}",
            font=("Arial", 12)
        ).pack(anchor="w")

    # ---------------- START SCREEN ----------------
    def show_start_screen(self):
        self.clear_frame(self.header_frame)
        self.clear_content()

        tk.Label(self.header_frame, text="Library System", font=("Arial", 22, "bold")).pack(anchor="w")

        tk.Label(
            self.content_frame,
            text="Click Scan to start",
            font=("Arial", 18, "bold")
        ).pack(pady=40)

        tk.Button(
            self.content_frame,
            text="Scan",
            width=20,
            height=2,
            command=self.scan_and_load_user
        ).pack()

    # ---------------- NAVIGATION ----------------
    def go_home(self):
        self.reset_session()
        self.show_start_screen()

    # ---------------- SCANNING ----------------
    def scan_and_load_user(self):
        self.reset_session()
        self.clear_content()

        tk.Label(self.content_frame, text="Scanning...", font=("Arial", 18)).pack(pady=20)
        self.root.update_idletasks()

        try:
            scanner = Scan()
            scanner.start_scanning()
            data = scanner.result

            if not data:
                messagebox.showerror("Error", "No QR data found")
                self.show_start_screen()
                return

            self.user_data = data[0]
            self.role = str(self.user_data.get("role", "")).lower()
            self.user_barcode = self.user_data.get("barcode")

            self.show_main_screen()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.show_start_screen()

    # ---------------- FORMATTER ----------------
    def format_book_data(self, data):
        if not data:
            return "No data found."

        output = ""

        for book in data:
            output += (
                f"Book ID       : {book.get('book_id')}\n"
                f"Barcode       : {book.get('barcode')}\n"
                f"Name          : {book.get('name')}\n"
                f"Status        : {book.get('status')}\n"
                f"Author        : {book.get('authors', {}).get('name')}\n"
                f"Course        : {book.get('courses', {}).get('course_name')}\n"
                f"Department    : {book.get('departments', {}).get('dept_name')}\n"
                f"{'-'*40}\n"
            )

        return output

    # ---------------- OUTPUT ----------------
    def show_output(self, title, content):
        self.clear_content()

        tk.Label(self.content_frame, text=title, font=("Arial", 18, "bold")).pack(pady=10)

        # format book data automatically
        if isinstance(content, list) and content and isinstance(content[0], dict):
            content = self.format_book_data(content)

        text = tk.Text(self.content_frame, font=("Consolas", 11))
        text.pack(fill="both", expand=True)

        text.insert("1.0", str(content))
        text.config(state="disabled")

        btn_row = tk.Frame(self.content_frame)
        btn_row.pack(pady=10)

        tk.Button(btn_row, text="Back", width=15, command=self.show_main_screen).pack(side="left", padx=5)
        tk.Button(btn_row, text="Home", width=15, command=self.go_home).pack(side="left", padx=5)

    # ---------------- MAIN SCREEN ----------------
    def show_main_screen(self):
        self.clear_content()
        self.show_top_bar("Library System")

        if self.role == "student":
            self.show_student_screen()
        elif self.role == "teacher":
            self.show_teacher_screen()
        elif self.role == "book":
            self.show_book_screen()
        else:
            tk.Label(self.content_frame, text="Invalid barcode", font=("Arial", 16)).pack(pady=20)

    # ---------------- STUDENT ----------------
    def show_student_screen(self):
        tk.Label(
            self.content_frame,
            text=f"Welcome {self.user_data.get('name')}",
            font=("Arial", 16)
        ).pack(pady=20)

        tk.Button(self.content_frame, text="Student Info", width=25,
                  command=lambda: self.show_output(
                      "Student Info",
                      self.student_database.get_info_student(self.user_barcode)
                  )).pack(pady=5)

        tk.Button(self.content_frame, text="All Books", width=25,
                  command=lambda: self.show_output(
                      "All Books",
                      self.library.show_all_books()
                  )).pack(pady=5)

        tk.Button(self.content_frame, text="Search Books", width=25,
                  command=self.search_books_screen).pack(pady=5)

        tk.Button(self.content_frame, text="Issue Book", width=25,
                  command=self.issue_book).pack(pady=5)

    # ---------------- TEACHER ----------------
    def show_teacher_screen(self):
        tk.Button(self.content_frame, text="Catalog", width=25,
                  command=lambda: self.show_output(
                      "Catalog",
                      self.library.get_catalog()
                  )).pack(pady=5)

        tk.Button(self.content_frame, text="Non Returners", width=25,
                  command=lambda: self.show_output(
                      "Non Returners",
                      self.library.get_non_returners()
                  )).pack(pady=5)

    # ---------------- BOOK ----------------
    def show_book_screen(self):
        tk.Label(self.content_frame, text="Book Panel", font=("Arial", 16)).pack(pady=20)

        tk.Button(self.content_frame, text="Book Info", width=25,
                  command=lambda: self.show_output(
                      "Book Info",
                      self.library.show_book(self.user_barcode)
                  )).pack(pady=5)

        tk.Button(self.content_frame, text="Return Book", width=25,
                  command=self.return_book).pack(pady=5)

    # ---------------- SEARCH ----------------
    def search_books_screen(self):
        self.clear_content()

        tk.Label(self.content_frame, text="Search Book", font=("Arial", 18)).pack(pady=10)

        entry = tk.Entry(self.content_frame, width=40)
        entry.pack(pady=10)

        def search():
            query = entry.get()
            result = self.library.search_books(query)
            self.show_output("Search Result", result)

        tk.Button(self.content_frame, text="Search", command=search).pack(pady=5)

    # ---------------- ACTIONS ----------------
    def issue_book(self):
        try:
            scanner = Scan()
            scanner.start_scanning()
            data = scanner.result

            book_barcode = data[0].get("barcode")

            result = self.library.issue_book(
                book_barcode=book_barcode,
                student_barcode=self.user_barcode
            )

            self.show_output("Issue Result", result)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_book(self):
        try:
            result = self.library.return_book(self.user_barcode)
            self.show_output("Return Result", result)
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()