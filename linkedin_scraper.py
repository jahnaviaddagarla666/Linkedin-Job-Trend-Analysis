
"""linkedin_scraper.py – minimal LinkedIn job search scraper (educational)."""
import argparse, json, pathlib, time, uuid
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from tqdm import tqdm

BASE = "https://www.linkedin.com/jobs/search/?keywords={kw}&location={loc}&start={start}"

def make_driver(cookie):
    opts = Options()
    opts.add_argument('--headless')
    driver = webdriver.Firefox(options=opts)
    driver.get('https://www.linkedin.com')
    driver.add_cookie({'name': 'li_at', 'value': cookie, 'domain': '.linkedin.com'})
    return driver

def run(cfg_path):
    cfg = json.load(open(cfg_path))
    driver = make_driver(cfg['li_at'])
    raw_dir = pathlib.Path('data/raw'); raw_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    try:
        for term in tqdm(cfg['search_terms'], desc='terms'):
            for city in cfg['cities']:
                for p in range(cfg['pages']):
                    url = BASE.format(kw=quote_plus(term), loc=quote_plus(city), start=p*25)
                    driver.get(url); time.sleep(3)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    cards = soup.select('div.job-card-container')
                    for c in cards:
                        rows.append({
                            'title': c.select_one('h3').get_text(strip=True) if c.select_one('h3') else None,
                            'company': c.select_one('h4').get_text(strip=True) if c.select_one('h4') else None,
                            'location': c.select_one('span.job-card-container__metadata-item').get_text(strip=True) if c.select_one('span.job-card-container__metadata-item') else None,
                            'search_term': term,
                            'city': city
                        })
    finally:
        driver.quit()
    df = pd.DataFrame(rows)
    outfile = raw_dir / ('jobs_' + str(uuid.uuid4()) + '.jsonl')
    df.to_json(outfile, orient='records', lines=True)
    print('Saved', len(df), 'rows to', outfile)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--config', default='config.json'); a = ap.parse_args(); run(a.config)
