import asyncio, requests, os, shutil, time

from tqdm import tqdm

from autoposting_vk.db_work import _def_signer_id_func, _get_username, read_people_base, check_post, write_post_data
from autoposting_vk.attachments import scrape_photos, send_text, send_media, scrape_data

from config import hidden_vars


class Posting:
    def __init__(self, data):
        self._char_exceed = None
        self._video_key = None
        self._images = None
        self.data = data
        self.time = self.data['date']
        self.id = self.data['id']
        self.paid = '<i>          Платная реклама</i>' if self.data.get('marked_as_ads') else ' '
        self.txt = self.data.get('text')
        self._att_key = 1 if self.data.get('attachments') else 0
        self.repost = self.data.get('repost_text') if self.data.get('repost_text') else ' '
        if self._att_key == 1:
            self._video_key = 1 if self.data['attachments'][0].get('type') == 'video' else 0
        self.signer_id = _def_signer_id_func(self.data)
        if self.signer_id == 'Anonymously':
            self.message = self.txt + f'\n          Анонимно'
        elif self._video_key == 1:
            self.message = self.txt
        else:
            self.signer_fullname = read_people_base('FULL_NAME', 'USER_ID', int(self.signer_id)) \
                if read_people_base('FULL_NAME', 'USER_ID', int(self.signer_id)) else _get_username(self.signer_id)
            self.signer_url = 'vk.com/id' + str(self.signer_id)
            self.message = f"{self.repost}\n{self.txt}" \
                           f"\n<a href='{self.signer_url}'>          {self.signer_fullname}</a>\n{self.paid}"

    def send_to_tg(self):
        self._char_exceed = True if len(self.message) < 1024 else False
        self._images = scrape_photos(self.data)
        if self._att_key == 0 or self._video_key == 1:
            send_text(self.data, self.message)
        else:
            if self._char_exceed:
                send_media(self.data, self._images, self.message, self._char_exceed)
            else:
                send_media(self.data, self._images, self.message, self._char_exceed)
                send_text(self.data, self.message)
        write_post_data(self.id, self.txt, self.signer_id, self.time)


def connect(count):
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': hidden_vars.tg_bot.vk_token,
                         'v': 5.131,
                         'owner_id': hidden_vars.tg_bot.owner_id,
                         'count': count,
                         'offset': 0
                     })

    return r.json()['response']['items']


async def start_autopost():
    try:
        while True:
            unpublished = list()
            n_new_posts = list()
            data_volume = connect(hidden_vars.tg_bot.amount_post_list)
            for i in range(len(data_volume)):
                find = check_post(data_volume[i]['id'])
                if find is None:
                    unpublished.append(data_volume[i])
                    n_new_posts.append(data_volume[i]['id'])
            n = 0
            # post list turn around
            unpublished.reverse() and n_new_posts.reverse()
            # clearing a large list
            data_volume.clear()
            while n != len(unpublished):
                data_volume.append(scrape_data(unpublished[n]))
                n += 1
            print(f'New posts amount: {len(data_volume)}\n'
                  f'Posts to be published: {n_new_posts}' if len(data_volume) > 0 else 'No new posts')
            for n in data_volume:
                post = Posting(n)
                post.send_to_tg()

            if len(os.listdir('autoposting_vk/content_data')) > 0:
                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'content_data')
                shutil.rmtree(path)
                os.mkdir('autoposting_vk/content_data')
            else:
                pass
            await asyncio.sleep(hidden_vars.tg_bot.request_period)
    except KeyboardInterrupt:
        print('AUTOPOST stopped')
