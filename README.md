Mini Project Details:
- An HTTP REST API.
- Connecting to https://www.coingecko.com/
- Login Screen, with proper Dashboard. (Used HTML)
- Applicate should have a proper Auth Method (Currently using JWT Auth Method).
- Tokens should be correctly fetched, without tokens system should not fetch coins.
- Fetching All the Coin Deatils.
- Records should be displayed in page_num query parameters.
- Default pagination is 10 items per call, can be modified on-the-fly.
- Default pagination can be overridden by query parameter per_page.
- Coins value should be displayed in Default Dollars.
- A Docker File should be created to execute the project in Docker Desktop Cointainer.
- Unit Test Documnet Should be created. 

Applications Used:
- Visual Studio Code
- Docker Desktop
- Command Prompt
- Python Insalled (Python 3.13.3)
- PIP Services (requirements.txt)


Steps for Execution:
1. All Programs should be correctly Structure in desired Folders & Templates.
2. Open Docker Desktop
3. In CMD, cmd: docker compose up --build (Command will help to build Coinatiner & Image in Docker Desktop) 
4. Docker will also provide the hosts, you can directly click on the hosts to go to the login portal.


Webpage
1. Login Screen (HTML) - Temaplates Files in /templates folder

User needs to enter UserName & Password
System will Vaildate based on JWT Method Auth
Output:
- Enter UserName & Password
- JWT-based Auth
- All Coins List
- Paginated responses


