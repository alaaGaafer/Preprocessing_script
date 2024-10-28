# RetTuning(AutoML Project)
## Description
The AutoML Project is designed to streamline the process of building and deploying machine learning models for small-scale businesses and data scientists. It offers a complete solution that covers the entire machine learning workflow, from data preparation to model deployment.

## Key Features:
  1-  Data Preprocessing: The project automates data cleaning and preparation tasks, including handling missing values, detecting outliers, and normalizing features. This ensures that data is ready for analysis         with minimal manual effort.

  2-  Feature Engineering: Advanced techniques are employed to extract and select important features, which enhances the performance of the machine learning models.

  3-  Model Training: The backend uses a structured pipeline to select and train machine learning models. It utilizes meta-learning to choose the most appropriate models and optimize their configurations based on       the data.

  4-  Hyperparameter Tuning: The system applies the SMAC (Sequential Model-Based Algorithm Configuration) method to fine-tune hyperparameters, improving model accuracy and performance.

  5-  Model Evaluation and Prediction: Users can assess model performance and make predictions on new datasets.

  6-  Frontend Interface: Built with React, the frontend provides a user-friendly interface for data upload, project management, model evaluation, and predictions.

  7-  Project Management: Users can create and re-use projects, keeping track of different models and their performance metrics for ongoing improvements.

  8-  Integration and API: The frontend and backend communicate through an API, ensuring smooth data exchange and interaction between the user interface and the machine learning engine.


## Running the Project

To set up and run the project, follow these steps:

### 1. Backend Setup

1. **Navigate to the Backend Directory**:
   ```bash
   cd Auto_ML_Project/backend/autoAnalysisServer
   ```

2. **Install Backend Dependencies**:
   Ensure that you have a `requirements.txt` file in the parent directory with the necessary Python packages listed.
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Run the Backend Server**:
   ```bash
   python manage.py runserver
   ```

### 2. Frontend Setup

1. **Navigate to the Frontend Directory**:
   ```bash
   cd Auto_ML_Project/front-end
   ```

2. **Install Frontend Dependencies**:
   Ensure you have `package.json` in this directory with the required Node.js packages.
   ```bash
   npm install
   ```

3. **Start the Frontend Application**:
   ```bash
   npm start
   ```
