from robocorp.tasks import task
from models.site_scraper import SiteScrapper
from models.output import Output
from models.work_item import WorkItem
from utils import configure_logger


url = 'https://www.nytimes.com/'

logger = configure_logger()

params = {
  "search_phrase": "currency",
  "category": [
    "Any"
 ],
  "num_months": 1
}

@task
def run_scraper() -> None:

    search_phrase = params['search_phrase']
    category = params['category']
    num_months = params['num_months']

    logger.info('Scrapping NYT for: %s', search_phrase)

    try:
        scrapper = SiteScrapper(logger, url)
    except Exception as e:
        logger.error("Could Not Start Browser Driver Because: %s", e)
        return

    work_item = WorkItem(logger)
    output = Output(logger, search_phrase)


    (search_phrase, category, num_months) = work_item.get_input_params(
        search_phrase, category, num_months
    )

    scrapper.close_policy_modal()
    scrapper.search(search_phrase)
    scrapper.sort()
    scrapper.apply_filter(category)
    news = scrapper.get_news(num_months, search_phrase)
    output.store_news(news)
    work_item.get_output([output.excel_file, output.zip_output], search_phrase)


if __name__ == "__main__":    
    run_scraper()
