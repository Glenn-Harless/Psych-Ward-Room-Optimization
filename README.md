
# Inpatient Psych Ward Space Optimization

## Project Overview

This project aims to model the most efficient use of space for an inpatient psych ward certified to hold up to 26 patients. The objective is to find an optimal combination of double and single rooms to minimize wasted space and ensure efficient utilization of beds. The comparison is made between the current bed allocation method and a new approach derived from a linear programming optimization.

## Methodology

The project is divided into several key components:

### Data Preprocessing

1. **preprocess_data.py**: This script processes raw data from Excel files, cleans it, and prepares it for analysis. The script extracts information about daily room usage, including the number of single-room patients, double-room patients, and closed rooms, and generates a final CSV file containing this data with accurate dates.

### Model Evaluation

1. **model_current.py**: 
    - Evaluates the current bed allocation model, where all rooms are double rooms. 
    - It calculates the number of wasted beds daily and cumulatively by considering patients who require isolation, thus wasting the second bed in a double room.

2. **model_optimizer.py**:
    - Evaluates the optimized bed allocation model derived from linear programming.
    - In this model, the ward has a combination of 10 double rooms and 6 single rooms, minimizing wasted beds by only placing isolated patients in double rooms when all single rooms are occupied.

### Visualization

1. **visualizer.py**: 
    - Generates visualizations comparing the efficiency of the current and optimized models. 
    - Key metrics such as daily wasted beds, cumulative efficiency, and daily efficiency are plotted to provide insights into how each model performs over time.

### Optimization Approach

- **Decision Variables:** 
  - Number of double rooms (D).
  - Number of single rooms (S).
- **Constraints:** 
  - Total number of beds (2D + S) must equal 26.
  - Ensure enough rooms for patients requiring single rooms.
  - Allow double room patients to occupy either single or double rooms.
- **Objective Function:** 
  - Minimize the total number of wasted beds.

A high-level overview of the approach includes:
1. **Defining the Objective Function:** The objective is to minimize the total number of wasted beds.
2. **Setting Decision Variables:** The number of double rooms (D) and single rooms (S).
3. **Establishing Constraints:** Ensuring the total number of beds is 26, and there are enough rooms for patients requiring single rooms while allowing double room patients to occupy any room type.
4. **Solving the Linear Program:** Using linear programming techniques to find the optimal values for D and S that minimize the objective function.
5. **Interpreting Results:** Extracting and analyzing the optimal room configuration and the associated number of wasted beds.

## Results

For a detailed discussion of the results, please refer to the `optimizer_results.md` file, which provides an in-depth analysis of the linear programming optimization and a comparison of the current and optimized models.

## Usage

### Prerequisites

Ensure you have the necessary dependencies installed. You can install them using the `requirements.txt` file:

```
pip install -r requirements.txt
```

### Running the Scripts

#### Data Preprocessing

Before running the models, ensure that your data is preprocessed using:

```
python preprocess_data.py
```

This will generate the `final_census_data.csv` file required by the model scripts.

#### Running the Current Model Evaluation

The `model_current.py` script evaluates the current bed allocation model:

```
python model_current.py
```

This will output a CSV file containing the evaluation results for the current model.

#### Running the Optimized Model Evaluation

The `model_optimizer.py` script evaluates the optimized bed allocation model:

```
python model_optimizer.py
```

This will output a CSV file containing the evaluation results for the optimized model.

#### Running the Visualization Script

The `visualizer.py` script generates visualizations to compare the current and optimized models:

```
python visualizer.py
```

This will output various visualizations as PNG files, comparing the two models.

### Running with Docker

You can also run the project using Docker. Ensure Docker is installed and running on your system.

#### Building the Docker Image

Build the Docker image using the provided `Dockerfile`:

```
docker-compose build   
```

Start the application using:

```
docker-compose up   
```

## Additional Information

For more details on how the linear programming was implemented and the specific results of the optimization, please refer to the `optimizer_results.md` file.
