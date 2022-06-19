# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "image_link": image_link_title(browser)
    }



    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


def image_link_title(browser):
# 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

# 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

# 3. Write code to retrieve the image urls and titles for each hemisphere.
    for x in range(0,4):
        # visit the initial site
        html = browser.html
        img_soup = soup(html, 'html.parser')

        # grab the link at range number
        img_box = img_soup.find('div', class_='collapsible results').find_all('div', class_='item')
        image_link = img_box[x].find('a').get('href')
        image_title = img_box[x].find('h3').text

        # visit the new link
        new_img_url_href = url + image_link
        browser.visit(new_img_url_href)
        html = browser.html
        img_soup = soup(html, 'html.parser')

        # grab the href for the jpg
        new_img_url = img_soup.find('div', class_='downloads').find('a').get('href')
        img_jpeg = url + new_img_url

        # save to dict
        hemisphere_image_urls_dict = {}
        hemisphere_image_urls_dict["img_url"] = img_jpeg
        hemisphere_image_urls_dict["title"] = image_title
        hemisphere_image_urls.append(hemisphere_image_urls_dict)
        browser.back()

    # 4. Print the list that holds the dictionary.
    return hemisphere_image_urls 


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


