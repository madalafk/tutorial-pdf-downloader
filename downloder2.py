#!/usr/bin/python3
import multiprocessing as mp
from bs4 import BeautifulSoup
import requests
import time
import os
import sys
import weasyprint
import argparse
import fnmatch
import shutil

def get_page(url):
    while True:
        try:
            page_response = requests.get(url, headers={'User-Agent': 'Chrome'}, timeout=5)
            page_response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(page_response.content, "html.parser")
            return str(soup)
        except requests.RequestException as e:
            print(f"Could not connect to {url.split('/')[-1]}, retrying...")
            print(f"Error: {e}")
            time.sleep(1)

def download_tutorial(url, domain_name):
    print(f"Downloading {url}")
    page_content = get_page(url)
    links = [domain_name + a['href'] for a in BeautifulSoup(page_content, "html.parser").find_all("a", href=True)]
    pages = [get_page(link) for link in links]

    head = page_content[:page_content.find("<body")] + '\n<body>\n'
    head = head.replace("<style>", '<style>\n.prettyprint{\nbackground-color:#D3D3D3;\nfont-size: 12px;}\n')

    end = '\n</body>\n</html>'
    page = head + "".join(pages) + end
    tutorial = url.split("/")[-2]
    with open(os.path.join('..', 'temp', f"{tutorial}.html"), "w") as f:
        f.write(page)
    print(f"{tutorial} download completed")

def download_all_tutorials(urls, domain_name):
    processes = []
    for url in urls:
        p = mp.Process(target=download_tutorial, args=(url, domain_name))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

def convert_to_pdf(tutorial):
    tutorial = os.path.splitext(tutorial)[0]
    try:
        html_file = os.path.join('..', 'temp', f"{tutorial}.html")
        pdf_file = os.path.join('..', 'downloads', tutorial, f"{tutorial}.pdf")
        os.makedirs(os.path.dirname(pdf_file), exist_ok=True)
        print(f"Converting {tutorial} to PDF, please wait...")
        html = weasyprint.HTML(html_file)
        main_doc = html.render()
        pdf = main_doc.write_pdf()
        with open(pdf_file, 'wb') as f:
            f.write(pdf)
        print(f"{tutorial} PDF saved")
    except Exception as e:
        print(f"Error converting {tutorial} to PDF: {e}")

def convert_all_to_pdf():
    completed_tutorials = set()
    # Wait for downloads to finish (replace with actual download completion check)
    time.sleep(10)  # Replace with a mechanism that indicates download completion
    
    while os.listdir(os.path.join('..', 'temp')):
        tutorials = fnmatch.filter(os.listdir(os.path.join('..', 'temp')), '*.html')
    try:
        shutil.rmtree(os.path.join('..', 'temp'))
    except Exception as e:
        print(f"Failed to delete '../temp': {e}")

def main():
    parser = argparse.ArgumentParser(description="Download tutorials from Javatpoint or Tutorialspoint and convert them to PDF")
    parser.add_argument("-a", "--all", action="store_true", help="Download all tutorials from Javatpoint and Tutorialspoint")
    parser.add_argument("-j", "--javatpoint", action="store_true", help="Download all tutorials from Javatpoint")
    parser.add_argument("-t", "--tutorialspoint", action="store_true", help="Download all tutorials from Tutorialspoint")
    parser.add_argument("-u", "--urls", action="store_true", help="Download all tutorials mentioned in 'download_links.py'")
    args = parser.parse_args()

    if not os.path.exists(os.path.join('..', 'downloads')):
        os.makedirs(os.path.join('..', 'downloads'))
    os.makedirs(os.path.join('..', 'temp'), exist_ok=True)

    if args.all:
        download_all_tutorials([
            "https://www.javatpoint.com/",
            "https://www.tutorialspoint.com/tutorialslibrary.htm"
        ],
        "https://www.tutorialspoint.com/"
        )
