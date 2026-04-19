from scanning import Scan
from library import Library
from database import Matching_QR
student_database = Matching_QR()
scanner = Scan()
scanner.start_scanning()
library = Library()
my_data  = scanner.result 
if my_data[0]['role'] == "student":
    print(f"Wecome\n{student_database.get_info_student(my_data[0]['barcode'])}")
    stop = False
    while not stop:
        response_student = (input("1.show all books,\n2.search books,\n3.issue book\npress q to to back : "))
        if response_student == "1":
            print(library.show_all_books())
        elif response_student == "2":
            searched_text = input("search the book using book name: ")
            book_found = library.search_books(searched_text)
            print(book_found)
            
        elif response_student == "3":
            book_scanner = Scan()
            book_scanner.start_scanning()
            book_data = book_scanner.result
            issue_book = library.issue_book(book_barcode=book_data[0]["barcode"],student_barcode=my_data[0]["barcode"])
            print(issue_book)
        elif response_student.lower() == "q":
            stop = True
        else:
            print("pls select from given option (1,2,3) ")



elif my_data[0]['role'] == "Teacher":
    stop = False
    print(f"Welcome\n{ my_data[0]['name']}\n")
    while not stop:
        response_teacher = input("1.show all catalog,\n2.show students who have not returned books,\npress q to to back : ")
        if response_teacher == "q":
            stop = True
        if response_teacher == "1":
            print(library.get_catalog())
        elif response_teacher == "2":
            print(library.get_non_returners())
        
        else:
            print("pls select from given option only ")

elif my_data[0]['role'] == "book":
    book_barcode = my_data[0]["barcode"]
    book_info = library.decode_dict(library.show_book(book_barcode) )# type: ignore
    library.print_book_info(book_barcode=book_barcode)
    response = input("press r to return and pay fine(if any) \n press any key to back: ")


    if response == "r":


        library.return_book(book_barcode=book_barcode)
else:
    print("ivalid barcode")