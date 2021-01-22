# Description

I wrote this code to automatically generate Trello cards containing the information in a Google Sheets schedule (which I first exported to CSV) for one of my Computer Science classes. This is a quick and dirty implementation.

# Setup/Prerequisites
- Python 3.7+
- Obtain a Trello API [Key](https://trello.com/app-key) and API Token
- Clone the repo
    - After cloning the repo and `cd`'ing into it, you have two options:
        1. If you've installed [`pipenv`](https://docs.python-guide.org/dev/virtualenvs/), you should be able to simply run `pipenv install`.
        2. Create a virtual environment, then use `pip` to install the dependencies from the `requirements.txt` file by running `pip install -r requirements.txt`.

# Running the Code
After modifying the code to your liking, you should be able to simply run `python3 process_schedule.py`.