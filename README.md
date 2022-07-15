#  Search Engine Example with Django

This repository provides an example of how to interface with a csv data file using the [Python Django Framework](https://www.djangoproject.com/).

### Requirements
* Python 3
* Django, `python3 -m pip install Django`, [more info](https://docs.djangoproject.com/en/4.0/intro/install/)
* Pandas, `pip3 install pandas`, [more info](https://pandas.pydata.org/docs/index.html)

### How to run the example

* Clone this directory on your local machine
	* `git clone https://github.com/becot85/django_example.git`
* Go to the example directory
	* `cd django_example/codingproblem`
* Launch the Django server using the following command
	* `python3 manage.py runserver`
* Open a web browser and go to the following address
	* [http://127.0.0.1:8000/csvfile/search_file/](http://127.0.0.1:8000/csvfile/search_file/)
* Type `data.csv` in the upper text box and click on the `Read file` button to load data.

* Search the content of the csv file using the different text boxes.

* **Note:** The csv file is located in the `codingproblem/` folder.
