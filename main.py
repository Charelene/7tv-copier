import requests, sqlite3, json, time


def main():
    print("No error handling, so don't screw this up!")
    print("Insert 7TV emote set ID you would like to copy:")
    copy_set_id = str(input())

    print("Now, insert your own emote set ID:")
    target_set_id = str(input())

    print("Open web inspector and get any sample request on 7tv, like opening your own sets."
          "Those appear as gql requests in Network inspector."
          "Get seventv-auth/Bearer token from request headers, but omit 'Bearer' or 'seventv-auth:")
    token = str(input())

    copy_set(copy_set_id)

    db_file = 'emoteset.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM emote_set")
    emote_entries = cursor.fetchall()

    for emote_entry in emote_entries:
        emote_id, name = emote_entry
        add_emote(target_set_id, token, emote_id, name)
        time.sleep(0.5)

    conn.close()

def add_emote(target_set_id, token, emote_id, name):
    url = "https://7tv.io/v3/gql"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Cookie": "seventv-auth=" + token,
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Origin": "https://7tv.app",
        "Referer": "https://7tv.app/",
        "Sec-CH-UA": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }
    body = {
        "operationName": "ChangeEmoteInSet",
        "variables": {
            "action": "ADD",
            "id": target_set_id,
            "name": name,
            "emote_id": emote_id
        },
        "query": "mutation ChangeEmoteInSet($id: ObjectID!, $action: ListItemAction!, $emote_id: ObjectID!) { emoteSet(id: $id) { id emotes(id: $emote_id, action: $action) { id name __typename } __typename }}"
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    print(response.text)


def copy_set(copy_set_id):
    url = "https://7tv.io/v3/emote-sets/" + copy_set_id
    db_file = 'emoteset.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emote_set';")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("DELETE FROM emote_set;")
        print("Clearing out the database to accomodate set specified")
    else:
        cursor.execute('''
            CREATE TABLE emote_set (
                id TEXT UNIQUE,
                name TEXT
            )
        ''')
        print("No database, creating one")

    emote_data = get_emote_data(url)
    cursor.executemany("INSERT INTO emote_set (id, name) VALUES (?, ?);", emote_data)

    conn.commit()
    conn.close()


def get_emote_data(url):
    response = requests.get(url)
    data = response.json()
    emotes = data.get("emotes", [])
    return [(emote["id"], emote["name"]) for emote in emotes]


if __name__ == "__main__":
    main()
