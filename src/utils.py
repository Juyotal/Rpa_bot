import logging
from dateutil.parser import parse
from datetime import datetime, timedelta

'''
code to be executed to scroll to SHOW_MORE button.
Tried everything but could not interact with button
upon deployment on cloud. This was my Last ressort
'''
js_code = """
    function scrollAndReturnTargetElement() {
        var targetElement = document.querySelector('[data-testid="search-show-more-button"]');
        if (targetElement) {
            targetElement.scrollIntoView();
            return targetElement;
        }
        return null;
    }
    return scrollAndReturnTargetElement();
"""


def configure_logger():
    '''Our Logger'''
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def get_post_date(dt_str):
    '''
    Get the date the  article was posted from date_time 
    string on article element
    '''
    if('h ago' in dt_str):
        h = dt_str.split('h')[0]
        date = (datetime.now() - timedelta(hours = int(h))).date()
        return date
    if('m ago' in dt_str):
        m = dt_str.split('m')[0]
        date = (datetime.now() - timedelta(minutes = int(m))).date()
        return date
    if('Just now' in dt_str):
        return datetime.now().date()

    date = parse(dt_str).date()
    return date
