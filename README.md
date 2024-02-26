# Game Deals
This is a project to look-up and synthesize data for PC game deals using Cheapshark (https://apidocs.cheapshark.com/).

**Link to project:** https://dealquest-b4db9479ca71.herokuapp.com/

## How It's Made:

**Tech used:** Flask, Python, HTML/CSS, JavaScript, Prometheus, Git/GitHub

Embark on a legendary quest with DealQuest, where the magic of Python and Flask combines to forge an extraordinary adventure! With Flask as your trusty steed, traversing the vast landscape of the web is a breeze, while Python, the wizard of the digital realm, weaves spells of functionality and logic. As you venture forth, HTML and CSS adorn your path with captivating visuals, while JavaScript breathes life into the journey, adding interactive elements to your quest. And fear not, for Prometheus, the guardian of metrics, stands watch, ensuring the stability and performance of our noble expedition. So, brave adventurer, heed the call of DealQuest, where every click brings you closer to uncovering legendary PC game deals waiting to be discovered!

## Installation:
To get started with DealQuest, follow these steps:
1. Clone the repository to your local machine:
```bash
   git clone https://github.com/jdavery/DealQuest.git
```
2. Navigate to the project directory.
```bash
   cd DealQuest
```
3. Install the required dependencies using pip:
```bash
   pip install -r requirements.txt
```
## Usage
Once you've installed the dependencies, you can run the DealQuest application:
1. Set the environment variable to point to the Flask app. Make sure you navigated to /src. :
```bash
  set FLASK_APP=src/app/__init__.py
```
2. Navigate to the src directory and run the Flask app:
```bash
  flask run
```
3. Access the application in your web browser at http://localhost:5000

## Features:
* **Game Deals**: Browse and discover the latest deals on PC games from various online stores.
* **Search Functionality**: Easily search for specific games or review values to find the best deals.
* **Deal Analysis**: Review some basic statistical analysis on the deals currently available.

## Endpoints:
* **/health**: Returns a 200 OK status to indicate that the application is running.
* **/metrics**: Returns JSON data with application metrics and a 200 OK status.

## Testing:
To run unit and integration tests:
```bash
   pytest src/tests/
```