from sqlalchemy.orm import Session
from backend.database import engine
from backend.models import Product

def update_images():
    with Session(engine) as session:
        products = session.query(Product).all()
        for p in products:
            if '?' not in p.image_url:
                p.image_url = p.image_url + "?v=2"
            else:
                base, v = p.image_url.split('?v=')
                p.image_url = f"{base}?v={int(v)+1}"
        session.commit()
        print("Updated image URLs in DB")

if __name__ == "__main__":
    update_images()
