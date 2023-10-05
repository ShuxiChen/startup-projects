from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import matplotlib.pyplot as plt


driver = webdriver.Chrome()
driver.get('https://briian.com/ptt-search.htm')
driver.implicitly_wait(10)

# UX of temeperature on diet and preference
hotExp_keywords = ['吃東西燙到', '吃燙到', '貓舌頭', '喝燙到', '怕燙', '喝太燙', '熱飲', '喝冷掉', '咖啡冷掉', '喜歡喝熱', '生理期喝熱的', '燙口']

titles = []

def scrape_titles():
    for item in driver.find_elements(By.CSS_SELECTOR, 'a.gs-title'):
        titles.append(item.text)

def next_page(keywords_list):
    search = driver.find_element(By.NAME,'search')
    
    for keyword in keywords_list:
        search.clear()
        search.send_keys(keyword)
        time.sleep(1)
        search.send_keys(Keys.ENTER)
        time.sleep(1)
        
        # Scrape titles from the initial page
        scrape_titles()

        for page_num in range(2, 11):
            # Locate the search element again to avoid StaleElementReferenceException
            search = driver.find_element(By.NAME,'search')

            # Navigate to the next page if available
            css_selector = f'div[aria-label="第 {page_num} 頁"]'
            next_page = driver.find_element(By.CSS_SELECTOR, css_selector)
            next_page.click()
            
            # Scrape titles from the current page
            scrape_titles()
            time.sleep(3)
    return titles


def extract_boards(titles):
    df = pd.DataFrame(titles, columns=['Title'])
    df.drop_duplicates(inplace=True)

    # Extract content after '板' in 'Title' column
    df_split = df['Title'].str.split('板').str[1]
    df_split = df_split.rename('Board').to_frame()
    df_split = df_split['Board'].str.split(' ').str[0]
    df_split.dropna(inplace=True)
    df_split = pd.DataFrame({'Board': df_split})
    
    return df_split


def bar_chart(df):
    # Calculate board counts
    board_counts = df['Board'].value_counts()

    # Create a bar chart for the top 10 boards
    plt.bar(board_counts.head(10).index, board_counts.head(10).values)

    # Add labels and title
    plt.xticks(fontsize=8, rotation='vertical')
    plt.xlabel('Board')
    plt.ylabel('Count')
    plt.title('Top 10 Ptt Boards for Hot Drink Experience')

    plt.show()


if __name__ == '__main__':
    next_page(hotExp_keywords)
    driver.quit()
    df_split = extract_boards(titles)
    bar_chart(df_split)
