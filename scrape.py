import requests, time
from bs4 import BeautifulSoup
import pandas as pd

def main():
    df = pd.DataFrame(columns=["article", "link", "doi", "authors", "keywords", "citations", "fcr", "rcr", "year", "issue", "volume", "downloaded"])
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for year in range(2012, 2021):
        issue = year - 1992
        for volume in range(1, 5):
            articles = []
            while not articles:
                time.sleep(1)
                page = requests.get(f"https://direct.mit.edu/evco/issue/{issue}/{volume}", headers=headers)
                soup = BeautifulSoup(page.text, "lxml")
                articles = soup.find_all('a', class_="viewArticleLink")

            for article in articles:
                heading = None
                doi = None
                while True:
                    time.sleep(1)
                    page = requests.get(f"https://direct.mit.edu/{article.get('href')}", headers=headers)
                    soup = BeautifulSoup(page.text, "lxml")
                    authors = ", ".join([author.find('a', class_="linked-name").get_text().strip() for author in soup.find_all("div", class_="al-author-name")])
                    keywords = ", ".join([keyword.get_text().strip() for keyword in soup.find_all('a', class_="kwd-part kwd-main")])
                    heading = soup.find("h1", class_="wi-article-title").get_text().strip() if soup.find("h1", class_="wi-article-title") else None
                    doi = soup.find("div", class_="citation-doi").get_text().strip() if soup.find("div", class_="citation-doi") else None
                    if heading and doi:
                        print(year, volume, doi)
                        citations = fcr = rcr = None
                        while True:
                            time.sleep(1)
                            page = requests.get(f"https://badge.dimensions.ai/details/doi/{'/'.join(doi.split('/')[-2:])}/metrics.json", headers=headers)
                            if not page.status_code == 200:
                                continue
                            metrics = page.json()
                            if metrics.get("status") == 404:
                                break
                            citations = metrics["times_cited"]
                            fcr = metrics["field_citation_ratio"]
                            rcr = metrics["relative_citation_ratio"]
                            if citations != None:
                                break

                        print(citations, fcr, rcr)
                        df.loc[len(df.index)] = [heading, article.get('href'), doi, authors, keywords, citations, fcr, rcr, year, issue, volume, False]
                        break
            
        df.to_csv("output/ecj-articles_2012-2020.csv", index=False)


if __name__=="__main__":
    start = time.time()
    main()
    print(f"elapsed time: {time.time()-start}")
