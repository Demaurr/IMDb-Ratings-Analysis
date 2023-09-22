# IMDb Rating Analysis

![Project Screenshot](Screeshots/Result.PNG) 
## Table of Contents 
 - [Introduction](#introduction) 
 - [Installation](#installation) 
 -  [Usage](#usage) 
 -  [Features](#features) 
 -  [Contributing](#contributing) 
 -  [License](#license) 
 -  [Acknowledgments](#acknowledgments)


## Introduction 
This Django project allows you to analyze and explore your movie data from [IMDb](https://www.imdb.com/list/ratings/?ref_=helpms_ih_tm_history).

## Installation  
1.  **Clone the repository to your local machine:**  
	```shell
	 git clone https://github.com/Brightlat/IMDb-Ratings-Analysis.git
2.  **Install Required Libraries**
	```shell
	pip install -r requirements.txt
3. **Start the development server:**
	```shell
	python manage.py runserver
## Usage

1.  **Use the provided HTML templates for the following views:**
    
    -   `search_result.html`: Display search results.
    -   `upload.html`: Upload CSV files.
    -   `result.html`: Display analysis results.
2.  **Customize the `views.py` and `movie_analysis.py` files** to implement your specific movie analysis logic.

## Features

-   Upload `ratings.csv` file with movie data from [IMDb](https://www.imdb.com/list/ratings/?ref_=helpms_ih_tm_history).
-   You Can Search for movies by year watched, genre watched, and other criteria.
-   Generate statistics and visualizations(Only while Running Through Commandline see [Documentation](Documentation.md) for more) based on movie data.

## Working Screenshots
![Upload](Screeshots/Upload.PNG) 
![Search](Screeshots/Searched_Result.PNG)

## Author
[Brightlat](https://github.com/Brightlat)
## Contributing

Contributions are welcome! If you have any improvements or new features to add, please follow these steps:

1.  **Fork the repository.**
2.  **Create a new branch for your feature:** `git checkout -b feature-name`
3.  **Make your changes and commit them:** `git commit -m 'Add new feature'`
4.  **Push to your branch:** `git push origin feature-name`
5.  **Create a pull request.**

## License

This project is licensed under the MIT License - see the [LICENSE](#License) file for details.
