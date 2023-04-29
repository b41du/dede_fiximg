from config import db_config, temp_table, reset_temp_table, temp_table_arc_field, images_destination_path, images_base_url, images_default_url
from helpers import get_random_string
from orator import DatabaseManager
from fake_useragent import UserAgent
from log import log
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import os
import shutil

log = log

class Main:
    DB = None
    
    def __init__(self):
        self.db_config = db_config
        self.DB = DatabaseManager(self.db_config)
        self.reset_temp_table()
        self.ua = UserAgent(browsers=['edge', 'chrome'])

    def reset_temp_table(self):
        if reset_temp_table:
            self.DB.table(temp_table).truncate()
            log.info('{} is resetted'.format(temp_table))

    def get_broken_images(self):
        articles_list = []
        if reset_temp_table:
            articles_list = self.DB.table('dede_archives') \
                .join('dede_addonarticle', 'dede_archives.id', 'dede_addonarticle.id')  
        else:
            id_filter = self.DB.table('temp_table').lists(temp_table_arc_field) 
            articles_list = self.DB.table('dede_archives') \
                .where_not_in('dede_archives.id', id_filter) \
                .join('dede_addonarticle', 'dede_archives.id', 'dede_addonarticle.id')

        return articles_list
    
    def donwnload_images(self, image_url):
        try:
            now = datetime.now()
            folder = now.strftime('%Y-%m-%d')
            file_name = os.path.basename(image_url)
            response = requests.get(url=image_url, headers=self.ua.random, stream=True)

            if response.status_code != 200:
                log.error('Failed download images from {}'.format(image_url))
                return False

            file_path = '{}{}/{}'.format(images_destination_path, folder, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)

            return '{}{}/{}'.format(images_base_url, folder, file_name)

        except Exception as e:
            log.error(str(e))
            return False
    
    def handle_article_images(self, article=''):
        article_soup = BeautifulSoup(article, 'html.parser')
        thumbnail = ''

        for image in article_soup.find_all('img'):
            image_url = image['src']
            local_img_url = self.donwnload_images(image_url)
            if local_img_url and not thumbnail:
                thumbnail = local_img_url
            elif not local_img_url:
                local_img_url = images_default_url
            image['src'] = images_default_url

        if not thumbnail:
            thumbnail = images_default_url

        return (thumbnail, str(article_soup))

    def execute(self):
        article_list = self.get_broken_images()
        for articles in article_list.select(
            'dede_archives.id',
            'dede_archives.litpic',
            'dede_addonarticle.body'
        ).chunk(100):
            for article in articles:
                article_id = article['id']

                thumbnail, article_str = self.handle_article_images(article['body'])

                try:
                    self.DB.table('dede_archives').where('id', article_id).update({'litpic': thumbnail})
                    self.DB.table('dede_addonarticle').where('id', article_id).update({'body': article_str})
                    
                    log.info('Data updated id {}'.format(article_id))

                except Exception as e:
                    log.error(str(e))
                    exit()


if __name__ == '__main__':
    main = Main()
    main.execute()