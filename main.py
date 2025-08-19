from flask import Flask, render_template, abort, url_for,  request, jsonify, current_app, send_from_directory
import json
import os
from faker import Faker
import markovify
import random
import copy


app = Flask(__name__)

def load_json(file_path):
    import os
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


with open("corpus.txt", encoding="utf-8") as f:
    text = f.read()
text_model = markovify.Text(text)

def load_json(file_path):
    import os
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



@app.route('/user/<int:user_id>')
def user_profile(user_id):
    users = load_json('data.json')
    names = load_json('BlankUser.json')

    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        abort(404)

    print(f"User found: {user['displayName']} (ID: {user_id})")
    print(user)

    photo_path = user.get('profilePhoto')
    static_folder = current_app.static_folder

    if not photo_path or not os.path.isfile(os.path.join(static_folder, photo_path)):
        photo_path = 'images/default_avatar.png'

    user['profilePhoto'] = get_static_url(photo_path)

    friends_ids = user.get('friends', [])
    friends_list = []
    for fid in friends_ids:
        friend = next((u for u in users if u['id'] == fid), None)
    if friend:
            friend_copy = copy.deepcopy(friend)
            friend_photo_path = friend_copy.get('profilePhoto')
            if not friend_photo_path or not os.path.isfile(os.path.join('static', friend_photo_path)):
                friend_photo_path = 'images/default_avatar.png'
            friend_copy['profilePhoto'] = get_static_url(friend_photo_path)
            friends_list.append(friend_copy)

    needed = 6 - len(friends_list)
    if needed > 0:
        existing_names = set(f['displayName'] for f in friends_list)
        existing_names.add(user['displayName'])

        available_names = [name for name in names if name not in existing_names]

        chosen_names = random.sample(available_names, min(needed, len(available_names)))

        for name in chosen_names:
            friends_list.append({
                "id": None,
                "displayName": name,
                "profilePhoto": url_for('static', filename='images/default_avatar.png')
             })

    # Новый блок — получение постов


    if 'posts' in user and user['posts']:
         posts = user['posts']
    else:
         posts = generate_user_posts(user_id, posts_count=10)
         #user['posts'] = posts  # опционально — чтобы в объекте пользователя появились сгенерированные посты

    return render_template('index.html', user=user, friends_list=friends_list, posts=posts)


def get_user_posts(user_data, posts_count=10, images_folder='static/images/post_images'):
    # Проверяем есть ли уже посты
    if "posts" in user_data and user_data["posts"]:
        return user_data["posts"]
    else:
        # Если нет, генерируем
        user_key = user_data.get("id") or user_data.get("username") or "default_key"
        generated_posts = generate_user_posts(user_key, posts_count, images_folder)
        user_data["posts"] = generated_posts
        return generated_posts


def generate_user_posts(user_key, posts_count=10, images_folder='static/images/post_images'):
    posts = []
    state = random.getstate()

    image_folder_path = os.path.join(os.getcwd(), images_folder)
    image_files = [f for f in os.listdir(image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    image_files.sort()

    total_images = len(image_files)

    for i in range(posts_count):
        random.seed(hash(f"{user_key}_{i}"))  

        content_sentences = []
        for _ in range(3):
            sentence = text_model.make_sentence(max_overlap_ratio=0.7)
            if sentence:
                content_sentences.append(sentence)
        content = " ".join(content_sentences)

        if total_images > 0:
            # Выбираем случайный файл, при этом seed фиксирован
            image_name = random.choice(image_files)
        else:
            image_name = None

        posts.append({
            "content": content or "Содержимое отсутствует",
            # "date": "2025-07-10",
            "image": image_name,
        })

    random.setstate(state)
    return posts



@app.route('/search_users')
def search_users():
    query = request.args.get('q', '').strip().lower()
    users = load_json('data.json')
    results = []
    static_folder = current_app.static_folder

    if query:
        for u in users:
            if (query in u.get('firstName', '').lower() or
                query in u.get('lastName', '').lower() or
                query in u.get('displayName', '').lower()):

                photo_path = u.get("profilePhoto", "images/default_avatar.png")
                full_path = os.path.join(static_folder, photo_path)

                if not photo_path or not os.path.isfile(full_path):
                    photo_path = "images/default_avatar.png"

                photo_url = get_static_url(photo_path)

                results.append({
                    "id": u["id"],
                    "displayName": f"{u.get('firstName', '')} {u.get('lastName', '')}".strip(),
                    "profilePhoto": photo_url
                })
    max_results = 10
    return jsonify(results[:max_results])
    
    



def get_static_url(path):
    if path.startswith('/static/'):
        return path
    return url_for('static', filename=path)


@app.route('/blocked')
def block_profile():
    return render_template('blocked.html')

@app.route('/error')
def error_page():
    return render_template('error.html')

@app.route('/server_work')
def server_work():
    return render_template('server_work.html')

@app.route('/')
def main():
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug=True)
