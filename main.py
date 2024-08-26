import requests  # pip install requests
import time
from bs4 import BeautifulSoup  # pip install beautifulsoup4
import random
import flet as ft  # pip install flet
import json
import threading
import traceback


# to_process will be used as a flag to stop the scraper thread whenever needed
# running will be used to check if the scraper thread is running or not, with this we can prevent the user from starting the scraper thread again and again
global to_process
global running
to_process = True
running = False


def get_last_page(main_url: str) -> int:
    # Here we will create a UserAgent object to generate a random user
    # agent which will be used to make sure requests are not blocked
    headers = {
        "authority": "www.gulftalent.com",
        "method": "GET",
        "path": "/jobs/title/hospital",
        "scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",

    }
    # Fetch the first page and extract the last page number from it
    response = requests.get(main_url, headers=headers)
    # Raise an HTTPError if the HTTP request returned an unsuccessful status
    response.raise_for_status()
    # now create a soup object
    soup = BeautifulSoup(response.text, "html.parser")
    # find <a href="/jobs/title/hospital/6" data-cy="pagination-last-btn"> (location of last page link)
    last_page = soup.find("a", {"data-cy": "pagination-last-btn"})["href"]
    return int(last_page.split("/")[-1])


def fetch_all_job_links_and_date(main_url: str, last_page: int) -> list:
    # Here we will create a UserAgent object to generate a random user
    # agent which will be used to make sure requests are not blocked
    headers = {
        "authority": "www.gulftalent.com",
        "method": "GET",
        "path": "/jobs/title/hospital",
        "scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
    }
    all_job_links = []
    global to_process
    # loop through all the pages and extract the job links first
    for page in range(1, last_page + 1):
        if not to_process:
            return all_job_links
        check = 0
        if check == 5:
            raise Exception("Failed to fetch (Site isn't working properly, please try in a bit)")
        while True:
            try:
                response = requests.get(main_url + f"/{page}", headers=headers)
                # Raise an HTTPError if the HTTP request returned an unsuccessful status
                response.raise_for_status()
                # now create a soup object
                soup = BeautifulSoup(response.text, "html.parser")
                # class="text-base title text-body space-top-tiny space-bottom-none text-overflow"
                h2_tags = soup.find_all(
                    "h2",
                    {
                        "class": "text-base title text-body space-top-tiny space-bottom-none text-overflow"
                    },
                )
                # h2 tags here contains the job links that we need to extract
                for h2_tag in h2_tags:
                    current_list = []
                    # try getting the href attribute of the a tag (Sometimes it's possible that the href attribute is not present)
                    try:
                        current_list.append(h2_tag.find("a")["href"])
                    except Exception as e:
                        print(e)
                    # Now we need to extract the date of the job posting, find the parent td tag of the h2 tag
                    parent_td_tag = h2_tag.find_parent("td")
                    # now in next the next 2nd td tag
                    date = parent_td_tag.find_next("td").find_next("td").text
                    current_list.append(date)
                    all_job_links.append(current_list)
                break
            except Exception as e:
                print(e)
                check += 1
        time.sleep(random.randint(1, 3))
    return all_job_links


def parse_link(base_url: str, link: str, date: str) -> dict:
    check = 0
    while True:
        if check == 5:
            raise Exception("Failed to fetch (Site isn't working properly, please try in a bit)")
        try:
            # create a dictionary to store the information for each job link
            main_dict = {
                "hospital": "",
                "location": "",
                "job_description": "",
                "job_posting_date": "",
            }
            # We need to extract the following information from the job link
            # hospital, location, job description, job posting date
            headers = {
                "authority": "www.gulftalent.com",
                "method": "GET",
                "path": "/jobs/title/hospital",
                "scheme": "https",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Priority": "u=0, i",
                "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",

            }
            response = requests.get(base_url + link, headers=headers)
            # Raise an HTTPError if the HTTP request returned an unsuccessful status
            response.raise_for_status()
            # now create a soup object
            soup = BeautifulSoup(response.text, "html.parser")
            # first h2 tag is the hopsital name and second h2 tag is the location
            h2_tags = soup.find_all("h2")
            # loop through the h2 tags and extract the hospital and location, if they are not present then skip them
            for num, h2_tag in enumerate(h2_tags):
                try:
                    if num == 0:
                        main_dict["hospital"] = h2_tag.text.strip()
                    elif num == 1:
                        pre_process = h2_tag.text.strip().split(",")
                        try:
                            main_dict["location"] = (
                                pre_process[0].strip() + "," + pre_process[1].strip()
                            )
                        except IndexError:
                            main_dict["location"] = pre_process[0].strip()
                except Exception as e:
                    import traceback

                    traceback.print_exc()
            # Extract the job description
            # find div class="container"
            div_tag = soup.find("div", {"class": "panel-body content-visibility-auto"})
            main_dict["job_description"] = (
                div_tag.text.replace("Easy Apply", "")
                .replace("Job description / Role", "")
                .replace("  ", " ")
                .strip()
            )
            # Extract the employment type from job description, also using a bit of regex to remove unecessary spaces and things
            main_dict["employement_type"] = (
                main_dict["job_description"]
                .split("\n\n\n")[0]
                .replace("\n", "")
                .strip()
                .split("  ")[-1]
                .split("\n")[0]
            )
            main_dict["job_description"] = (
                div_tag.text.replace("Easy Apply", "")
                .replace("Job description / Role", "")
                .replace("  ", " ")
                .split("\n\n\n", 2)[2]
                .replace("\n", "")
                .replace("Apply Now", "")
                .strip()
            )
            main_dict["job_description"] = (
                repr(main_dict["job_description"])
                .replace("\\n", " ")
                .replace("\\r", " ")
                .replace("\\t", "   ")
            )
            main_dict["job_posting_date"] = date.strip()
            return main_dict
        except Exception as e:
            print(e)
            time.sleep(random.randint(1, 3))
            check += 1


def check_settings() -> None:
    # check if settings.json file is present or not, if not then create one with default settings
    try:
        with open("settings.json", "r") as file:
            pass
    except FileNotFoundError:
        with open("settings.json", "w") as file:
            # By default, option to scrape all the jobs is selected
            # Also, the max delay is set to 1-3 seconds
            # file name is set to jobs.csv and link is set to scrape hospital jobs
            settings = {
                "main_url": "https://www.gulftalent.com/jobs/title/hospital",
                "max_delay": "1-3",
                "file_name": "jobs.csv",
                "max_jobs": 0,
            }
            json.dump(settings, file)


def user_interface(page: ft.Page):
    # create a function to save the settings in the settings.json file whenever the user changes the input and hits enter
    def save_settings(param, file_name: str = "settings.json") -> None:
        with open(file_name, "r") as file:
            settings = json.load(file)
        if param == "main_url":
            settings[param] = url_field.value
        elif param == "file_name":
            settings[param] = file_name_field.value
        elif param == "max_delay":
            settings[param] = max_delay_field.value
        elif param == "max_jobs":
            settings[param] = int(max_jobs_field.value)
        with open(file_name, "w") as file:
            json.dump(settings, file)

    # create a function to start the main scraper thread
    # this function will be called whenever the user hits the start button
    def main_scraper() -> None:
        try:
            # Load latest settings from the settings.json file
            with open("settings.json", "r") as file:
                settings = json.load(file)
            main_url = settings["main_url"]
            from_sec, to_sec = settings["max_delay"].split("-")
            # get the last page number
            check = 0
            while True:
                if check == 5:
                    break
                try:
                    last_page = get_last_page(main_url)
                    break
                except Exception as e:
                    print(e)
                    time.sleep(random.randint(1, 3))
                    check += 1
                    if check == 5:
                        error = traceback.format_exc()
                        raise error
            # get all the job links and their posting dates
            all_job_links_and_dates = fetch_all_job_links_and_date(main_url, last_page)
            # Now we need to parse each link and extract the required information
            # define the base url
            base_url = "https://www.gulftalent.com"
            # if the max_jobs is set to 0 then scrape all the jobs
            if int(settings["max_jobs"]) != 0:
                all_job_links_and_dates = all_job_links_and_dates[
                    : int(settings["max_jobs"])
                ]
            global to_process
            for element in all_job_links_and_dates:
                if not to_process:
                    return
                link, date = element
                # save all the data in a csv file
                try:
                    with open(settings["file_name"], "r") as file:
                        pass
                except FileNotFoundError:
                    try:
                        with open(settings["file_name"], "w") as file:
                            file.write(
                                "Link,Hospital,Location,Job Description,Job Posting Date,Employment Type\n"
                            )
                    except:
                        # show a dialog box saying that this name is not valid, please enter a valid name
                        def close_dialog(e):
                            dlg.open = False
                            page.update()
                        dlg = ft.AlertDialog(
                            title=ft.Text("Error"),
                            content=ft.Text(f"The file name is not valid, please enter a valid name..."),
                            actions=[ft.ElevatedButton("OK", on_click=close_dialog)],
                            actions_alignment=ft.MainAxisAlignment.CENTER,
                        )
                        page.overlay.append(dlg)
                        dlg.open = True
                        page.update()
                        return
                # parse the link
                data = parse_link(base_url, link, date)
                # save the data in the csv file
                with open(settings["file_name"], "a", encoding="utf-8") as file:
                    # save the link too
                    file.write(
                        f"https://www.gulftalent.com{link},{data['hospital'].replace(',', '')},{data['location'].replace(',','|')},{data['job_description'].replace(',', '')},{data['job_posting_date'].replace(',', ' ')},{data['employement_type'].replace(',', ' ')}\n"
                    )
                # This delay is important and is recommended to not be set at zero to avoid getting blocked
                time.sleep(random.randint(float(from_sec), float(to_sec)))
        except Exception as e:
            def close_dialog(e):
                dlg.open = False
                page.update()
            # now show a simple dialog box to show the user that the process has been stopped
            dlg = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"An error occured: {e}"),
                actions=[ft.ElevatedButton("OK", on_click=close_dialog)],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()
            with open("error.log", "a", encoding="utf-8") as file:
                error = traceback.format_exc()
                file.write(f"ERROR LOG {time.ctime()}\n\n{error}\n---------------------END OF ERROR---------------------\n\n")
            return
        # Once done show the dialog box saying that the scraping is done
        def close_dialog(e):
            dlg.open = False
            page.update()

        # now show a simple dialog box to show the user that the process is complete
        dlg = ft.AlertDialog(
            title=ft.Text("Process Completed"),
            content=ft.Text(
                "Process has been completed, please check the output file..."
            ),
            actions=[ft.ElevatedButton("OK", on_click=close_dialog)],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # create a thread instance here so it can be accessed globally (In this function)
    scraper_thread = threading.Thread(target=main_scraper, daemon=True)

    # create a function to start the scraper thread
    def start_scraper_thread(e):
        global to_process
        global running
        if running:
            return
        # Once a user hits the start button, we need to start the scraper thread, but if the thread has been run before it won't start
        # so we need to create a new thread instance
        scraper_thread = threading.Thread(target=main_scraper, daemon=True)
        scraper_thread.start()
        running = True


        def close_dialog(e):
            dlg.open = False
            page.update()
        
        # now show a simple dialog box to show the user that the process has been started
        dlg = ft.AlertDialog(
            title=ft.Text("Process Started"),
            content=ft.Text("Process has been started..."),
            actions=[ft.ElevatedButton("OK", on_click=close_dialog)],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()
        # join the scraper thread so
        scraper_thread.join()
        # set the to_process to True so that the scraper thread can be started again
        to_process = True
        running = False

    # create a function to stop the scraper thread
    def stop_scraper_thread(e):
        global to_process
        to_process = False

        # open up a dialog box to show that the process has been stopped
        def close_dialog(e):
            dlg.open = False
            page.update()

        # now show a simple dialog box to show the user that the process has been stopped
        dlg = ft.AlertDialog(
            title=ft.Text("Process Stopped"),
            content=ft.Text("Process has been stopped..."),
            actions=[ft.ElevatedButton("OK", on_click=close_dialog)],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    page.window.height = 530
    page.window.width = 870
    page.padding = 0
    page.window.max_height = 530
    page.window.max_width = 870
    page.title = "GulfTalent Crawler"
    page.window.maximizable = False
    page.window.resizable = False  # window is not resizable
    page.bgcolor = "#FFFFFF"
    page.fonts = {
        "RobotoMono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf",
    }
    # create inputfields here so that they can be stored in the settings.json file
    with open("settings.json", "r") as file:
        settings = json.load(file)
    url_field = ft.TextField(
        value=settings["main_url"],
        width=400,
        height=50,
        border_radius=5,
        bgcolor="#D9D9D9",
        color="#000000",
        border_color="white",
        on_change=lambda x: save_settings("main_url"),
        expand=True,
    )
    file_name_field = ft.TextField(
        value=settings["file_name"],
        width=400,
        height=50,
        border_radius=5,
        bgcolor="#D9D9D9",
        color="#000000",
        border_color="white",
        on_change=lambda x: save_settings("file_name"),
        expand=True,
    )
    max_delay_field = ft.TextField(
        value=settings["max_delay"],
        width=400,
        height=50,
        border_radius=5,
        bgcolor="#D9D9D9",
        color="#000000",
        border_color="white",
        on_change=lambda x: save_settings("max_delay"),
        expand=True,
    )
    max_jobs_field = ft.TextField(
        value=settings["max_jobs"],
        width=400,
        height=50,
        border_radius=5,
        bgcolor="#D9D9D9",
        color="#000000",
        border_color="white",
        on_change=lambda x: save_settings("max_jobs"),
        expand=True,
    )
    # create two cards, one that will store only the text part but other will have all inputs and buttons
    card_one = ft.Container(
        width=310,
        height=750,
        bgcolor="#5E95FF",
        content=ft.Column(
            tight=0,
            spacing=0,
            wrap=0,
            run_spacing=0,
            controls=[
                ft.Divider(color="#5E95FF", height=10, thickness=20),
                ft.Text(
                    size=30,
                    spans=[
                        ft.TextSpan("  "),
                        ft.TextSpan(
                            "GULF",
                            ft.TextStyle(
                                color="white",
                                font_family="RobotoMono",
                                decoration=ft.TextDecoration.UNDERLINE,
                                decoration_thickness=3,
                                decoration_color="white",
                                decoration_style=ft.TextDecorationStyle.DOUBLE,
                            ),
                        ),
                        ft.TextSpan(
                            "TALENT",
                            ft.TextStyle(color="white", font_family="RobotoMono"),
                        ),
                    ],
                ),
                ft.Text(
                    size=30,
                    spans=[
                        ft.TextSpan("  "),
                        ft.TextSpan(
                            "CR",
                            ft.TextStyle(
                                color="white",
                                font_family="RobotoMono",
                                decoration=ft.TextDecoration.UNDERLINE,
                                decoration_thickness=3,
                                decoration_color="white",
                                decoration_style=ft.TextDecorationStyle.DOUBLE,
                            ),
                        ),
                        ft.TextSpan(
                            "AWLER",
                            ft.TextStyle(color="white", font_family="RobotoMono"),
                        ),
                    ],
                ),
                ft.Text("\n\n\n\n\n"),
                ft.Row(
                    controls=[
                        ft.Text("   "),
                        ft.Text(
                            "Scrape all job\nlisting from\nGulftalent\nwithout any\nhassle of manual\nintervention...",
                            size=27,
                            color="#FFFFFF",
                            font_family="RobotoMono",
                            weight=ft.FontWeight.W_400,
                        ),
                    ]
                ),
            ],
        ),
    )
    card_two = ft.Container(
        height=750,
        width=530,
        bgcolor="#FFFFFF",
        content=ft.Column(
            tight=0,
            spacing=0,
            wrap=0,
            run_spacing=0,
            controls=[
                ft.Text("                       DashBoard", color="#000000", size=30),
                ft.Divider(color="#000000", height=20, thickness=3),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Text(
                            " Url: ", color="#000000", size=25, font_family="RobotoMono"
                        ),
                        url_field,
                    ],
                ),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Text(
                            " FileName: ",
                            color="#000000",
                            size=25,
                            font_family="RobotoMono",
                        ),
                        file_name_field,
                    ],
                ),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Text(
                            " Max-Delay: ",
                            color="#000000",
                            size=25,
                            font_family="RobotoMono",
                        ),
                        max_delay_field,
                    ],
                ),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Text(
                            " Max-Jobs: ",
                            color="#000000",
                            size=25,
                            font_family="RobotoMono",
                        ),
                        max_jobs_field,
                    ],
                ),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Divider(color="#FFFFFF", height=10, thickness=2),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Text("                         ", size=20),
                        ft.FilledButton(
                            content=ft.Text(
                                "Start",
                                color="#FFFFFF",
                                size=20,
                                font_family="RobotoMono",
                            ),
                            style=ft.ButtonStyle(bgcolor="#5E95FF"),
                            on_click=start_scraper_thread,
                        ),
                        ft.Text("          ", size=20),
                        ft.FilledButton(
                            content=ft.Text(
                                "Stop",
                                color="#FFFFFF",
                                size=20,
                                font_family="RobotoMono",
                            ),
                            style=ft.ButtonStyle(bgcolor="#5E95FF"),
                            on_click=stop_scraper_thread,
                        ),
                    ],
                ),
            ],
        ),
    )
    page.add(ft.Row(spacing=0, controls=[card_one, card_two]))
    page.update()


if __name__ == "__main__":
    # Initiate the app and pass GUI function to render
    check_settings()
    ft.app(target=user_interface)