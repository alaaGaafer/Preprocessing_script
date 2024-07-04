from similaritySearch.functions import *
from bestmodel import *
from cashAlgorithm.smacClass import ProblemType
import pandas as pd


def calculate_date_frequency(series):
    """
    Calculate the most common frequency (interval) of a datetime series.

    Parameters:
    series (pd.Series): A pandas Series of datetime objects.

    Returns:
    str: A string representing the most common frequency (e.g., 'D' for days, 'H' for hours).
    """
    # Drop NaN values to avoid errors in calculations
    series = series.dropna()

    # Calculate the differences between consecutive dates
    diffs = series.diff().dropna()

    # Calculate the most common frequency
    freq = diffs.mode()[0]

    # Convert the frequency to a string representation
    series = series.dropna()

    # Calculate the differences between consecutive dates
    diffs = series.diff().dropna()

    # Calculate the most common frequency
    freq = diffs.mode()[0]

    # Convert the frequency to a string representation
    if freq == pd.Timedelta(days=1):
        return 'D'  # Daily
    elif freq >= pd.Timedelta(days=7):
        return 'W'  # Weekly
    elif freq >= pd.Timedelta(days=30):
        return 'M'  # Monthly
    elif freq >= pd.Timedelta(days=90):
        return 'Q'  # Quartely
    elif freq >= pd.Timedelta(days=365):
        return 'A'  # Annually
    else:
        return freq  # Return the exact frequency if it's not a common one


def Detections_(df, y_column, problem, date_col=None):
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])

    if problem == "timeseries":
        df.rename(columns={date_col: 'ds', y_column: 'y'}, inplace=True)
        y_column = 'y'
        df['y'] = df['y'].str.replace('[^0-9\.]', '', regex=True)
        df['y'] = pd.to_numeric(df['y'], errors='coerce')
        df['y'] = df['y'].astype(float)

    df = RemoveIDColumn.remove_high_cardinality_columns(df)
    df = MissingValues().del_high_null_cols(df)
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

    nulls_columns = MissingValues().detect_nulls(df)
    cols_with_outliers = Outliers().detect_outliers(df)
    df = Duplicates().handle_dub(df)
    imbalance_detected = None
    if problem == "classification":
        imbalance_detected = HandlingImbalanceClasses().detect_class_imbalance(df, y_column)
    df_without_y = df.drop(columns=[y_column])
    low_variance_columns, low_variance_info = HandlingColinearity().detect_low_variance(df_without_y)

    return df, nulls_columns, cols_with_outliers, imbalance_detected, low_variance_columns, categorical_columns


def _process_data(df: pd.DataFrame, fill_na_dict: dict, outliers_methods_input: tuple,
                  Norm_method: str) -> pd.DataFrame:
    """Handle missing values, outliers, normalization, and encoding."""
    df = MissingValues().handle_nan(df, fill_na_dict)
    cols_with_outliers = Outliers().detect_outliers(df)
    df = Outliers().handle_outliers(df, cols_with_outliers, outliers_methods_input)
    df = DataNormalization().normalize_data(df, Norm_method)

    return df


def Cleaning(df, problem, y_column, fill_na_dict, outliers_methods_input, imb_instruction, Norm_method,
             lowvariance_actions, encoding_dict, date_col=None):
    if problem == "timeseries":
        date_col = 'ds'
        y_column = 'y'
        frequency = calculate_date_frequency(df[date_col])
        df.set_index('ds', inplace=True)
        train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)
    elif problem == "classification":
        train_data, test_data = train_test_split(df, test_size=0.2, random_state=42, stratify=df[y_column])
        train_data = train_data.reset_index(drop=True)
        test_data = test_data.reset_index(drop=True)
    else:
        df['timestamp'] = df[date_col].astype('int64') / 10 ** 9  # Convert to UNIX timestamp in seconds
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['day'] = df[date_col].dt.day
        df.drop(date_col, axis=1, inplace=True)
        train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)
        train_data = train_data.reset_index(drop=True)
        test_data = test_data.reset_index(drop=True)

    train_data = _process_data(train_data, fill_na_dict, outliers_methods_input, Norm_method)
    test_data = _process_data(test_data, fill_na_dict, outliers_methods_input, Norm_method)

    df_copy = pd.concat([train_data, test_data])
    df_copy = df_copy.sort_index()
    original_columns = set(df.columns)

    # Remove co-linearity & low_variance
    historical_df_without_y = df_copy.drop(columns=[y_column])
    historical_df_without_y = HandlingColinearity().handle_low_variance(historical_df_without_y, lowvariance_actions)
    historical_df_without_y = HandlingColinearity().handling_colinearity(historical_df_without_y)
    historical_df_without_y[y_column] = df_copy[y_column]

    # Update historical_df_copy with processed columns
    df_copy = historical_df_without_y.copy()

    # Identify removed columns
    processed_columns = set(df_copy.columns)
    removed_columns = list(original_columns - processed_columns)

    # Remove identified columns from train_data and test_data
    train_data = train_data.drop(columns=removed_columns)
    test_data = test_data.drop(columns=removed_columns)
    # if problem != "timeseries":
    # not needed now
    # meta_extractor, meta_features, best_models = extract_and_search_features(df_copy)

    train_data = EncodeCategorical().Encode(train_data, encoding_dict)
    test_data = EncodeCategorical().Encode(test_data, encoding_dict)

    if imb_instruction:
        train_data = HandlingImbalanceClasses().handle_class_imbalance(train_data, y_column, imb_instruction)
        test_data = HandlingImbalanceClasses().handle_class_imbalance(test_data, y_column, imb_instruction)

    df_copy = pd.concat([train_data, test_data])
    df_copy = df_copy.sort_index()

    if problem != "timeseries":
        x_train = train_data.drop(columns=[y_column])
        y_train = train_data[y_column]

        # Split test_data into features and labels
        x_test = test_data.drop(columns=[y_column])
        y_test = test_data[y_column]

        return x_train, y_train, x_test, y_test,
    else:
        return train_data, test_data, frequency


def user_interaction(df, problem, y_column, date_col=None):
    try:
        df, nulls_columns, cols_with_outliers, imbalance, low_variance_columns, categorical_columns = Detections_(df,
                                                                                                                  y_column,
                                                                                                                  problem,
                                                                                                                  date_col)

        # Handling missing values
        fill_na_dict = {}
        if nulls_columns:
            fill_na_dict = {col: 'auto' for col in nulls_columns}

        # Handling outliers
        outliers_method_input = ('z_score', 'auto', 3)
        imb_instruction = "auto" if imbalance else None
        Norm_method = "auto"
        low_actions = {}
        encoding_dict = {}
        if categorical_columns:
            encoding_dict = {col: 'auto' for col in categorical_columns}
        if low_variance_columns:
            low_actions = {col: 'auto' for col in low_variance_columns}

        if problem != "timeseries":
            x_train, y_train, x_test, y_test = Cleaning(df, problem, y_column, fill_na_dict, outliers_method_input,
                                                        imb_instruction, Norm_method, low_actions, encoding_dict,
                                                        date_col)
            return x_train, y_train, x_test, y_test

        else:
            train_data, test_data, frequency = Cleaning(df, problem, y_column, fill_na_dict, outliers_method_input,
                                                        imb_instruction, Norm_method, low_actions, encoding_dict,
                                                        date_col)
            return train_data, test_data, frequency

    except ValueError as ve:
        print(f"Error occurred: {ve}")
        return None


if __name__ == "__main__":
    df1 =pd.read_csv(r"daily-minimum-temperatures-in-me.csv")
    problemtype1 = "timeseries"
    train_data, test_data,frequency = user_interaction(df1, problemtype1, "Daily minimum temperatures", date_col="Date")
    choosenModels=["Arima",'Sarima']
    traindatax='lol'
    test_datax='loll'
    Bestmodelobj = Bestmodel(ProblemType.TIME_SERIES,choosenModels,traindatax,traindatax,train_data,test_data,frequency)
    Bestmodelobj.splitTestData()
    # Bestmodelobj.Getincumbent()
    Bestmodelobj.TrainModel()

    df2 = pd.read_csv(r"train.csv")
    problemtype2 = "classification"
    choosenModels = ["KNN", "LR", "RF"]
    x_train, y_train, x_test, y_test = user_interaction(df2, problemtype2, "Survived", date_col=None)
    Bestmodelobj = Bestmodel(ProblemType.CLASSIFICATION, choosenModels, x_train,x_test,y_train,y_test)
    Bestmodelobj.splitTestData()
    # Bestmodelobj.Getincumbent()
    Bestmodelobj.TrainModel()

    df3 = pd.read_csv(r"pulsedata.csv")
    problemtype3 = "regression"
    x_train, y_train, x_test, y_test = user_interaction(df3, problemtype3, "Calories", date_col="Date")
    choosenModels = ['LinearRegression', "Lasso"]
    Bestmodelobj = Bestmodel(ProblemType.REGRESSION, choosenModels, x_train, x_test, y_train, y_test)
    Bestmodelobj.splitTestData()
    # Bestmodelobj.Getincumbent()
    Bestmodelobj.TrainModel()
