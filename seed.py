from app import app, db, User, Note, bcrypt
from faker import Faker

fake = Faker()

with app.app_context():
    print("Clearing old data...")
    Note.query.delete()
    User.query.delete()

    print("Creating sample users...")
    pwd = bcrypt.generate_password_hash("password123").decode('utf-8')
    
    # Capitalization matched here
    kamau = User(username="kamau", password_hash=pwd)
    wanjiru = User(username="wanjiru", password_hash=pwd)
    
    db.session.add_all([kamau, wanjiru])
    db.session.commit()

    
    local_normalies = [
        "M-Pesa Monthly Budget",
        "Nairobi Expressway Toll Notes",
        "Naivasha Trip Itinerary",
        "Matatu Route Schedule",
        "SGR Ticket Reservation Details",
        "Weekly Grocery Shopping List",
        "Tech Meetup in Kilimani",
        "Electricity Token Refill Reminder",
        "Water Bill Payments",
        "Weekend Chama Savings Plan"
    ]

    print("Creating sample notes...")
    for user in [kamau, wanjiru]:
        for title in local_normalies:
            note = Note(
                title=title,
                content=fake.paragraph(nb_sentences=2),
                user_id=user.id
            )
            db.session.add(note)

    db.session.commit()
    print("Database seeded successfully!")