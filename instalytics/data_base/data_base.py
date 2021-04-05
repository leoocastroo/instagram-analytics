from cassandra.cluster import Cluster

from instalytics.scrape.instagram_extract import InstagramExtract


class CassandraConnector():

    def __init__(self):
        self.cluster = Cluster()

        self.session = self.cluster.connect()

        self.create_keyspace()

        self.create_user_table()

        self.session.set_keyspace('instalytics')

    def create_keyspace(self):
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS instalytics WITH replication = {'class': 'SimpleStrategy', 'replication_factor' :1};
        """)

    def create_user_table(self):
        self.session.execute("""
        CREATE TABLE IF NOT EXISTS instalytics.users (
            id int,
            username text,
            full_name text,
            biography text,
            category_name text,
            followers_count int,
            followed_count int,
            medias_count int,
            profile_pic_url text,
            external_url text,
            is_verified boolean,
            is_business_account boolean,
            is_private boolean,
            is_real boolean,
            primary key(id)
        );
        """)

    def insert_user(self, user):
        followers_count = user.get('edge_follow').get('count', 0) if user.get('edge_follow') else 0
        followed_count = user.get('edge_followed_by').get('count', 0) if user.get('edge_followed_by') else 0
        medias_count = user.get('edge_owner_to_timeline_media').get('count', 0) if user.get('edge_owner_to_timeline_media') else 0

        self.session.execute("""
            INSERT INTO users (id, username, full_name, biography, category_name, followers_count, followed_count, medias_count, profile_pic_url, external_url, is_verified, is_business_account, is_private, is_real) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        """, (int(user.get('id')), user.get('username'), user.get('full_name'), user.get('biography'), user.get('category_name'), followers_count, followed_count, medias_count, user.get('profile_pic_url'), user.get('external_url'), user.get('is_verified'), user.get('is_business_account'), user.get('is_private'), user.get('is_real', True)))

    def get_user(self, user_id):
        return self.session.execute("SELECT * FROM users WHERE id = %s", (user_id, ))