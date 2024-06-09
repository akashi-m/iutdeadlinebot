import requests
from bs4 import BeautifulSoup

# URLs for login and the target page
login_url = 'https://eclass.inha.ac.kr/login/index.php'
target_url = 'https://eclass.inha.ac.kr/'

# Login credentials
payload = {
    'username': 'U2110207',  # replace with your username
    'password': 'Dovenskab_13'   # replace with your password
}

# Using session as a context manager
with requests.Session() as session:
    # Get the login page to fetch any necessary cookies or tokens
    login_page = session.get(login_url)
    login_page.raise_for_status()  # Ensure the request was successful

    # Parse the login page for any hidden fields (if necessary, for example, CSRF tokens)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    hidden_inputs = soup.find_all('input', type='hidden')
    for hidden_input in hidden_inputs:
        payload[hidden_input['name']] = hidden_input['value']

    # Post the login credentials
    response = session.post(login_url, data=payload)
    response.raise_for_status()  # Ensure the login request was successful

    # Check if login was successful by fetching the target page
    response = session.get(target_url)
    response.raise_for_status()  # Ensure the request was successful

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find and extract the content of <h3> tags within the specified structure
    course_list = soup.select('ul.my-course-lists.coursemos-layout-0 li.course_label_re_02')
    for course in course_list:
        h3_tag = course.find('h3')
        if h3_tag:
            subject_name = h3_tag.get_text(strip=True)
            link_tag = course.find('a', class_='course_link')
            if link_tag:
                subject_link = link_tag.get('href')
                print(f"Subject: {subject_name}")

                # Now, let's parse the assignment page
                assignment_response = session.get(subject_link)
                assignment_response.raise_for_status()  # Ensure the request was successful

                # Parse the assignment page content
                assignment_soup = BeautifulSoup(assignment_response.content, 'html.parser')

                # Extract the link to the Assignment activity
                assignment_link_tag = assignment_soup.find('ul', class_='add_activities').find('a', string='Assignment')
                if assignment_link_tag:
                    assignment_link = assignment_link_tag.get('href')

                    # Now, let's parse the assignment details page
                    assignment_details_response = session.get(assignment_link)
                    assignment_details_response.raise_for_status()  # Ensure the request was successful

                    # Parse the assignment details page content
                    details_soup = BeautifulSoup(assignment_details_response.content, 'html.parser')

                    # Extract the content of classes "cell c1", "cell c2", "cell c3"
                    rows = details_soup.select('tbody tr')
                    for row in rows:
                        cell_c1 = row.find('td', class_='cell c1')
                        cell_c2 = row.find('td', class_='cell c2')
                        cell_c3 = row.find('td', class_='cell c3')

                        if cell_c1 and cell_c2 and cell_c3:
                            assignment_title = cell_c1.get_text(strip=True)
                            due_date = cell_c2.get_text(strip=True)
                            status = cell_c3.get_text(strip=True)
                            print(f"Assignment Title: {assignment_title}, Due Date: {due_date}, Status: {status}")
