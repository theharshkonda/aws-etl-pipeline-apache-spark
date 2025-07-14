# 🚀 End-to-End ETL Pipeline with Spark, AWS Glue, S3, and Athena 

This project demonstrates how to build a **scalable ETL (Extract, Transform, Load)** pipeline using **AWS Glue**, **S3**, **Glue Data Catalog**, and **Amazon Athena**. The pipeline ingests raw data from S3, transforms it via a Glue job, and outputs it in optimized **Parquet format** for fast querying.

---

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
Glue Jobs	Python/Spark-based transformation jobs
Glue Data Catalog	Metadata store for Athena/Redshift
Amazon Athena	SQL-based query engine for S3
IAM Roles	Secure access control

✅ Pre-requisites
Before you begin:
S3 Bucket: Create a bucket (e.g., my-etl-bucket) with two folders:
raw_data/
cleaned_data/
IAM Role: Ensure an IAM role exists with at least the following permissions:
AWSGlueServiceRole managed policy
S3 read/write permissions for your bucket
Enable AWS Glue and Athena in the region you're working in.

🛠️ Step-by-Step Setup
1. Upload Raw Data to S3
Upload a sample CSV (or JSON) to the S3 raw_data/ folder:
s3://my-etl-spark-bucket/raw_data/data.csv
You can use the AWS Console or aws s3 cp command.

2. Configure and Run Glue Crawler (Raw Data)
Navigate to AWS Glue > Crawlers
Click Create Crawler
Name: raw-data-crawler
Source Type: S3
Path: s3://my-etl-spark-bucket/raw_data/
Choose IAM Role: AWSGlueServiceRole-GlueCrawlerRole
Target: Create or use database: my_etl_db
Run the crawler

🔍 Result: A table called raw_data will appear under the my_etl_db Glue database.

3. Create and Run AWS Glue ETL Job
Script: glue_etl_job.py

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
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
    connection_options = {"path": "s3://my-etl-bucket/cleaned_data"},
    format = "parquet"
)
job.commit()


## To Run:
Go to AWS Glue > Jobs
Click Create Job
Choose script editor and paste the above
Choose your existing IAM role
Run the job
✅ Output will be written to:
s3://my-etl-spark-bucket/cleaned_data/


## 4. IAM Role Fix: Add S3 Write Permissions
If your job fails with a PERMISSION_ERROR, do the following:
Go to IAM > Roles > AWSGlueServiceRole-GlueCrawlerRole
Add this inline policy:
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
      "Resource": "arn:aws:s3:::my-etl-spark-bucket/cleaned_data/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::my-etl-spark-bucket"
    }
  ]
}
✅ Replace my-etl-spark-bucket with your actual bucket name.


## 5. Run Crawler for Cleaned Data
Go to Glue > Crawlers
Create a new crawler: cleaned-data-crawler
Data Source: s3://my-etl-spark-bucket/cleaned_data/
Target database: my_etl_db
Run the crawler
✅ This adds a new table: cleaned_data in your Glue Catalog

## 6. Query Cleaned Data in Athena
Go to Amazon Athena > Query Editor
Choose Data Source: AwsDataCatalog
Choose Database: my_etl_db

## Run query:
SELECT * FROM cleaned_data LIMIT 10;
✅ You should see the transformed data loaded via Glue ETL job.

## 🔁 Re-running the Pipeline
Task	When to Run Again
Upload new raw data	Whenever new data arrives
Re-run raw-data-crawler	After uploading new files
Run Glue ETL Job	To re-transform newly added raw data
Run cleaned-data-crawler	To update the cleaned_data table
Query in Athena	After running all above steps


📬 Support
For help with permission errors, job failures, or Data Catalog issues, check:
AWS Glue Logs in CloudWatch
IAM Role permissions for Glue, S3, Athena
Athena Workgroup settings for output location


🏁 License
This project is licensed under the MIT License.
