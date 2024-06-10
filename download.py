import requests, time
import pandas as pd
import pathlib
from bs4 import BeautifulSoup
from slugify import slugify

def main():
    df = pd.read_csv("output/ecj-articles_2012-2020.csv")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for i, row in df.iterrows():
        if row["downloaded"]:
            continue

        pathlib.Path(f"publications/{row['year']}/{row['volume']}").mkdir(parents=True, exist_ok=True) 
        print(row['year'], row['volume'])
        
        try:
            page = requests.get(f"https://sci-hub.st/{row['doi']}", headers=headers)
        except requests.exceptions.RequestException:
            continue

        soup = BeautifulSoup(page.text, "lxml")

        if soup.find('embed', id="pdf"):
            embed = soup.find('embed', id="pdf").get('src')
        else:
            continue

        url = f"https://sci-hub.st/{embed}" if embed[1] != "/" else f"https://{embed[2:]}"

        response = requests.get(url=url, headers=headers, stream=True)

        with open(f"publications/{row['year']}/{row['volume']}/{slugify(row['article'])}.pdf", "wb") as f:
            for chunk in response.iter_content(chunk_size=512*1024):
                f.write(chunk)

        df.at[i, 'downloaded'] = True
        
    df.to_csv("output/ecj-articles_2012-2020.csv", index=False)

if __name__=="__main__":
    start = time.time()
    main()
    print(f"elapsed time: {time.time()-start}")
