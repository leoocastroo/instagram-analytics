import json
from datetime import datetime

import requests

from instalytics.utils.constants import InstagramConstants


class InstagramExtract():

    def __init__(self, username, login_user, login_pass, cookies=None):
        self.username = username

        self.login_user = login_user

        self.login_pass = login_pass

        self.cookies = cookies

        self.session = requests.session()

    def login(self):
        self.session.headers.update({'Referer': InstagramConstants.BASE_URL, 'user-agent': InstagramConstants.USER_AGENT})
        response = self.session.get(InstagramConstants.BASE_URL)

        self.session.headers.update({'X-CSRFToken': response.cookies['csrftoken']})

        if self.cookies:
            self.session.headers.update({'cookies': self.cookies})
        else:
            payload = {
                'username': self.login_user,
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{self.login_pass}',
                'queryParams': {},
                'optIntoOneTap': 'false'
            }

            response = self.session.post(InstagramConstants.LOGIN_URL, data = payload)
            data = json.loads(response.text)

            if data.get("authenticated"):
                self.cookies = response.cookies
            else:
                raise Exception(f'Error! login failed {response.text}')

    def get_user(self):
        response = self.session.get(InstagramConstants.USER_URL.replace('__USER__', self.username))

        if response.status_code == 200:
            self.user = response.json()['graphql']['user']

    def get_followers(self):
        end_cursor = ''
        has_next_page = True
        self.followers = []

        while has_next_page:
            igq = InstagramConstants.QUERY_URL
            payload = {
                "query_hash": InstagramConstants.QUERY_FOLLOWERS,
                "id": self.user['id'],
                "include_reel": True,
                "fetch_mutual": False,
                "first": 12,
                "after": end_cursor
            }

            response = self.session.get(igq, params=payload)
            if response.status_code == 200:
                result = response.json()

                has_next_page = result['data']['user']['edge_followed_by']['page_info']['has_next_page']
                if has_next_page:
                    end_cursor = result['data']['user']['edge_followed_by']['page_info']['end_cursor']
                else:
                    has_next_page = False
                self.followers.extend(result['data']['user']['edge_followed_by']['edges'])
            else:
                has_next_page = False

    def get_followed(self):
        end_cursor = ''
        has_next_page = True
        self.followed = []

        while has_next_page:
            igq = InstagramConstants.QUERY_URL
            payload = {
                "query_hash": InstagramConstants.QUERY_FOLLOWED,
                "id": self.user['id'],
                "include_reel": True,
                "fetch_mutual": False,
                "first": 12,
                "after": end_cursor
            }

            response = self.session.get(igq, params=payload)
            if response.status_code == 200:
                result = response.json()

                has_next_page = result['data']['user']['edge_follow']['page_info']['has_next_page']
                if has_next_page:
                    end_cursor = result['data']['user']['edge_follow']['page_info']['end_cursor']
                else:
                    has_next_page = False
                self.followed.extend(result['data']['user']['edge_follow']['edges'])
            else:
                has_next_page = False

    def get_medias(self):
        end_cursor = ''
        has_next_page = True
        self.medias = []
        while has_next_page:
            igq = InstagramConstants.QUERY_URL
            payload = {
                "query_hash": InstagramConstants.QUERY_MEDIAS,
                "id": self.user['id'],
                "first": 12,
                "after": end_cursor
            }

            response = self.session.get(igq, params=payload)
            if response.status_code == 200:
                result = response.json()

                has_next_page = result['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
                if has_next_page:
                    end_cursor = result['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                else:
                    has_next_page = False
                self.medias.extend(result['data']['user']['edge_owner_to_timeline_media']['edges'])
            else:
                has_next_page = False

    def get_media(self, shortcode, get_comments=False):
        igq = InstagramConstants.QUERY_URL
        payload = {
            "query_hash":"cf28bf5eb45d62d4dc8e77cdb99d750d",
            "shortcode": shortcode,
            "child_comment_count":3,
            "fetch_comment_count":40,
            "parent_comment_count":24,
            "has_threaded_comments": True
        }

        response = self.session.get(igq, params=payload)

        if response.status_code == 200:
            media = response.json()
            if get_comments:
                media['data']["shortcode_media"]["edge_media_to_parent_comment"]["edges"] = self.get_media_comments(media)
            return media["data"]
        return {}

    def get_media_comments(self, media):
        end_cursor = media['data']["shortcode_media"]["edge_media_to_parent_comment"]["page_info"]["end_cursor"]
        has_next_page = media['data']["shortcode_media"]["edge_media_to_parent_comment"]["page_info"]["has_next_page"]
        comments = media['data']["shortcode_media"]["edge_media_to_parent_comment"]["edges"]
        short_code = media['data']["shortcode_media"]["shortcode"]

        while has_next_page:
            igq = InstagramConstants.QUERY_URL
            payload = {
                "query_hash": InstagramConstants.QUERY_COMMENTS,
                "shortcode": short_code,
                "first": 12,
                "after": end_cursor
            }

            response = self.session.get(igq, params=payload)

            if response.status_code == 200:
                result = response.json()
                has_next_page = result['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['has_next_page']
                if has_next_page:
                    end_cursor = result['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['end_cursor']
                else:
                    has_next_page = False
                comments.extend(result['data']['shortcode_media']['edge_media_to_parent_comment']['edges'])
            else:
                has_next_page = False

        return comments


if __name__ == '__main__':
    ie = InstagramExtract('raffalobianco', 'leocastroo', 'Lpc)(200600LPC')
    ie.login()
    ie.get_user()
    # ie.get_medias(stop_date=datetime(2021,1,1))
    # ie.get_followers()
    # ie.get_media(ie.medias[1]['node']['shortcode'], get_comments=True)
