import pandas as pd
import numpy as np

bank_marketing_data = "bank_marketing.csv"

# columns for each DataFrame:
client_cols = ['client_id', 'age', 'job', 'marital', 'education', 'credit_default', 'housing', 'loan']
campaign_cols = ['client_id', 'campaign', 'month', 'day', 'duration', 'pdays', 'previous', 'poutcome', 'y']
economics_cols = ['client_id', 'emp_var_rate', 'cons_price_idx', 'euribor3m', 'nr_employed']

# split DataFrames:
client = pd.read_csv(bank_marketing_data, usecols=client_cols)
campaign = pd.read_csv(bank_marketing_data, usecols=campaign_cols)
economics = pd.read_csv(bank_marketing_data, usecols=economics_cols)

# rename certain columns:
renamed_client_cols = {'client_id': 'id'}
client.rename(columns=renamed_client_cols, inplace=True)
renamed_campaign_cols = {'campaign': 'number_contacts', 'duration': 'contact_duration', 'previous': 'previous_campaign_contacts', 'poutcome': 'previous_outcome', 'y': 'campaign_outcome'}
campaign.rename(columns=renamed_campaign_cols, inplace=True)
renamed_economics_cols = {'euribor3m': 'euribor_three_months', 'nr_employed': 'number_employed'}
economics.rename(columns=renamed_economics_cols, inplace=True)

# clean "education" and "job" columns in client DataFrame:
client["education"] = client["education"].str.replace(".", "_")
client["education"] = client["education"].replace("unknown", np.NaN)
client["job"] = client["job"].str.strip(".")

# convert selected strings to binary and NumPy null values:
campaign["campaign_outcome"] = campaign["campaign_outcome"].map({"yes": 1, "no": 0})
campaign["previous_outcome"] = campaign["previous_outcome"].map({"success": 1, "failure": 0})
campaign["previous_outcome"] = campaign["previous_outcome"].replace("nonexistent", np.NaN)

# add "campaign_id" column to campaign DataFrame:
campaign["campaign_id"] = 1

# create a datetime column:
campaign["year"] = "2022"
campaign["month"] = campaign["month"].str.capitalize()
campaign["day"] = campaign["day"].astype(str)
campaign["last_contact_date"] = campaign["year"] + "-" + campaign["month"] + "-" + campaign["day"]
campaign["last_contact_date"] = pd.to_datetime(campaign["last_contact_date"], format="%Y-%b-%d")

# remove redundant data:
redundant_data = ["month", "day", "year"]
campaign.drop(columns=redundant_data, inplace=True)

# save created DataFrames:
client.to_csv("client.csv", index=False)
campaign.to_csv("campaign.csv", index=False)
economics.to_csv("economics.csv", index=False)

# create client_table w/ SQL code:
client_table = """
CREATE TABLE client
(
    id SERIAL PRIMARY KEY,
    age INTEGER,
    job TEXT,
    marital TEXT,
    education TEXT,
    credit_default BOOLEAN,
    housing BOOLEAN,
    loan BOOLEAN
);
\copy client from 'client.csv' DELIMITER ',' CSV HEADER
"""

# create campaign_table w/ SQL code:
campaign_table = """
CREATE TABLE campaign
(
    campaign_id SERIAL PRIMARY KEY,
    client_id SERIAL REFERENCES client (id),
    number_contacts INTEGER,
    contact_duration INTEGER,
    pdays INTEGER,
    previous_campaign_contacts INTEGER,
    previous_outcome BOOLEAN,
    campaign_outcome BOOLEAN,
    last_contact_date DATE
);
\copy campaign from 'campaign.csv' DELIMITER ',' CSV HEADER
"""

# create economics_table w/ SQL code:
economics_table = """
CREATE TABLE economics
(
    client_id SERIAL REFERENCES client (id),
    emp_var_rate FLOAT,
    cons_price_idx FLOAT,
    euribor_three_months FLOAT,
    number_employed FLOAT
);
\copy economics from 'economics.csv' DELIMITER ',' CSV HEADER
"""
