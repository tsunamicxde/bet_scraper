import multiprocessing
import time

from scraper.dota2_upcoming_scraper import DotaUpcomingScraper
from scraper.dota2_live_scraper import DotaScraper
from scraper.cs2_live_scraper import CsScraper
from scraper.cs2_upcoming_scraper import CsUpcomingScraper
from scraper.lol_live_scraper import LolScraper
from scraper.lol_upcoming_scraper import LolUpcomingScraper
from scraper.ml_live_scraper import MlScraper
from scraper.ml_upcoming_scraper import MlUpcomingScraper


def run_scraper(scraper_class):
    try:
        scraper = scraper_class()
        scraper.setup_method()
        scraper.scrape()
        scraper.teardown_method()
    except KeyboardInterrupt:
        print("Программа остановлена пользователем.\n")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        scraper_classes = [DotaUpcomingScraper, DotaScraper, CsScraper, CsUpcomingScraper,
                           LolScraper, LolUpcomingScraper, MlScraper, MlUpcomingScraper]

        processes = []
        for scraper_class in scraper_classes:
            time.sleep(5)
            process = multiprocessing.Process(target=run_scraper, args=(scraper_class,))
            processes.append(process)
            process.start()
    except KeyboardInterrupt:
        print("Программа остановлена пользователем.")
    except Exception:
        pass
