from celery import shared_task
import csv
from .models import Product
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@shared_task(bind=True)
def process_csv_upload(self, file_path):
    """ Background task to process CSV upload """
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
        total = len(reader)
        for index, row in enumerate(reader, start=1):
            print("Processing product:", row['name'])
            Product.objects.create(
                name=row['name'],
                price=row['price'],
                description=row['description'],
                status=row['status']
            )
            self.update_state(state='PROGRESS', meta={'progress': (index / total) * 100})
    
    return {'progress': 100}
