from tinydb import TinyDB, Query
from datetime import datetime

db = TinyDB('database/user_data.json')
User = Query()


def get_user(user_id):
    return db.search(User.user_id == user_id)


def update_image_count(message, input_path):
    user = message.from_user
    user_id = user.id
    username = user.username  # Can be None
    first_name = user.first_name  # Can be None
    last_name = user.last_name  # Can be None
    today = datetime.now().date().isoformat()

    user_data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'image_count': 1,
        'date': today,
        'input_path': input_path}

    existing_user = get_user(user_id)
    if existing_user:
        existing_user = existing_user[0]
        if existing_user.get("date") == today:
            new_count = existing_user.get("image_count", 0) + 1
            user_data['image_count'] = new_count
        db.update(user_data, User.user_id == user_id)
    else:
        user_data['user_id'] = user_id
        db.insert(user_data)
    print(existing_user if existing_user else user_data)


def can_send_image(user_id, max_imgs):
    users = get_user(user_id)
    if not users:
        return True  # If no record exists, the user can send an image
    user = users[0]
    today = datetime.now().date().isoformat()
    # Check if the limit is reached and if the record is for today
    if user.get("date") == today and user.get("image_count", 0) >= max_imgs:
        return False
    return True


def reset_image_counts():
    # Logic to reset the image count for all users
    db.update({'image_count': 0}, User.all())


def count_unique_users():
    unique_users = set()
    all_users = db.all()
    for user_data in all_users:
        user_id = user_data.get('user_id')
        if user_id:
            unique_users.add(user_id)
    return len(unique_users)
