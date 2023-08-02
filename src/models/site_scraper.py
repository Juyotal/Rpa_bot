import re

from RPA.Browser.Selenium import Selenium, By, WebDriverWait, ElementNotFound
from selenium.common.exceptions import (
    StaleElementReferenceException, 
    TimeoutException
)
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils import get_post_date, js_code

def get_tag_contents(web_element, tag):
    return [element for element in web_element.find_elements(By.TAG_NAME, tag)]


def parse_news_data(news_element):
    '''
    Get data to be populated in excell from the news element
    '''
    title = (get_tag_contents(news_element, 'h4')[0]).text
    paragraphs = get_tag_contents(news_element, 'p')
    desc = paragraphs[1].text if len(paragraphs) >= 2 else ''
    img_path = ''

    try:
        img = news_element.find_element(By.TAG_NAME, 'img')
        img_path += img.get_attribute('src')
    except Exception:
        pass

    return ({
        'title': title,
        'description': desc,
        'money_found': bool(re.search(r"\$[\d,.]+|[\d,.]+ dollars|\d+ USD", f"{title} {desc}")),
        'img_path': img_path
    })


class SiteScrapper:
    def __init__(self, logger, url):
        self.logger = logger
        self.driver = Selenium()
        self.driver.set_selenium_implicit_wait(5)
        self.driver.open_available_browser(url, maximized=True)


    def close_policy_modal(self):
        '''
        There is a Updated Policy modal that pops when you enter page for first time
        Instead of a Cookie PopUp. But I beliee it is temporary so took necessary actions
        and they do not even as you Permission for your cookies. How Rude.
        '''
        self.logger.info("Closing policy banner...")

        try:
            self.driver.wait_until_element_is_visible('id:complianceOverlay')
        except AssertionError:
            return
        
        modal_element = self.driver.find_element('id:complianceOverlay') 
        close_button = modal_element.find_element(By.XPATH, '//button[text()="Continue"]')
        close_button.click()



    def search(self, search_phrase):
        '''
        Search_Phrase is Input in the search bar and submitted for results here
        '''
        try:
            self.logger.info("Inputing search phrase and submiting ...")
            self.driver.click_element( 'xpath://button[@data-test-id="search-button"]')
            self.driver.input_text('xpath://input[@data-testid="search-input"]', search_phrase)
            self.driver.click_element('xpath://button[@data-test-id="search-submit"]')
        except Exception as exception:
            self.logger.info('search unresolved due to %s', exception)


    def sort(self, latest=True):
        '''
        Obtained Articles are Sorted In Descending order of oldness(If it is a word)
        '''
        sort_by = "newest" if latest else "oldest"
        try:
            self.logger.info('Sorting Articles by %s', sort_by)
            self.driver.wait_until_element_is_visible('xpath://select[@data-testid="SearchForm-sortBy"]')
            self.driver.click_element('xpath://select[@data-testid="SearchForm-sortBy"]')
            self.driver.click_element('xpath://option[@value="' + sort_by + '"]')
        except Exception as exception:
            self.logger.info('search unresolved due to %s', exception)


    def apply_filter(self, filter_list):
        '''
        And Boom, the necessary Filters are Applied
        Or Just ignored if not found on website-section-filter
        '''
        self.logger.info("Applying filters...")
        try:
            self.driver.click_button_when_visible('xpath://button[@data-testid="search-multiselect-button"]')
        except AssertionError:
            self.logger.info("Section button not found")
            return

        dropdown_list = self.driver.find_element('xpath://ul[@data-testid="multi-select-dropdown-list"]')

        if 'Any' in filter_list:

            try:
                self.driver.click_element('xpath://input[contains(@value, "any")]')
            except: 
                self.logger.info('Option Not Found')
            
            self.driver.click_element('xpath://button[@data-testid="search-multiselect-button"]')
            return
        
        options_list = []
        for li in get_tag_contents(dropdown_list, 'li'):
            option_element = li.find_element(By.TAG_NAME, 'input')
            option = option_element.get_attribute('value').split('|')[0]
            options_list.append(option)

        filter_list = list(set(options_list) & set(filter_list))

        for filter in filter_list:
            self.driver.click_element('xpath://input[contains(@value, "' + filter + '")]')

        self.driver.click_element('xpath://button[@data-testid="search-multiselect-button"]')
       
        
    def get_news(self, months, search_phrase, news_dicts = []):
        '''
        Finally, Here We Obtain our News Dictionary ready to be saved in excel.
        Oww! actually, one more field is needed which is image-save-path and
        is obtained from our Output Class, after image is saved.
        '''
        self.logger.info('extracting news data')
        months = 1 if months == 0 else months    
        months -= 1

        today = datetime.now().date()
        try:
            limit = today.replace(day=1) - relativedelta(months=months)
        except ValueError:
            limit = datetime(1950,1,1).date()
        
        self.logger.info('Limit date set to %s', str(limit))
        
        date = today
        elements_list = None
        processed_articles = 0

        def list_refresh(self):
            elts_list = self.driver.find_elements(By.XPATH, '//li[@data-testid="search-bodega-result"]')
            return len(elts_list) != processed_articles

        while(date >= limit):
            self.logger.info('Articels extracted: %s', processed_articles)

            WebDriverWait(self.driver, 5).until(list_refresh)
            elements_list = self.driver.find_elements('xpath://li[@data-testid="search-bodega-result"]')
            
            if(len(elements_list) == processed_articles):
                break
            
            for i in range(processed_articles, len(elements_list)):
                element = elements_list[i]
                try:
                    date_str = get_tag_contents(element, 'span')[0]
                    date = get_post_date(date_str.text)
                    news_data = parse_news_data(element)
                except StaleElementReferenceException:
                    self.driver.reload_page()
                    processed_articles  = 0
                    self.logger.error('Stale Element. Will Refresh Page.')
                    continue
                    
                if date < limit:
                    break
                  
                processed_articles += 1
                search_phrase_count = news_data['title'].lower().count(search_phrase.lower()) + news_data['description'].lower().count(search_phrase.lower())
                news_dicts.append({
                    'date': date.strftime("%Y-%m-%d"),
                    **news_data,
                    'count': search_phrase_count,
                })
            
            try:
                self.logger.info("Requesting more articles...")
                self.driver.execute_javascript(js_code) # just scrolling to the button.
                show_more = self.driver.find_element('xpath://button[@data-testid="search-show-more-button"]')
                show_more.click()
            except ElementNotFound:
                self.logger.info("No more articles to request")
                break
            except Exception as exception:
                self.logger.info("Error requesting more articles: %s", exception)
                break


        return news_dicts