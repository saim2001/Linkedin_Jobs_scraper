from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pprint
from pycountry import countries
from utils import *
from rough import test_list


def initiate_driver(URL):
    try:
        option = Options()
        # Set the user data directory and profile directory for Chrome
        option.add_argument("--user-data-dir=C:/Users/saim rao/AppData/Local/Google/Chrome/User Data/")
        option.add_argument("--profile-directory=Profile 4")
        # Initialize Chrome driver with the specified options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
        # Open the specified URL
        driver.get(URL)
        print('\u2713', 'Driver initiated successfully')
        time.sleep(5)
        return driver
    except Exception as e:
        print('\u2717', e)
        return None


def search_jobs(by, driver):
    # Search for jobs using the provided search term
    wait_for_element_to_load(By.XPATH, "//*[@placeholder='Search']", driver).send_keys(by)
    wait_for_element_to_load(By.XPATH, "//*[@placeholder='Search']", driver).send_keys(Keys.ENTER)
    time.sleep(3)
    # Click on the "Jobs" button to filter the search results to show only jobs
    waitforelemtobeclickable(By.XPATH, "//nav[@aria-label='Search filters']//button[text()='Jobs']", driver).click()
    return 0


def scrape_jobs(driver):
    # Scrape the job elements from the search results
    jobs = wait_for_elements_to_load(By.XPATH, "//li[contains(@class, 'jobs-search-results')]", driver)
    return jobs


def scrape_job_details(driver):
    jobs = scrape_jobs(driver)
    jobs_list = []

    for job in jobs:
        job_dict = {}
        # Scroll to the job element and click on it to view job details
        driver.execute_script("arguments[0].scrollIntoView();", job)
        job.click()
        time.sleep(2)
        # Extract job title
        job_title = wait_for_element_to_load(By.XPATH, "//h2[contains(@class,'job-title')]", driver).text
        try:
            # Extract company name and LinkedIn profile link if available
            company = wait_for_element_to_load(By.XPATH, "//span[contains(@class, 'company-name')]/a", driver)
            company_name = company.text
            company_linkedin = company.get_attribute('href')
        except:
            company = wait_for_element_to_load(By.XPATH, "//span[contains(@class, 'company-name')]", driver)
            company_name = company.text
            company_linkedin = None
        try:
            # Extract job location
            location = driver.find_element(By.XPATH, "(//span[contains(@class, 'bullet')])[1]").text
        except:
            location = None
        # Find the corresponding country name based on the location
        if location != None:
            for country in countries:
                if country.name in location:
                    job_country = country.name
        try:
            # Extract recruiter name and LinkedIn profile link if available
            recruiter_name = driver.find_element(By.XPATH, "//div[contains(@class,'hirer')]/a").text
            recruiter_linkedin = driver.find_element(By.XPATH, "//div[contains(@class,'hirer')]/a").get_attribute('href')
        except:
            recruiter_name = None
            recruiter_linkedin = None
        # Extract the date posted
        date = extract_date_from_text(driver.find_element(By.XPATH, "//span[contains(@class,'posted-date')]").text)
        # Populate the job details dictionary
        job_dict['position'] = job_title
        job_dict['country'] = job_country
        job_dict['location'] = location
        job_dict['recruiter_name'] = recruiter_name
        job_dict['recruiter_linkedin'] = recruiter_linkedin
        job_dict['date_posted'] = date
        job_dict["company name"] = company_name
        job_dict["company linkedin"] = company_linkedin

        jobs_list.append(job_dict)
    return jobs_list


def scrape_all_jobs(driver):
    pages = None
    try:
        # Check if there are multiple pages of search results
        pages = wait_for_elements_to_load(By.XPATH, "//ul[contains(@class,'pagination')]//button", driver)

    except:
        pass
    if pages is not None:
        no_pages = len(pages)
        job_list_all = []
        for page in range(no_pages):
            pages = wait_for_elements_to_load(By.XPATH, "//ul[contains(@class,'pagination')]//button", driver)
            no_pages = len(pages)
            try:
                # Click on the page button to navigate to the next page
                pages[page].click()
            except Exception as e:
                print(e)
                pass
            time.sleep(3)
            # Scrape job details from the current page
            jobs_list = scrape_job_details(driver)
            job_list_all.extend(jobs_list)
        return job_list_all
    else:
        return scrape_job_details(driver)


def scrape_company(job_list, driver):
    company_dict_unq = {}
    try:
        for job in job_list:
            if job["company name"] not in company_dict_unq:
                if job["company linkedin"] is not None:
                    # Visit the company's LinkedIn page
                    driver.get(job["company linkedin"])
                    try:
                        # Click on the "About" section of the company page
                        wait_for_element_to_load(By.XPATH, "//a[contains(@class,'org-page') and text()='About']", driver).click()
                    except:
                        while True:
                            pass
                    try:
                        # Extract the company's website
                        website = wait_for_element_to_load(By.XPATH, "//dt[text()='Website']//following-sibling::dd//a", driver).get_attribute('href')
                    except:
                        try:
                            website = wait_for_element_to_load(By.XPATH, "//span[text()='Contact us']//parent::a", driver).get_attribute('href')
                        except Exception as e:
                            website = None
                            print(e)
                    try:
                        # Extract the company's address
                        addresses = wait_for_element_to_load(By.XPATH, "(//div[contains(@class,'org-location') and not(contains(@class,'map-container'))]//p)[1]", driver).text
                    except Exception as e:
                        print(e)
                        try:
                            addresses = wait_for_element_to_load(By.XPATH, "(//dt[text()='Headquarters']//following-sibling::dd)[1]", driver).text
                        except Exception as e:
                            addresses = None
                            print(e)
                    comp_country = None
                    for country in countries:
                        if addresses is not None:
                            if country.alpha_2 in addresses.split(", "):
                                comp_country = country.name

                    company_dict = {}
                    company_dict["website"] = website
                    company_dict["address"] = addresses
                    company_dict["country"] = comp_country
                    job["company"] = company_dict
                    company_dict_unq[job["company name"]] = company_dict

            else:
                job["company"] = company_dict_unq[job["company name"]]
        print('\u2713', 'jobs scraped successfully')
        return job_list
    except:
        print('\u2717', e)
        return 1


def insert_into_db(job_lst):
    # Create a database connection
    con = create_db_connection()

    # Create a cursor for executing SQL queries
    cursor = create_db_cursor(con)

    # Lists to store company and job data
    companies_data = []
    jobs_data = []

    try:
        # Iterate over each job in the job_lst
        for job in job_lst:
            if 'company' in job:
                # If the job has company information, create a tuple with company data
                temp_tuple_comp = (
                    job["company name"],
                    job["company"]["website"],
                    job["company linkedin"],
                    job["company"]["country"],
                    job["company"]["address"],
                    None,
                    None
                )
            else:
                # If the job does not have company information, create a tuple with None values
                temp_tuple_comp = (
                    job["company name"],
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
                )
            companies_data.append(temp_tuple_comp)

            # Create a tuple with job data
            temp_tuple_job = (
                job["position"],
                job["country"],
                job["location"],
                job["recruiter_name"],
                job["recruiter_linkedin"],
                job["date_posted"]
            )
            jobs_data.append(temp_tuple_job)

        # SQL query to insert company data into the database
        query_1 = "INSERT INTO companies_demand (name, website, linkedin, country, address, domain, twitter) values(%s, %s, %s, %s, %s, %s, %s)"

        # Insert the first company's data
        cursor.execute(query_1, companies_data[0])
        first_id_inserted = cursor.lastrowid

        # Insert the remaining companies' data
        cursor.executemany(query_1, companies_data[1:-1])

        # Insert the last company's data
        cursor.execute(query_1, companies_data[-1])
        last_id_inserted = cursor.lastrowid

        # Commit the changes to the database
        con.commit()

        # SQL query to select the inserted company IDs
        select_query = "SELECT id FROM companies_demand WHERE id >= %s and id <= %s"

        # Execute the select query with the inserted company IDs
        cursor.execute(select_query, (first_id_inserted, last_id_inserted))

        # Fetch all the inserted company IDs
        inserted_ids = cursor.fetchall()

        # SQL query to insert job data into the database
        query_2 = """
              INSERT INTO jobs_demand (company_id, position, country, location, recruiter_name, recruiter_linkedin, date_posted)
              values(%s, %s, %s, %s, %s, %s, %s)
          """

        # Iterate over the inserted company IDs and corresponding job data
        for id, job in zip(inserted_ids, jobs_data):
            temp_tuple = (id[0],) + job
            # Replace the original job data with the modified tuple that includes the company ID
            jobs_data[jobs_data.index(job)] = temp_tuple

        # Insert the job data into the database
        cursor.executemany(query_2, jobs_data)

        # Commit the changes to the database
        con.commit()

        # Close the cursor and the database connection
        cursor.close()
        con.close()

        # Print a success message
        print('\u2713', 'Data inserted successfully')
    except Exception as e:
        # Print an error message if an exception occurs
        print('\u2717', e)

    # Return 0 as the function result
    return 0



if __name__ == '__main__':
    # Initialize the Chrome driver
    driver = initiate_driver('https://www.linkedin.com/')
    # Search for jobs with the specified search term
    search_jobs = search_jobs('python developer', driver)
    # Scrape all job details
    scraped_jobs = scrape_all_jobs(driver)
    pprint.pprint(scraped_jobs)
    print(len(scraped_jobs))
    # Scrape company details for each job
    job_list = scrape_company(scraped_jobs, driver)
    pprint.pprint(job_list)
    # Insert scraped data in DB
    insert_into_db(job_list)

