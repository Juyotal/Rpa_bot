from RPA.Robocorp.WorkItems import WorkItems as WI
import os


def capitalize_words_in_list(input_list):
    capitalized_list = [
        element.title() if " " in element else
        element.upper() if element.lower() == "u.s." else
        element.capitalize()
        for element in input_list
    ]

    return capitalized_list


class WorkItem:
    ''' 
        Just a little Class created to make getting Input and
        Output from WorkItems a little more practical for our tasks
    '''
    def __init__(self, logger):
        self.item = WI()
        self.item.get_input_work_item()
        self.logger = logger


    def get_input_params(self, phrase, category, num_months):
        '''
            Get the Input Params for our scrapping from the Worker Items
            If no Worker Item param is set for the particular, the default param
            is used for the process.
        '''

        try:
            phrase = self.item.get_work_item_variable("search_phrase")
        except KeyError:
            self.logger.info('No work item for Search phrase Set')
            
        try:
            category = self.item.get_work_item_variable("category")
            category = capitalize_words_in_list(category)
        except KeyError:
            self.logger.info('No work item for Category Set')
        
        try: 
            num_months = int(self.item.get_work_item_variable("number_of_months"))
        except KeyError:
            self.logger.info('No work item for number_of_months Set')

        return (phrase, category, num_months)
    
    
    def get_output(self, dirs, name):
        '''
            Given the dir of the Output folder as input
            We obtain the files to be uploaded to the cloud
        '''
        try:
            for file_path in dirs:
                file = file_path.split('/')[-1]
                self.item.add_work_item_file(file_path)
                json_rep = {'search_phrase': name, 'file': file}
                self.item.create_output_work_item(json_rep, files=file_path, save=True)
        
            self.logger.info('OutPut Sucessfully Saved !!!')

        except Exception as e:
            self.logger.error('Failed saving Output due to: %s', e)
