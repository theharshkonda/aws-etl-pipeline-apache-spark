  # 🚀 Serverless ETL Pipeline Using AWS Glue, S3, and Athena! 🛠️

This project demonstrates how to build a **scalable ETL (Extract, Transform, Load)** pipeline using **AWS Glue**, **S3**, **Glue Data Catalog**, and **Amazon Athena**. The pipeline ingests raw data from S3, transforms it via a Glue job, and outputs it in optimized **Parquet format** for fast querying.

---
# 📦 Use Case
For this Pipeline, let's assume you have a vendor who provides incremental sales data at the end of every month. The file arrives in Amazon S3 as a CSV file, and it needs to be processed and made available to your data analysts for querying and analysis.

# 🏗️ Architecture
To implement this data pipeline, we will use AWS Glue — a fully managed serverless ETL service — as the data processing engine, and Amazon S3 for storage.

<img width="3750" height="3750" alt="( RAW DATA ) (1)" src="https://github.com/user-attachments/assets/dae8f7b0-b3e9-4e11-a0c5-2a8ec914f9e6" />

We'll use:

RAW data: Input and unprocessed CSV files stored in S3 (e.g., s3://my-etl-bucket/raw_data/)

CLEANSED data: Transformed and processed data stored back into S3 in Parquet format (e.g., s3://my-etl-bucket/cleaned_data/)

We will build a pipeline that:

Receives a new sales file in S3.

Catalogs the schema using an AWS Glue Crawler.

Processes the data using an AWS Glue ETL Job (PySpark) with the necessary transformations.

Saves the cleaned and transformed data into a target S3 bucket.

Makes the output data queryable using Amazon Athena via SQL.

## 📌 Table of Contents

- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)
- [Tools & Technologies](#tools--technologies)
- [Pre-requisites](#pre-requisites)
- [Step-by-Step Setup](#step-by-step-setup)
  - [1. Upload Raw Data to S3](#1-upload-raw-data-to-s3)
  - [2. Configure and Run Glue Crawler (Raw Data)](#2-configure-and-run-glue-crawler-raw-data)
  - [3. Create and Run AWS Glue ETL Job](#3-create-and-run-aws-glue-etl-job)
  - [4. IAM Role Fix: Add S3 Write Permissions](#4-iam-role-fix-add-s3-write-permissions)
  - [5. Run Crawler for Cleaned Data](#5-run-crawler-for-cleaned-data)
  - [6. Query Cleaned Data in Athena](#6-query-cleaned-data-in-athena)
- [Re-running the Pipeline](#re-running-the-pipeline)
- [Next Steps](#next-steps)

---

## 📖 Overview

The ETL process includes:

- **Extracting** raw CSV or JSON data from an Amazon S3 bucket
- **Transforming** it using an AWS Glue job (DynamicFrames)
- **Loading** the processed output in S3 in optimized **Parquet format**
- **Querying** the cleaned data using Amazon Athena for analysis

---

## 🧱 Tool	Purpose
AWS S3	Storage for raw and cleaned datasets
AWS Glue	Serverless ETL engine
Glue Crawlers	Automatically infer schema & update Catalog
Glue Jobs	Python/aws-based transformation jobs
Glue Data Catalog	Metadata store for Athena/Redshift
Amazon Athena	SQL-based query engine for S3
IAM Roles	Secure access control

✅ Pre-requisites
Before you begin:

S3 Bucket: Create a bucket (e.g., my-etl-bucket) with two folders:

raw_data/

cleaned_data/

<img width="1709" height="758" alt="Screenshot 2025-07-14 231214" src="https://github.com/user-attachments/assets/64f9dabe-abed-4694-b3b1-99561bb39f06" />

IAM Role: Ensure an IAM role exists with at least the following permissions:

AWSGlueServiceRole managed policy

S3 read/write permissions for your bucket

Enable AWS Glue and Athena in the region you're working in.



## 🧾 Step-by-Step Setup

### 1. Upload Raw Data to S3

Upload a sample CSV (or JSON) to the S3 raw_data/ folder:

```
s3://my-etl-aws-bucket/raw_data/data.csv
```

You can use the AWS Console **or** CLI command:

```bash
aws s3 cp data.csv s3://my-etl-aws-bucket/raw_data/
```

---

<img width="1689" height="780" alt="Screenshot 2025-07-14 231257" src="https://github.com/user-attachments/assets/c60323a6-6e42-4e6f-a6c6-70cd5b5b9618" />


### 2. Configure and Run Glue Crawler (Raw Data)

1. Navigate to **AWS Glue > Crawlers**
2. Click **Create Crawler**
3. Configuration:
   - **Name**: `raw-data-crawler`
   - **Source Type**: S3
   - **Path**: `s3://my-etl-aws-bucket/raw_data/`
   - **IAM Role**: `AWSGlueServiceRole-GlueCrawlerRole`
   - **Target Database**: `my_etl_db`
4. Click **Run Crawler**

✅ **Result**: A table called `raw_data` will appear under the `my_etl_db` Glue database.

---

<img width="1915" height="864" alt="Screenshot 2025-07-14 232224" src="https://github.com/user-attachments/assets/f8fdf2df-3aca-46f0-b344-881b21222cf5" />


### 3. Create and Run AWS Glue ETL Job

#### Script: `glue_etl_job.py`

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyaws.context import awsContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = awsContext()
glueContext = GlueContext(sc)
aws = glueContext.aws_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

datasource = glueContext.create_dynamic_frame.from_catalog(
    database = "my_etl_db",
    table_name = "raw_data"
)

transformed_data = datasource.drop_fields(['unnecessary_column'])

glueContext.write_dynamic_frame.from_options(
    frame = transformed_data,
    connection_type = "s3",
    connection_options = {"path": "s3://my-etl-aws-bucket/cleaned_data"},
    format = "parquet"
)

job.commit()
```
<img width="1917" height="799" alt="Screenshot 2025-07-14 233942" src="https://github.com/user-attachments/assets/47605ced-f2fa-49b2-8689-6359645baedd" />

#### To Run:

- Go to **AWS Glue > Jobs**
- Click **Create Job**
- Use **script editor** and paste above
- Choose your existing **IAM Role**
- Click **Run Job**

<img width="1909" height="873" alt="Screenshot 2025-07-15 002130" src="https://github.com/user-attachments/assets/9c5a7652-5e30-44a3-968c-30460d54d013" />

✅ Output written to:

```
s3://my-etl-aws-bucket/cleaned_data/
```

---

<img width="1914" height="726" alt="Screenshot 2025-07-15 002153" src="https://github.com/user-attachments/assets/34bff6af-511a-4dd5-80ad-07e31962f5b5" />


### 4. IAM Role Fix: Add S3 Write Permissions

If your job fails with a `PERMISSION_ERROR`, follow these steps:

1. Go to **IAM > Roles > AWSGlueServiceRole-GlueCrawlerRole**
2. Add this **inline policy**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-etl-aws-bucket/cleaned_data/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::my-etl-aws-bucket"
    }
  ]
}
```

✅ Replace `my-etl-aws-bucket` with your actual bucket name.

---

### 5. Run Crawler for Cleaned Data

1. Go to **Glue > Crawlers**
2. Click **Create Crawler**
3. Configuration:
   - **Name**: `cleaned-data-crawler`
   - **Source**: `s3://my-etl-aws-bucket/cleaned_data/`
   - **Target Database**: `my_etl_db`
4. Click **Run Crawler**

✅ A new table `cleaned_data` will be created.

---

<img width="1865" height="882" alt="Screenshot 2025-07-14 234429" src="https://github.com/user-attachments/assets/fc2912f6-c597-4a0a-8fc9-89a6d687bd9a" />


### 6. Query Cleaned Data in Athena

1. Go to **Amazon Athena > Query Editor**
2. Choose:
   - **Data Source**: `AwsDataCatalog`
   - **Database**: `my_etl_db`
3. Run Query:

```sql
SELECT * FROM cleaned_data LIMIT 10;
```
<img width="1919" height="886" alt="Screenshot 2025-07-15 002454" src="https://github.com/user-attachments/assets/cf25bdc9-653c-491a-9f49-ac1b723dea40" />

<img width="1919" height="899" alt="Screenshot 2025-07-15 002632" src="https://github.com/user-attachments/assets/6d60b10a-9cb7-4d84-a497-2e1868f3efc3" />


✅ You should see the transformed data loaded via the Glue ETL job.

---

## 🔁 Re-running the Pipeline

| Task                     | When to Run Again                      |
|--------------------------|----------------------------------------|
| Upload new raw data      | Whenever new data arrives              |
| Run raw-data-crawler     | After uploading new files              |
| Run Glue ETL Job         | To re-transform newly added raw data   |
| Run cleaned-data-crawler | To update the `cleaned_data` table     |
| Query in Athena          | After running all the above steps      |

---

## 📬 Support

If anything goes wrong (e.g. permission errors, table not found), check:

- **AWS Glue Logs** → In **CloudWatch**
- **IAM Role permissions** → For Glue, S3, Athena
- **Athena Workgroup settings** → For output location

---

## 🏁 License

This project is licensed under the **MIT License**.
