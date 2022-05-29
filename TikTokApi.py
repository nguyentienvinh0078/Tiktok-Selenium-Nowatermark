import os, re, requests, json, time, sys


class TiktokDownload():
    def __init__(self):
        os.system('cls')
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            try:
                application_path = os.path.dirname(os.path.realpath(__file__))
            except NameError:
                application_path = os.getcwd()

        self.root_dir = application_path
        self.save_folder = 'TikTok Multi'

    def auto_downoad(self):
        while True:
            self.url_input, self.check_input = self.get_url_input()
            if self.check_input:
                self.is_userpage, self.user_title, self.url_input = self.check_user_page(self.url_input)
                self.save_folder = 'Tiktok Multiple' if self.is_userpage else'Tiktok One'
                self.folder_save_path = f'{self.root_dir}\{self.save_folder}'
                self.json_file_path = f'{self.root_dir}\{self.save_folder}\{self.user_title}.json'

                try:
                    if not os.path.exists(self.folder_save_path):
                        os.makedirs(self.folder_save_path)
                except:
                    print('[ Feedback ]: Lỗi khi tạo thư mục!')
                    print('-' * 120)
                    return
                
                if self.is_userpage:
                    print('[ Feedback ]: Tải xuống nhiều video!')
                    print('-' * 120)
                    self.video_data = self.get_data(self.url_input)
                else:
                    print('[ Feedback ]: Tải xuống 1 video!')
                    print('-' * 120)
                    response = requests.get(url=self.url_input, headers=self.headers)
                    video_url = response.url
                    video_id = re.findall('video\/(\d+)', video_url)[0]
                    # jx_url_base = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=' # douyin
                    tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{}%5D'.format(video_id)
                    self.video_data = [{
                        "video_number": "1",
                        "video_id": video_id,
                        "video_url": video_url,
                        "video_api": tiktok_api_link,
                    }]

                self.download(self.video_data)
                os.system('cls')
                print('[ Feedback ]: Tải xuống hoàn tất {} video'.format(len(self.video_data)))
            else: break

    def check_user_page(self, url_input):
        if 'www.tiktok.com/@' in url_input:
            if '/video/' in url_input: 
                return False, re.findall('\/@(.*)\/video', url_input)[0], url_input
            else: 
                return True, re.findall('tiktok.com\/@(.*)', url_input.split('?')[0])[0], url_input
        else:
            response = requests.get(url=url_input, headers=self.headers)
            if '/video/' in response.url: 
                return False, re.findall('\/@(.*)\/video', response.url)[0], response.url
            else: 
                return True, re.findall('tiktok.com\/@(.*)', response.url.split('?')[0])[0], response.url
        
    def get_url_input(self):
        retry_max = 3
        for retry_number in range(retry_max):
            print('-' * 120)
            print('[ Feedback ]: Nhập vào link để tải xuống, Nhập "close" để thoát!')
            print('-' * 120)
            url_input = re.sub("[^\x00-\xff]", '', input('[ Nhập link ]: ')).replace(' ', '')
            print('-' * 120)
            check_input = False
            if url_input == '':
                print(f'[ Feedback ]: <!> Link nhập trống! Hãy kiểm tra lại....\r')
                print('-' * 120)
                if (retry_number + 1) != retry_max:
                    print('[ Feedback ]: <!> Thử lại lần thứ {}!\r'.format(retry_number + 1))
                    print('-' * 120)
            elif 'tiktok.com' in url_input:
                check_input = True
                print('[ Feedback ]: Nhập link thành công!')
                print('-' * 120)
                break
            elif url_input == 'close' or url_input == 'Close' or url_input == 'x':
                break
            else:
                print(f'[ Feedback ]: <!> Link nhập không thành công....\r')
                print('-' * 120)
                if (retry_number + 1) != retry_max:
                    print('[ Feedback ]: <!> Thử lại lần thứ {}!\r'.format(retry_number + 1))
                    print('-' * 120)
        return url_input, check_input

    def request_deal(self, url, max_again=3):
        for req_again in range(max_again):
            try:
                return requests.get(url, headers=self.headers, timeout=10)
            except requests.exceptions.RequestException as bug:
                print(bug)
                continue

    def get_user_id(self, input_url, max_again=3):
        for get_again in range(max_again):
            try:
                user_name = re.findall('tiktok.com\/@(.*)', input_url.split('?')[0])[0]
                api_user_id = "https://t.tiktok.com/node/share/user/@{}?aid=1988".format(user_name)
                user_data = self.request_deal(api_user_id).json()
                try:
                    return str(user_data["userInfo"]["user"]["id"])
                except:
                    return str(user_data['seoProps']['pageId'])
            except Exception as bug:
                # print(bug)
                continue

    def get_data(self, input_url):
        user_id = self.get_user_id(input_url)
        min_cursor, max_cursor = '0', '0'
        video_data = []
        done = False
        while not done:
            data_url = 'https://www.tiktok.com/share/item/list?id={:s}&type=1&count=100&maxCursor={:s}&minCursor={:s}'.format(user_id, max_cursor, min_cursor)
            response = self.request_deal(data_url)
            if response.status_code == 200:
                js = response.json()

                item_list_data = js['body']['itemListData']
                max_cursor = js['body']['maxCursor']
                done = not js['body']['hasMore']
                
                for item in item_list_data:
                    video_id = str(item['itemInfos']['id'])
                    user_title = str(item['authorInfos']['uniqueId'])
                    video_urls = 'https://www.tiktok.com/@{}/video/{}'.format(user_title, video_id)
                    tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{}%5D'.format(video_id)
                    
                    video_data.append({
                        'video_id': video_id,
                        'video_url': video_urls,
                        'video_api': tiktok_api_link,
                    })

        with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
            json.dump(video_data, json_file, indent=4, separators=(',', ': '))

        return video_data

    def download(self, video_data):
        number_of_videos = len(video_data)
        for video_number in range(number_of_videos):
            js = json.loads(self.request_deal(video_data[video_number]['video_api']).text)
            try:
                # nickname = str(js['item_list'][0]['author']['nickname']) #douyin
                unique_id = str(js["aweme_details"][0]['author']["unique_id"])
            except Exception as bug:
                # print(bug)
                # nickname = 'Empty Nickname'
                pass
                print('[ Feedback ]: Không tìm được nickname, đặt thành: Empty Nickname!\r')
                print('-' * 120)

            try:
                folder_nickname_path = f'{self.folder_save_path}\{unique_id}'
                if not os.path.exists(folder_nickname_path): 
                    os.makedirs(folder_nickname_path)
            except Exception as bug:
                # print(bug)
                print(f'[ Feedback ]: Không tạo được thư mục {unique_id}!\r')
                print('-' * 120)
                return 
            
            try:
                video_url_no_watermark = str(js["aweme_details"][0]["video"]["play_addr"]["url_list"][0])
                # video_url_no_watermark = str(js['item_list'][0]['video']['play_addr']['url_list'][0]).replace('playwm', 'play') #douyin
            except Exception as bug:
                #print(bug)
                print('[ Feedback ]: Không lấy được link video không nhãn!\r')
                print('-' * 120)
            
            filename = '{}.mp4'.format(video_data[video_number]['video_id'])
            nickname_path_listdir = os.listdir(folder_nickname_path)

            try:
                if filename in nickname_path_listdir:
                    print(f'[ Download ]: {video_number+1:2>}/{number_of_videos} Tệp ID [ {filename} ] đã tồn tại, Bỏ qua tải xuống! ', end = "")
                    for i in range(15):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    print('-' * 120)
                    continue    
            except Exception as bug:
                #print(bug)
                pass
            
            retry_download_max = 3
            for retry_number in range(retry_download_max):
                try:
                    print(f'\n[   Video    ]: {video_number+1}/{number_of_videos}')
                    print(f'[   Video    ]: Đang tải tệp -- [ {filename} ] --')
                    start_download_time = time.time()
                    size = 0
                    chunk_size = 1024
                    video = self.request_deal(video_url_no_watermark)
                    content_size = int(video.headers['content-length'])
                    MB_size = content_size / chunk_size / 1024

                    if video.status_code == 200:
                        video_path = f'{folder_nickname_path}\{filename}'
                        with open(file=video_path, mode='wb') as file:
                            for data in video.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                size = size + len(data)
                                print('\r' + '[  Download  ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')
                    end_download_time = time.time()
                    download_time = end_download_time - start_download_time
                    print(f'\n[  Download  ]: Thời gian: {download_time:.2f}s, Kích thước: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    #print(bug)
                    continue

if __name__ == '__main__':
    try:
        tiktok_download = TiktokDownload()
        tiktok_download.auto_downoad()
    except Exception as bug:
        print(bug)
        os.system('pause')
