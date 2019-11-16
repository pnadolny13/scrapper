from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import time


class WebParser:

    CSV_FILE = 'outfile_path'
    blacklist = [
        'Find a Home',
        'My Searches',
        'Favorites',
        'Messages',
        'My Agent',
        'Help',
        'Legend',
        'Ruler',
        'Disclaimer'
    ]

    def __init__(self):
        option = webdriver.ChromeOptions()
        option.add_argument(" — incognito")
        self.browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=option)
        self.browser.get('https://smartmls.mlsmatrix.com/Matrix/Public/Portal.aspx?k=1713938X9VG6&p=DE-a-735')
        time.sleep(2)

    def _get_mls_id_links(self):
        mls_id_links = []
        elems = self.browser.find_elements_by_tag_name('a')
        for elem in elems:
            text = elem.text
            if text and text not in self.blacklist and ' ' not in text:
                mls_id_links.append(text)
        return mls_id_links

    def _go_to_property_display_page(self, mls_id):
        link = self.browser.find_element_by_link_text(mls_id)
        link.click()
        # time.sleep(2)
        while not self._page_loaded('Notes for you and your agent', text=True):
            time.sleep(2)

    def _get_description(self, soup):
        spans = soup.find_all('span', {'class': 'd-textSoft'})
        for span in spans:
            return span.get_text()

    def _parse_html(self):
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        property_details = ['test_column']
        description = self._get_description(soup)
        property_details.append(description)
        return property_details

    def _append_to_csv(self, property_details, headers=None):
        with open(self.CSV_FILE, 'a', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            if headers:
                writer.writerow(headers)
            writer.writerows([property_details])
            # writer.writerow(property_details)

    def _go_back_home(self, mls_id):
        back_link = self.browser.find_element_by_xpath('//button[@id="_ctl0_m_btnClosePILP"]')
        back_link.click()
        # expect current id to be back mls_id
        while not self._page_loaded(mls_id):
            time.sleep(2)

    def _page_loaded(self, id, text=False):
        try:
            if text:
                text = self.browser.find_element_by_tag_name('body').text
                if id not in text:
                    raise Exception
            else:
                self.browser.find_element_by_link_text(id)
            return True
        except Exception:
            return False

    def main(self):
        mls_id_links = self._get_mls_id_links()
        for mls_id in mls_id_links:
            print(mls_id)
            self._go_to_property_display_page(mls_id)
            property_details = self._parse_html()
            self._append_to_csv(property_details)
            self._go_back_home(mls_id)


if __name__ == "__main__":
    mls = WebParser()
    mls.main()
