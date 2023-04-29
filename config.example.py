app_name = 'img_fix'

db_config = {
    'default': 'mysql',
    'mysql': {
        'driver': 'mysql',
        'host': 'localhost',
        'database': 'database',
        'user': 'root',
        'password': '',
        'prefix': ''
    }
}

temp_table = 'fix_image_temp'
temp_table_arc_field = 'article_id'
reset_temp_table = False

images_destination_path = '/www/wwwroot/wztest19.top/images/uploads/'
images_base_url = '/images/uploads/'
images_default_url = '/images/defaultpic.gif'