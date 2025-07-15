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
