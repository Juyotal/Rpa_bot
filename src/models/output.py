import os
import shutil
import zipfile
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files

current_directory = os.getcwd()

out_folder='output'
imgs_folder='imgs'
excel_file='news_data.xlsx'
output_zip = 'images.zip'

class Output:

    def __init__(self, logger, search_phrase):
        '''
        Initialising Our OutPut Class. 
        This takes Care of saving files and images to the respective directories.
        If directory already exists for the search, it is first deleted on init.
        '''
        self.logger = logger
        self.output_dir = os.path.join(current_directory, out_folder)
        self.imgs_dir = os.path.join(self.output_dir, imgs_folder)
        self.excel_file = os.path.join(self.output_dir, excel_file)
        self.zip_output = os.path.join(self.output_dir , output_zip)

        try:
            os.makedirs(self.imgs_dir)
            self.logger.info('Directory %s successfully deleted to be rebuilt.', self.output_dir)
        except Exception as e:
            self.logger.info('Error while deleting directory: %s', e)
            return



    def download_image(self, img_url):
        ''' Download image from URL and save it to the download folder
            I did it usign requests library because I was unable 
            to use RPA.HTTP library (triggered SO level error)
        '''
        filename = img_url.split('/')[-1].split('?')[0]
        http = HTTP()

        try:
            save_path = os.path.join(self.imgs_dir, filename)
            http.download(url=img_url, target_file=save_path)
        except Exception as exception:
            self.logger.error("Error downloading image: %s", exception)
            filename = ""
        return filename
    

    def zip_images(self):
        ''' 
        Create a Zip of our Images Folder and Delete the OG folder
        '''
        with zipfile.ZipFile(self.zip_output, 'w') as zipf:
            for root, _, files in os.walk(self.imgs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, self.imgs_dir))

        shutil.rmtree(self.imgs_dir)
        self.logger.info("Images succesfully Zipped")
      

    def store_news(self, news):
        '''Create excel file with header and store the results'''

        self.logger.info("Storing news to EXCEL file...")
        excel_file = Files()
        workbook = excel_file.create_workbook()
        try:
            headers = ["date", "title", "description", "money_found", "image_filename", "search_count", ]
            for col, header in enumerate(headers, start=1):
                workbook.set_cell_value(1, col, header)

            for row, record in enumerate(news, start=2):
                if record['img_path'] != '': # download image if path exists
                   record['img_path'] = self.download_image(record['img_path'])

                for col, (_, value) in enumerate(record.items(), start=1):
                    workbook.set_cell_value(row, col, value)
            self.zip_images()
        except Exception as exception:
            self.logger.error("Error while storing data to EXCEL file: %s", exception)

        workbook.save(self.excel_file)
        self.logger.info("Finished storing news to EXCEL file. Exiting...")
