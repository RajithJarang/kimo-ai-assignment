import logging
from typing import List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from app.conf.config import Config
from app.models.course import CourseModel, ChapterModel
from app.pipeline.rating_pipeline import rating_pipeline

__db_name = Config.app_settings.get('db_name')
__db_collection = Config.app_settings.get('db_collection')


async def get_all_courses(
        conn: AsyncIOMotorClient,
        filter_query,
        sort_query
) -> List[CourseModel] | None:
    logging.info('Get all courses called')
    cursor = conn[__db_name].get_collection(__db_collection).find(filter_query).sort(sort_query)
    all_courses = await cursor.to_list(None)
    return all_courses


async def get_course(
        conn: AsyncIOMotorClient,
        course_id: UUID
) -> CourseModel | None:
    logging.info(f"Calling get_course with course_id{course_id}")
    response = await conn[__db_name].get_collection(__db_collection).find_one({'id': course_id})
    if response is None:
        logging.info(f"No course found for course_id{course_id}")
        return None
    return CourseModel(**response)


async def get_chapter(
        conn: AsyncIOMotorClient,
        chapter_id: UUID
) -> ChapterModel | None:
    logging.info(f"Calling get_chapter with chapter_id : {chapter_id}")
    response = await conn[__db_name].get_collection(__db_collection).find_one({'chapters.id': chapter_id},
                                                                              {'chapters.$': 1})
    if response is None or response.get('chapters') is None or not response.get('chapters'):
        logging.info(f"No chapters found for chapter_id : {chapter_id}")
        return None
    chapters = response.get('chapters')[0]
    return ChapterModel(**chapters)


async def update_rating(
        conn: AsyncIOMotorClient,
        chapter_id: UUID,
        rating: bool
) -> bool:
    logging.info("Updating rating for chapter %s", chapter_id)
    query = ({'chapters.id': chapter_id})
    resp = await conn[__db_name][__db_collection].find_one_and_update(
        query,
        {
            "$inc": {
                "chapters.$.rating.total_ratings": 1,
                "chapters.$.rating.positive_ratings": 1 if rating else 0,
                "chapters.$.rating.negative_ratings": 1 if not rating else 0,
            }
        },
        rating_pipeline(rating),
    )
    return True


