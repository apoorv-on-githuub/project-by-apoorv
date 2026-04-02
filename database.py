import os
from tabulate import tabulate
from supabase import create_client, Client
class Matching_QR:
    def __init__(self):
        url: str = "https://ajklxuhylyutzzxdvdjj.supabase.co"
        key: str ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqa2x4dWh5bHl1dHp6eGR2ZGpqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MTc0NDgsImV4cCI6MjA5MDI5MzQ0OH0.3HsK3yjnyKYG2LRAN15ZmYVfRwJ_KlYdYwl_J6_AlnU"
        self.supabase: Client = create_client(url, key)
        

    
    def find_info(self, barcode):
        for table in ["students", "teachers","books"]:
            response = self.supabase.table(table) \
                .select("*") \
                .eq("barcode", barcode) \
                .execute()

            if response.data:
                return response.data

        return None
       
    def get_info_student(self,barcode):
        raw_data = self.find_info(barcode=barcode)

        return (tabulate(raw_data, headers="keys", tablefmt="grid"))
   



                