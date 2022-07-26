import requests
import json
import tqdm

with open('input_info.txt') as file:
    '''input_info.txt includes:
    First line - VK token
    Second line - YandexDisk token
    Third line - VK User_id whos photos to be downloaded'''
    access_token = file.readline().strip()
    yd_token = file.readline().strip()
    user_id = file.readline().strip()


class VK:
    '''Class to search for profile photos of VK users'''

    def __init__(self, token: str, user_id: str):
        self.token = token
        self.user_id = user_id
        self.params = {'v': '5.131', 'access_token': self.token}


    def vk_info(self) -> dict:
        '''Method to get information on the profile photos'''
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.user_id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1}
        response = requests.get(url, params={**params, **self.params})
        return response.json()


    def vk_info_to_json(self, quantity=5) -> dict:
        '''Method to get .json from vk_get_info'''
        profile_photo_info = {}
        types = {'s': 0, 'm': 1, 'x': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'y': 7, 'z': 8, 'w': 9}
        for params in self.vk_info()['response']['items']:
            if params['likes']['count'] not in profile_photo_info:
                photo_name = str(params['likes']['count']) + '.jpg'
                profile_photo_info.setdefault(photo_name, [])
            else:
                photo_name = str(params['date']) + '.jpg'
                profile_photo_info.setdefault(params['date'], [])
            for size in sorted(params['sizes'], key=lambda item: item['type']):
                if size['type'] == 'w':
                    profile_photo_info[photo_name] = [size['url'], 'w', types['w']]
                    break
                else:
                    profile_photo_info[photo_name] = [sorted(params['sizes'], key=lambda item: item['type'])[-1]['url'],
                                         sorted(params['sizes'], key=lambda item: item['type'])[-1]['type'],
                                         types[sorted(params['sizes'], key=lambda item: item['type'])[-1]['type']]]
        if quantity > len(profile_photo_info):
            print(f'There are only {len(profile_photo_info)} photos in profile of {user_id}')
            exit()
        result = sorted(profile_photo_info.items(), key=lambda param: param[-1][-1])
        result = dict(result[-quantity:])
        return result


class YD:
    '''Class to upload photos on YandexDisk'''

    def __init__(self, token: str):
        self.token = token
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }


    def yd_folder(self, folder_name: str) -> None:
        '''Method to create YandexDisc folder'''
        params = {
            'path': f'/{folder_name}/'
        }
        requests.put(self.url, headers=self.headers, params=params)


    def yd_upload_file(self, loading_files: dict, loading_folder: str) -> None:
        '''Method to uploag photos in the created YandexDisc folder'''
        user_url = self.url + 'upload'
        headers = self.headers
        photos = []
        for key, value in tqdm(loading_files.items(), ascii=True, desc='Uploading photos: '):

            params = {
                'url': value[0],
                'path': f'{loading_folder}/{key}',
                'disable_redirects': 'true'
            }
            response = requests.post(user_url, params=params, headers=headers)
            photos.append({'file_name': key,
                                'size': value[1]})
            status = response.status_code
            if status < 400:
                tqdm.write(f'\nPhoto {key} has been uploaded: {status}')
            else:
                tqdm.write(f'\nUpload failed: {status}')
        with open('data.json', 'a') as file:
            json.dump(photos, file, indent=0)

        tqdm.write('Upload complete')


if __name__ == '__main__':
    photos_quantity = int(input())
    f_name = 'vk_photos'
    my_profile = VK(access_token, user_id)
    my_profile.vk_info()
    my_profile.vk_info_to_json(photos_quantity)
    my_disc = YD(yd_token)
    my_disc.yd_folder(f_name)
    my_disc.yd_upload_file(my_profile.vk_info_to_json(photos_quantity), f_name)