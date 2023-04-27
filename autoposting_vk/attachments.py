from datetime import datetime
import requests, time, json, vk_api, asyncio
from config import hidden_vars

session = vk_api.VkApi(token=hidden_vars.tg_bot.vk_api_token)


class Attachments:
    def __init__(self, data):
        self.att = list()
        self.image_list = list()
        for i in range(len(data['attachments'])):
            if 'photo' in data['attachments'][i]:
                self.att.append(data['attachments'][i]['photo']['sizes'][-1].get('url'))
                self.image_list.append(f'autoposting_vk/content_data/{data["id"]}_{i}.jpg')
            if 'doc' in data['attachments'][i]:
                self.att.append(data['attachments'][i]['doc']['preview']['photo']['sizes'][-1].get('src'))
                self.image_list.append(f'autoposting_vk/content_data/{data["id"]}_{i}.jpg')
            if 'market_album' in data['attachments'][i]:
                self.att.append(data['attachments'][i]['market_album']['photo']['sizes'][-1].get('url'))
                self.image_list.append(f'autoposting_vk/content_data/{data["id"]}_{i}.jpg')



def scrape_data(data):
    if data.get('copy_history'):
        data['from_id'] = data['copy_history'][0]['from_id']
        data['group_name'] = \
            session.method('groups.getById', {'group_id': -data['from_id']})[0]['name']
        data['repost_group'] = f"<a href='https://vk.com/public{data['from_id']}'>{data['group_name']}</a>"
        data['repost_text'] = f"<b> ↑ ↑ ↑ ↑ Р Е П О С Т ↓ ↓ ↓ ↓</b>\n  {data['repost_group']}\n"
        data['text'] = data['copy_history'][0].get('text')
        data['signer_id'] = data['copy_history'][0].get('signer_id')
        data.update(attachments=data['copy_history'][0]['attachments'])
        data.update(copy_history='data transferred')
        return data
    else:
        return data


def scrape_photos(data):
    box = Attachments(data)
    if data.get('attachments'):
        for i in range(len(box.att)):
            photo = requests.get(box.att[i])
            with open(f'autoposting_vk/content_data/{data["id"]}_{i}.jpg', 'wb') as fd:
                for chunk in photo.iter_content(50000):
                    fd.write(chunk)
                    time.sleep(2.3)
        return box.image_list
    return box.image_list


def send_media(data, images, caption, char_exceed, photo='photo'):
    request_url = "https://api.telegram.org/bot" + hidden_vars.tg_bot.bot_token + "/sendMediaGroup"
    files = {f'post_name{item}': open(f'{images[item]}', 'rb') for item in range(len(images))}
    caption = caption
    list_attach = [
        {"type": photo, "media": "attach://post_name0", "caption": caption, "parse_mode": 'HTML'}]
    if not char_exceed:
        list_attach[0].pop('caption')
    if len(images) >= 2:
        for item in range(len(images) - 1):
            list_attach.append({"type": photo, "media": f"attach://post_name{item + 1}"})
    media = json.dumps(list_attach)
    params = {"chat_id": hidden_vars.tg_bot.tg_chat,
              "media": media,
              "disable_notification": hidden_vars.tg_bot.notification}
    result = requests.post(request_url, params=params, files=files)
    if result.status_code == 200:
        time_now = datetime.fromtimestamp(time.mktime(datetime.now().timetuple())).strftime('%H:%M:%S')
        print(f"{data['id']}, {result.ok}, Photo`s:, {len(list_attach)}, send_with_media, {time_now}")


def send_text(data, text):
    link = str()
    try:
        video_owner_id = str(data['attachments'][0]['video']['owner_id'])
        video_id = str(data['attachments'][0]['video']['id'])
        if 'video' in data['attachments'][0]:
            link = f'\n<a href="https://vk.com/video{video_owner_id}_{video_id}">→→→→→ Видео ссылка ←←←←←</a>'
    except (IndexError, KeyError):
        link = None
    request_url = "https://api.telegram.org/bot" + hidden_vars.tg_bot.bot_token + "/sendMessage"
    params = {"chat_id": hidden_vars.tg_bot.tg_chat,
              "text": text,
              "parse_mode": 'HTML',
              "disable_web_page_preview": True,
              "disable_notification": hidden_vars.tg_bot.notification
              }
    if link:
        params.update({"text": text + link})
        params.update({"disable_web_page_preview": False})
    result = requests.post(request_url, params=params)
    if result.status_code == 200:
        time_now = datetime.fromtimestamp(time.mktime(datetime.now().timetuple())).strftime('%H:%M:%S')
        print(f"{data['id']}, {result.ok}, Photo`s: 0, send_only_text, {time_now}")
