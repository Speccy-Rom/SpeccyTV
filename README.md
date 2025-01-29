# Speccy TV 
### - streaming service with ETL on steroids
Streaming service with ETL on steroids

## Presentation

[Click here](docs/presentation)

## Architecture

![architecture](docs/architecture/architecture.png)

## Services

#### Movies Admin Service
This service is responsible for managing movies.

#### Movies_async_api Service
This service is responsible for asynchronous API calls.

#### Movies_auth Service
This service is responsible for user authentication and authorization.

#### Movies_billing Service
This service is responsible for billing.

#### Movies_etl Service
This service is responsible for ETL.

#### Movies_streaming_admin Service
This service is responsible for managing streaming.

#### Movies_streaming_converter Service
This service is responsible for converting streaming.

#### Movies_streaming_etl Service
This service is responsible for ETL on streaming.

#### Movies_ugc Service
This service is responsible for user generated content.

## Components

### S3 Storage
MinIO is an open-source object storage compatible with Amazon S3 API. It is released under the Apache v2 license and adheres to the philosophy of Spartan minimalism. MinIO simply runs its server with a single command, allowing you to store data using the full power of the S3 API.

### Movies Streaming Admin
Django Admin is a ready-made CRUDL interface with search, filters, and advanced settings.

### Movies Streaming API
Django Rest Framework (DRF) is a library that works with standard Django models to create a flexible and powerful API for the project.

### Movies Streaming Converter
FFmpeg is a set of free, open-source libraries that allow recording, converting, and streaming digital audio and video in various formats. It includes libavcodec for encoding and decoding audio and video, and libavformat for multiplexing and demultiplexing media containers. The name comes from the MPEG expert group and FF, meaning "fast forward".

FastAPI is a relatively new web framework written in Python for creating REST (and if you try hard, GraphQL) APIs, based on new features of Python 3.6+, such as type hints and native asynchronicity (asyncio). Additionally, FastAPI tightly integrates with OpenAPI-schema and automatically generates documentation for your API via Swagger and ReDoc.

### Airflow ETL
Apache Airflow is open-source software for creating, monitoring, and orchestrating data processing workflows.

## Sources
- [Microservices.io](https://microservices.io/)
- [Veeam Blog on Habr](https://habr.com/ru/company/veeam/blog/517392/)
- [Habr Post](https://habr.com/ru/post/512386/)