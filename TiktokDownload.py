import os, time, re, requests, json
from tkinter import N
import chromedriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class TiktokDownload:
    def __init__(self):
        os.system('cls')
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }

        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        self.save_folder = 'TikTok Multi'
        self.download_page_url = 'https://snaptik.app/vn'

        """
            URL INPUT
            # user page link
            https://www.tiktok.com/@tinaneeeee/video/7098291042625080602?is_copy_url=1&is_from_webapp=v1
            https://www.tiktok.com/@tinaneeeee

            # video link
            https://vt.tiktok.com/ZSdQkfHpf/?k=1
            https://vt.tiktok.com/ZSdQk9f8J/
        """

        self.url_input = ''; self.check_input = False; self.is_userpage=False; self.user_title='Empty title'

        self.auto_downoad()

    def auto_downoad(self):
        while True:
            self.url_input, self.check_input = self.get_url_input()
            if self.check_input:
                self.is_userpage, self.user_title, self.url_input = self.check_user_page(self.url_input)
                self.save_folder = 'Tiktok Multiple' if self.is_userpage else'Tiktok One'
                self.folder_save_path = f'{self.root_dir}\{self.save_folder}\{self.user_title}'
                self.json_file_path = f'{self.root_dir}\{self.save_folder}\{self.user_title}.json'

                try:
                    if not os.path.exists(self.folder_save_path):
                        os.makedirs(self.folder_save_path)
                except:
                    print('[ Feedback ]: Lỗi khi tạo thư mục!')
                    print('-' * 120)
                    return

                self.video_data = self.scroll_data(self.url_input) if self.is_userpage \
                    else [{"video_number": "1", "video_id": re.findall('video\/(\d+)', self.url_input)[0], "video_url": self.url_input}]

                self.video_data = self.update_data(self.video_data)
                
                self.download(self.video_data)
            else:
                break

    def check_user_page(self, url_input):
        if 'www.tiktok.com/@' in url_input:
            if '/video/' in url_input: 
                return False, re.findall('@(\w+)', url_input)[0], url_input
            else: 
                return True, re.findall('@(\w+)', url_input)[0], url_input
        else:
            response = requests.get(url=url_input, headers=self.headers)
            if '/video/' in response.url: 
                return False, re.findall('@(\w+)', response.url)[0], response.url
            else: 
                return True, re.findall('@(\w+)', response.url)[0], response.url
        
    def get_url_input(self):
        retry_max = 3
        for retry_number in range(retry_max):
            print('\n' + '-' * 120)
            url_input = re.sub("[^\x00-\xff]", '', input('Nhập link: ')).replace(' ', '')
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
            elif url_input == 'close':
                break
            else:
                print(f'[ Feedback ]: <!> Link nhập không thành công....\r')
                print('-' * 120)
                if (retry_number + 1) != retry_max:
                    print('[ Feedback ]: <!> Thử lại lần thứ {}!\r'.format(retry_number + 1))
                    print('-' * 120)
        return url_input, check_input

    def init_driver(self, opt='hide'):
        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')
        options.add_argument('--start-maximized')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        if opt == 'hide':
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')
        if opt == 'diswin':
            options.add_argument("--window-position=-10000,0")
        elif opt == 'headless':
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        
        options.add_experimental_option ("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_settings.popups": 0,
            "download.default_directory": f"{self.root_dir}",
            "directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False,
        })
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options) 
        return driver

    def scroll_data(self, url):
        print(f'[ Feedback ]: Đang lấy dữ liệu video...\r')
        print('-' * 120)
        start_time = time.time()
        self.driver = self.init_driver('headless')
        self.driver.get(url)

        scroll_pause_time = 1
        last_scroll_height = 0
        while True:
            new_scroll_height = self.driver.execute_script('return document.body.scrollHeight')
            if new_scroll_height != last_scroll_height:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(scroll_pause_time)
                last_scroll_height = new_scroll_height
            else:
                break
        
        src_elements = self.driver.find_elements_by_css_selector("div[data-e2e='user-post-item'] a")

        data = []
        video_number = 1
        for src_element in src_elements:
            video_url = src_element.get_attribute('href')
            data.append({
                'video_number': str(video_number),
                'video_id': (re.findall('/video/(\d+)?', video_url)[0]),
                'video_url': video_url,
            })
            with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=4, separators=(',', ': '))
            video_number = video_number + 1

        self.driver.quit()
        end_time = time.time()
        sub_time = end_time - start_time
        print('[ Feedback ]: Lấy dữ liệu thành công -*- {} Video -*- Thời gian: {:.2f} giây...'.format(video_number-1, sub_time))
        print('-' * 120)
        return data

    def update_data(self, video_data):
        print('[ Feedback ]: Đang cập nhật dữ liệu....')
        print('-' * 120)
        self.driver = self.init_driver('headless')
        self.driver.get(self.download_page_url)
        total_time = 0
        number_of_videos = len(video_data)
        for i in range(number_of_videos):
            start_time = time.time()
            for retry_num in range(3):
                self.driver.find_element_by_css_selector("#url").send_keys(video_data[i]['video_url'])
                self.driver.find_element_by_css_selector('#submiturl').click()
                try:    
                    download_1_css_selected = "div[class='abuttons mb-0'] a[title='Download Server 01']"
                    download_1 = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, download_1_css_selected))
                    )
                    download_2_css_selected = "div[class='abuttons mb-0'] a[title='Download Server 02']"
                    download_2 = self.driver.find_element_by_css_selector(download_2_css_selected)
                    download_3_css_selected = "div[class='abuttons mb-0'] a[title='Download Server 03']"
                    download_3 = self.driver.find_element_by_css_selector(download_3_css_selected)
                    video_data[i].update({
                        'download_url_1': str(download_1.get_attribute('href')),
                        'download_url_2': str(download_2.get_attribute('href')),
                        'download_url_3': str(download_3.get_attribute('href')),
                    })
                    break
                except: 
                    again_download_css_celected = "#navbar > nav > div > div.navbar-brand > a.navbar-item"
                    again_download = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, again_download_css_celected))
                    ).click()
                    continue
            
            with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
                json.dump(video_data, json_file, indent=4, separators=(',', ': '))

            again_download_css_celected = "#navbar > nav > div > div.navbar-brand > a.navbar-item"
            again_download = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, again_download_css_celected))
            ).click()

            end_time =  time.time()
            sub_time = end_time - start_time
            total_time = total_time + sub_time
            print("\r" + "[ Feedback ]: Cập nhật {:>2}/{} -+- Thời gian: {:.2f} giây...".format(i+1, number_of_videos, total_time), end='')
        
        print('')
        print('-' * 120)
        print('[ Feedback ]: Cập nhật dữ liệu thành công')
        print('-' * 120)
        self.driver.quit()
        return video_data

    def download(self, video_data):
        number_of_videos = len(video_data)
        for i in range(number_of_videos):
            video_name = str(video_data[i]['video_id']) + '.mp4'
            folder_path_listdir = os.listdir(self.folder_save_path)
            try:
                if video_name in folder_path_listdir:
                    print(f'[ Download ]: {i+1}/{number_of_videos} Tệp tên [ {video_name}.mp4 ] đã tồn tại, bỏ qua tải xuống!', end = "")
                    for i in range(10):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    print('-' * 120)
                    continue    
            except Exception as bug:
                # print(bug)
                pass

            for retry_num in range(3):
                try:
                    print(f'\n[   Video    ]: {i+1: >2} / {number_of_videos}')
                    print(f'[   Video    ]: Tải xuống video tên -- [ {video_name} ] --')
                    start_download_time = time.time()
                    for requests_num in range(3):
                        try:
                            video = requests.get(url=video_data[i]['download_url_1'], timeout=5, headers=self.headers)
                            break
                        except Exception as bug:
                            # print(bug)
                            continue
                    try:
                        content_size = int(video.headers['content-length'])
                    except Exception as bug:
                        video = requests.get(url=video_data[i]['download_url_2'], timeout=5, headers=self.headers)
                        try:
                            content_size = int(video.headers['content-length'])
                        except Exception as bug:
                            video = requests.get(url=video_data[i]['download_url_3'], timeout=5, headers=self.headers)
                            content_size = int(video.headers['content-length'])
                    size = 0
                    chunk_size = 1024
                    MB_size = content_size / chunk_size / 1024

                    if video.status_code == 200:
                        video_path = self.folder_save_path + '\\' + video_name
                        video_path = '{}\{}'.format(self.folder_save_path, video_name)
                        with open(file=video_path, mode='wb') as file:
                            for v_data in video.iter_content(chunk_size=chunk_size):
                                file.write(v_data)
                                size = size + len(v_data)
                                print('\r' + '[  Download  ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')        
                    end_download_time = time.time()
                    download_time = end_download_time - start_download_time
                    print(f'\n[  Download  ]: Thời gian: {download_time:.2f}s, Kích thước: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    # print(bug)
                    continue

def main():
    tiktok_download = TiktokDownload()

if __name__ == '__main__':
    main()