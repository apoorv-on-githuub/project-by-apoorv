from supabase import create_client, Client
import pandas as pd
from datetime import date
from tabulate import tabulate
class Library:
    def __init__(self):
        url: str = "https://ajklxuhylyutzzxdvdjj.supabase.co"
        key: str ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqa2x4dWh5bHl1dHp6eGR2ZGpqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MTc0NDgsImV4cCI6MjA5MDI5MzQ0OH0.3HsK3yjnyKYG2LRAN15ZmYVfRwJ_KlYdYwl_J6_AlnU"
        self.supabase: Client = create_client(url, key)

    def show_book(self,book_barcode):
        if self.check_book(book_barcode) is True:
            response = self.supabase.table("books") \
                .select("barcode,book_id, name, status, authors(name), courses(course_name), departments(dept_name)") \
                .eq("barcode", book_barcode) \
                .execute()
            return response.data

        else:
            print("book Not available")
        
    def check_book(self, barcode):
            response = self.supabase.table("books") \
                .select("barcode, name, status, authors(name), courses(course_name), departments(dept_name)") \
                .eq("barcode", barcode) \
                .execute()
            if len(response.data) >= 1:
                 return True
            else:
                 return False
    def decode_dict(self, data):
        return {
            "book_name": data[0]["name"],
            "author": data[0]["authors"]["name"],
            "department": data[0]["departments"]["dept_name"],
            "course": data[0]["courses"]["course_name"],
            "status": data[0]["status"],
            "book_id": data[0]["book_id"]
        }
    def print_book_info(self,book_barcode):
          if self.check_book(book_barcode) is True:
            info = self.decode_dict(self.show_book(book_barcode))
            
           
            print( f"Book Name: {info['book_name']}\
                       \nAuthor: {info['author']}\
                       \nDepartment: {info['department']}\
                       \nCourse: {info['course']}\
                       \nStatus: {info['status']}")
         
    def issue_book(self,book_barcode,student_barcode):
        
           
            info = self.decode_dict(self.show_book(book_barcode))
            book_id = info["book_id"]
            if info["status"] == "available":
                 
                    (self.supabase
                        .table("books")
                        .update({"status": "issued"})
                        .eq("book_id", book_id)
                    .execute())
                    (self.supabase.table("book_issues").insert({
                        "book_id":book_id ,
                        "student_barcode": student_barcode,
                        "status": "issued"

                    }).execute())
                    return "Book Issued Successfully"
            else:
                result = (
                        self.supabase
                            .table("book_issues")
                            .select("students(name, roll_no)")
                            .eq("book_id", book_id)
                            .execute() 
                    )
                

                issued_person , roll_no = result.data[0]["students"]["name"],result.data[0]["students"]["roll_no"]
                return(f"\nbook not availale and already issued by: \nName :{issued_person}, Roll No. {roll_no} ")
        
    def return_book(self ,book_barcode):
        
            info = self.decode_dict(self.show_book(book_barcode))
            book_id = info["book_id"]
           

            if info["status"] != "available":
                 
                    (self.supabase
                        .table("books")
                        .update({"status": "available"})
                        .eq("book_id", book_id)
                    .execute())

                    (self.supabase.table("book_issues") \
                    .update({
                        "status": "returned",
                        "actual_return_date": date.today().isoformat()
                    }) \
                    .eq("book_id", book_id) \
                    .execute())
                    return "Book returned successfuly"
            else:
                 return "Book already in library"
    def show_all_books(self):
        response = self.supabase.table("books") \
            .select("barcode, book_id, name, status, authors(name), courses(course_name), departments(dept_name)") \
            .execute()

        data = response.data

        # flatten manually
        clean_data = []
        for row in data:
            clean_data.append({
                "barcode": row["barcode"],
                "book_id": row["book_id"],
                "name": row["name"],
                "status": row["status"],
                "author": row["authors"]["name"],
                "course": row["courses"]["course_name"],
                "department": row["departments"]["dept_name"]
            })

        # print like relational table
        return (tabulate(clean_data, headers="keys", tablefmt="grid"))

        
  



    def search_books(self, parameter):
        q = parameter.strip()
        response = self.supabase.table("books") \
                .select("barcode, name, book_id,status, authors(name), courses(course_name), departments(dept_name)") \
                .ilike("name", f"%{parameter}%") \
                .execute()
        if response.data:
            data = response.data
            clean_data = []
            for row in data:
                clean_data.append({
                    "barcode": row["barcode"],
                    "book_id": row["book_id"],
                    "name": row["name"],
                    "status": row["status"],
                    "author": row["authors"]["name"],
                    "course": row["courses"]["course_name"],
                    "department": row["departments"]["dept_name"]
                })

        # print like relational table
            return (tabulate(clean_data, headers="keys", tablefmt="grid"))
                
        else:
                return "No books found"
    
    def get_catalog(self):
        response = (
        self.supabase
        .table("book_issues")
        .select("""
            issue_date,
            status,
            fine,
            students!inner(name, roll_no, email),
            books!inner(
                name,
                courses!inner(course_name)
            )
        """)
        .execute()
    )

        data = response.data


        table = []

        for row in data:
            table.append([
                row["students"]["name"],
                row["students"]["roll_no"],
                row["students"]["email"],
                row["books"]["name"],
                row["books"]["courses"]["course_name"],
                row["issue_date"],
                row["status"],
                row["fine"]
            ])

        headers = ["Name", "Roll", "Email", "Book", "Course", "Date", "Status", "Fine"]

        return(tabulate(table, headers=headers, tablefmt="grid"))

    def get_non_returners(self):
        response = self.supabase.rpc("get_issued_books_count").execute()
        data = response.data
        table = [
            [
                row["student_name"],
                row["roll_no"],
                row["email"],
                row["status"],
                row["number_of_book_issued"]
            ]
            for row in data
        ]

        headers = ["Name", "Roll No", "Email", "Status", "Books Issued"]

        return (tabulate(table, headers=headers, tablefmt="grid"))