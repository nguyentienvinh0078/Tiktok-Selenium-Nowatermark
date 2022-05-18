from dataclasses import dataclass
import os, time, re, requests, json
from urllib import response
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
        self.save_type = 'TikTok Multi'

        self.download_page_url = 'https://snaptik.app/vn'

        # self.url = 'https://vt.tiktok.com/ZSdQkfHpf/?k=1'
        # self.url = 'https://www.tiktok.com/@tinaneeeee'

        i = 1
        retry_input_num = 3
        self.url = ''
        print('-' * 120)
        while self.url != 'quit':
            if (self.url == ''):
                while (i <= retry_input_num):
                    self.url = re.sub("[^\x00-\xff]", '', input('\nLink: ')).replace(' ', '')
                    self.check_input = False   
                    print('-' * 120)
                    if (self.url == ''):
                        print(f'[ Feedback ]: <!> Fail Getlink!\r')
                        print('-' * 120)
                        if i != retry_input_num:
                            print(f'\n[ Feedback ]: <!> Retry time {i+1}!\r')
                            print('-' * 120)

                    elif 'tiktok.com' in self.url:
                        self.check_input = True   
                        # print(f'[ Thông báo ]: Douyin link: --[ {self.url} ]-- nhập thành công!')
                        print(f'[ Feedback ]: Getlink Success!')
                        break
                    elif (self.url == 'quit'):
                        break
                    else:
                        print(f'[ Feedback ]: <!> Fail Getlink......\r')
                        print('-' * 120)
                        if i != retry_input_num:
                            print(f'\n[ Feedback ]: <!> Retry time {i+1}!\r')
                            print('-' * 120)
                    i = i + 1
            else:
                self.check_input = True

            if self.check_input:   
                response = requests.get(url=self.url, headers=self.headers)
                self.user_title = re.findall('@(\w+)', response.url)[0]
                self.data = []
                if '/video/' in response.url:
                    print('-' * 120)
                    print(f'[ Feedback ]: Getting Data...\r')
                    print('-' * 120)
                    self.save_type = 'Tiktok One'
                    self.folder_save_path = self.root_dir + '\\' + self.save_type
                    try:
                        self.user_title_folder = self.folder_save_path + '\\' + self.user_title
                        if not os.path.exists(self.user_title_folder):
                            os.makedirs(self.user_title_folder)
                    except:
                        print('[ Feedback ]: Create save folder Error!')
                        print('-' * 120)
                        return
                    self.json_file_path = self.folder_save_path + '\\' + self.user_title + '.json'
                    self.video_id = re.findall('video\/(\d+)', response.url)[0]
                    self.data.append({
                        'video_number': str(1),
                        'video_id': self.video_id,
                        'video_url': self.url,
                    })
                    with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
                        json.dump(self.data, json_file, indent=4, separators=(',', ': '))
                    
                    self.data = self.update_data()
                    self.download(self.json_file_path)
                else:
                    self.save_type = 'TikTok Multi'
                    self.folder_save_path = self.root_dir + '\\' + self.save_type
                    try:
                        self.user_title_folder = self.folder_save_path + '\\' + self.user_title
                        if not os.path.exists(self.user_title_folder):
                            os.makedirs(self.user_title_folder)
                    except:
                        print('[ Feedback ]: Create save folder Error!')
                        print('-' * 120)
                        return

                    self.json_file_path = self.folder_save_path + '\\' + self.user_title + '.json'
                    self.data = self.scroll_and_get_data(self.url)
                    self.data = self.update_data()
                    self.download(self.json_file_path)
                self.url = ''

    def init_driver(self, folder_save_path, opt='hide'):
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
            "download.default_directory": f"{folder_save_path}",
            "directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False,
        })
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options) 
        return driver

    def scroll_and_get_data(self, url):
        print('-' * 120)
        print(f'[ Feedback ]: Getting Data...\r')
        print('-' * 120)
        start_time = time.time()
        self.driver = self.init_driver(self.folder_save_path, 'headless')
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
        i = 1
        for src_element in src_elements:
            video_url = src_element.get_attribute('href')
            data.append({
                'video_number': str(i),
                'video_id': (re.findall('/video/(\d+)?', video_url)[0]),
                'video_url': video_url,
            })
            with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=4, separators=(',', ': '))
            i = i + 1

        self.driver.quit()
        end_time = time.time()
        sub_time = end_time - start_time
        print('[ Feedback ]: Get Data Success -*- {} Video -*- Time: {:.2f}s'.format(i-1, sub_time))
        print('-' * 120)
        return data

    def update_data(self):
        with open(self.json_file_path, mode='r') as json_file:
            data = json.load(json_file)
        number_of_videos = len(data)

        self.driver = self.init_driver(self.user_title_folder, 'headless')
        self.driver.get(self.download_page_url)
        total_time = 0
        for i in range(number_of_videos):
            start_time = time.time()
            retry_num = 0
            retry_max = 3
            while retry_num < retry_max: 
                self.driver.find_element_by_css_selector("#url").send_keys(data[i]['video_url'])
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
                    data[i].update({
                        'download_url_1': str(download_1.get_attribute('href')),
                        'download_url_2': str(download_2.get_attribute('href')),
                        'download_url_3': str(download_3.get_attribute('href')),
                    })
                    break
                except: 
                    again_download_css_celected = "#navbar > nav > div > div.navbar-brand > a.navbar-item"
                    again_download = self.driver.find_element_by_css_selector(again_download_css_celected).click()
                    print(f'[ Feedback ]: Update Data Error!')
                    print('-' * 120)
                    if retry_num != retry_max:
                        print(f"[  Feedback ]: Update Overtime {retry_num}, Retry time {retry_num}!\r")
                    else:
                        print(f"[  Feedback  ]: Update Overtime {retry_num}, Cancel\r")
                        print('-' * 120)
                    retry_num += 1
            
            with open(self.json_file_path, mode='w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=4, separators=(',', ': '))

            again_download_css_celected = "#navbar > nav > div > div.navbar-brand > a.navbar-item"
            again_download = self.driver.find_element_by_css_selector(again_download_css_celected).click()

            end_time =  time.time()
            sub_time = end_time - start_time
            total_time = total_time + sub_time
            print("\r" + "[ Feedback ]: Update {:>2}/{} -+- Time: {:.2f}s".format(i+1, number_of_videos, total_time), end='')
        
        print('')
        print('-' * 120)
        print('[ Feedback ]: Update Scucess')
        print('-' * 120)
        self.driver.quit()

        return data

    def download(self, json_file_path):
        with open(json_file_path, mode='r') as json_file:
            data = json.load(json_file)
        number_of_videos = len(data)
        for i in range(number_of_videos):
            video_name = str(data[i]['video_id']) + '.mp4'
            folder_path_listdir = os.listdir(self.user_title_folder)
            # kiểm tra xem video đã tồn tại hay chưa, nếu đã có thì bỏ qua tải xuống
            try:
                if video_name in folder_path_listdir:
                    print(f'[ Download ]: {i+1}/{number_of_videos} File ID [ {video_name} ] Was Exists, Skip Download!', end = "")
                    for i in range(10):
                        print(">", end='', flush=True)
                        time.sleep(0.01)
                    print('\r')
                    print('-' * 120)
                    continue    
            except Exception as bug:
                # print(bug)
                pass

            retry_num = 1
            retry_download_max = 3
            # tối đa ba lần thử
            while retry_num <= retry_download_max:
                try:
                    print(f'\n[    Video   ]: {i+1: >2} / {number_of_videos}')
                    start_download_time = time.time()
                    requests_num = 0
                    while requests_num < retry_download_max:
                        try:
                            video = requests.get(url=data[i]['download_url_1'], timeout=5, headers=self.headers)
                            break
                        except requests.exceptions.RequestException:
                            if requests_num != retry_download_max:
                                print(f"[  Feedback ]: Request Overtime {requests_num}, Retry time {requests_num}!\r")
                            else:
                                print(f"[  Feedback ]: Request Overtime {requests_num}, Cancel\r")
                                print('-' * 120)
                            requests_num += 1
                    size = 0
                    chunk_size = 1024
                    try:
                        content_size = int(video.headers['content-length'])
                    except Exception as bug:
                        video = requests.get(url=data[i]['download_url_2'], timeout=5, headers=self.headers)
                        try:
                            content_size = int(video.headers['content-length'])
                        except Exception as bug:
                            video = requests.get(url=data[i]['download_url_3'], timeout=5, headers=self.headers)
                            content_size = int(video.headers['content-length'])

                    MB_size = content_size / chunk_size / 1024

                    print(f'[ Video ]: Downloading.... -- [ {video_name} ] --')
                    if video.status_code == 200:
                        video_name = self.user_title_folder + '\\' + video_name
                        with open(file=video_name, mode='wb') as file:
                            for v_data in video.iter_content(chunk_size=chunk_size):
                                file.write(v_data)
                                size = size + len(v_data)
                                print('\r' + '[ Download ]: %s%.2f%%' % ('>'*int(size*50/content_size), float(size/content_size*100)), end=' ')        
                    end_download_time = time.time()
                    download_time = end_download_time - start_download_time
                    print(f'\n[ Download ]: Time: {download_time:.2f}s, Size: {MB_size:.2f}MB')
                    print('-' * 120)
                    break
                except Exception as bug:
                    print(bug)
                    print(f'[ Feedback ]: Error Download!')
                    print('-' * 120)
                    if retry_num != retry_download_max:
                        print(f"[  Feedback ]: Download Overtime {retry_num}, Retry time {retry_num}!\r")
                    else:
                        print(f"[  Feedback ]: Download Overtime {retry_num}, Cancel\r")
                        print('-' * 120)
                    retry_num += 1

def main():
    tiktok_download = TiktokDownload()

if __name__ == '__main__':
    main()