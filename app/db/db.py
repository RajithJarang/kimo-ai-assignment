import asyncio
import json
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging

from app.conf.config import Config
from app.models.course import CourseModel

load_dotenv()

db_client: AsyncIOMotorClient = None


async def get_db() -> AsyncIOMotorClient:
    return db_client


async def connect_and_init_db():
    global db_client
    try:
        db_client = AsyncIOMotorClient(
            Config.app_settings.get('mongodb_url'),
            username=Config.app_settings.get('db_username'),
            password=Config.app_settings.get('db_password'),
            maxPoolSize=Config.app_settings.get('max_db_conn_count'),
            minPoolSize=Config.app_settings.get('min_db_conn_count'),
            uuidRepresentation="standard",
        )
        logging.info('Connected to mongo.')
    except Exception as e:
        logging.exception(f'Could not connect to mongo: {e}')
        raise


async def close_db_connect():
    global db_client
    if db_client is None:
        logging.warning('Connection is None, nothing to close.')
        return
    db_client.close()
    db_client = None
    logging.info('Mongo connection closed.')


async def init_database():
    client: AsyncIOMotorClient = None
    try:
        client = AsyncIOMotorClient(
            Config.app_settings.get('mongodb_url'),
            username=Config.app_settings.get('db_username'),
            password=Config.app_settings.get('db_password'),
            maxPoolSize=Config.app_settings.get('max_db_conn_count'),
            minPoolSize=Config.app_settings.get('min_db_conn_count'),
            uuidRepresentation="standard",
        )
        logging.info('Initializing database')
        # We load the database if
        db_name, db_collection = Config.app_settings.get('db_name'), Config.app_settings.get('db_collection')
        collection = client[db_name].get_collection(db_collection)
        if collection is not None and await collection.count_documents({}) == 0:
            logging.info('Loading courses from json file Database')
            courses_file = Config.app_settings.get('courses_file')
            if courses_file is not None:
                with open(courses_file) as f:
                    data = json.load(f)
                    items = [CourseModel(**item).dict() for item in data]
                    await collection.insert_many(items)
                    await set_indexing(collection)
                    await set_pipeline(collection)
                    logging.info('Courses inserted successfully')
            else:
                logging.exception("No courses file found")
        else:
            logging.info('Database already loaded')

    except Exception as e:
        logging.exception(f'Error loading init data into database {e}')
        raise
    finally:
        client.close()


async def set_indexing(collection):
    try:
        # General purpose indexing of id fields
        await collection.create_index('id')

        # ascending indexing of name fields
        await collection.create_index([('name', 1)])

        # descending indexing of date fields
        await collection.create_index([('date', -1)])

        # descending indexing of rating fields
        await collection.create_index([('rating', -1)])

        # for domain queries
        await collection.create_index('domain')

        # General purpose indexing of id fields
        await collection.create_index('chapters.id')

        # accesnding indexing of name of chapters
        await collection.create_index([('chapters.name', 1), ])

        # decending indexing of rating of chapters
        await collection.create_index([('chapters.rating', -1)])

    except Exception as e:
        logging.exception(f'Error setting indexing')
        pass


async def set_pipeline(collection):
    db_name, db_collection = Config.app_settings.get('db_name'), Config.app_settings.get('db_collection')

    # Used mongodb compass to write the aggrator
    pipeline = [
        {
            '$unwind': {
                'path': '$chapters',
                'includeArrayIndex': 'true'
            }
        }, {
            '$group': {
                '_id': '$_id',
                'positive_rating': {
                    '$sum': '$chapters.rating.positive_ratings'
                },
                'negative_rating': {
                    '$sum': '$chapters.rating.negative_ratings'
                },
                'total_rating': {
                    '$sum': '$chapters.rating.total_ratings'
                }
            }
        }, {
            '$addFields': {
                'rating': {
                    '$cond': {
                        'if': {
                            '$eq': [
                                '$total_rating', 0
                            ]
                        },
                        'then': 0,
                        'else': {
                            '$divide': [
                                {
                                    '$subtract': [
                                        '$positive_rating', '$negative_rating'
                                    ]
                                }, '$total_rating'
                            ]
                        }
                    }
                }
            }
        }, {
            '$project': {
                'rating': 1
            }
        }, {
            '$merge': {
                'into': 'courses',
                'on': '_id',
                'whenMatched': 'merge'
            }
        }
    ]

    result = collection.aggregate(pipeline)

    # Print the result
    async for document in result:
        print(document)
