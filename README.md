# Bayesian Bowl 

## Setup 
1. Download [conda](https://www.anaconda.com/download/)/[miniconda](https://docs.conda.io/projects/miniconda/en/latest/) 
2. Have git setup on your computer. You should be able to download it [here](https://git-scm.com/downloads)
3. Clone the repo
```
git clone https://github.com/KuleenS/BayesianBowl.git
```
4. Download environment packages to create environment called bayes
```
conda env create -f environment.yml
```
5. Set up a jupyter server either using jupyter notebook or VSCode Jupyter Notebook
6. Run the code in the folders


## Explanation of code files

### src/data/data_scraping/scraper.py
Initial file to scrape all the data from the website

### src/data/data_cleaning/data_aggregation.ipynb
Aggregates raw data into csv

Warning: this has manual step. If you do not want to manually align like 10 tournaments. Please just move use the dataset.csv and cleaned_filtered_dataset_nans.csv

### src/data/data_cleaning/clean.ipynb
Cleans dataset and standardizes some of the inconsistencies

### src/data_visualization/data_visualization.ipynb
Exploratory data analysis

### src/model/run_model.ipynb
Running the models and outputting their predictions.

Warning might require a GPU. Would recommend you run these on Google Colab

## Explanation of data files

## data/filter
List of teams that are excluded from our analysis

## data/dataset.csv
Aggregated raw data into csv format

## data/cleaned_filtered_dataset_nans.csv
Final version of data

## data/graph.csv
CSV data to input into [cosmograph](https://cosmograph.app/) to visualize graph

# Report and Slides 

Bayesian_Bradley_Terry - slides explaining project at a high level
Bayesian_Report.pdf - full in depth technical report explaining process and project

