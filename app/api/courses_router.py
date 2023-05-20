import pprint
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Response, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from app.common.error import BadRequest
from app.conf import logging
from app.conf.config import Config
from app.db.db import get_db
from app.models.course import CourseModel, CourseModelList, ChapterModel
from app.schemas import courses as repository

router = APIRouter()

sort_options = {
    'alphabetical': [('name', 1)],
    'date': [('date', -1)],
    'total_rating': [('total_rating', -1)]
}


@router.get('/', include_in_schema=False, status_code=200)
@router.get('', response_model=CourseModelList | None, status_code=200,
            responses={
                400: {}
            })
async def get_courses(
        db: AsyncIOMotorClient = Depends(get_db),
        sort: str = 'alphabetical',
        domain: str = None,
):
    try:
        if sort not in sort_options.keys():
            raise HTTPException(status_code=400, detail="doesnt supported sort options")

        sort_query = sort_options[sort]
        filter_query = {}
        if domain:
            filter_query['domain'] = domain

        response = await repository.get_all_courses(
            db,
            filter_query,
            sort_query
        )
        return CourseModelList(courses=response, count=len(response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/course/{course_id}', include_in_schema=False, status_code=200)
@router.get('/course/{course_id}', response_model=CourseModel | None, status_code=200,
            responses={
                400: {}
            })
async def get_course_by_id(
        course_id: UUID,
        db: AsyncIOMotorClient = Depends(get_db),
):
    try:
        response = await repository.get_course(
            db,
            course_id
        )
        if response is None:
            raise HTTPException(status_code=404, detail="Course not found")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/chapter/{chapter_id}', include_in_schema=False, status_code=200)
@router.get('/chapter/{chapter_id}', response_model=ChapterModel | None, status_code=200,
            responses={
                400: {}
            })
async def get_chapter_by_id(
        chapter_id: UUID,
        db: AsyncIOMotorClient = Depends(get_db),
):
    try:
        response = await repository.get_chapter(
            db,
            chapter_id
        )
        if response is None:
            raise HTTPException(status_code=404, detail="Chapter not found")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/rating/{chapter_id}', include_in_schema=False, status_code=200)
@router.put('/rating/{chapter_id}', status_code=200,
            responses={
                400: {}
            })
async def update_rating(
        chapter_id: UUID,
        rating: bool,
        db: AsyncIOMotorClient = Depends(get_db),
):
    try:
        response = await repository.update_rating(db, chapter_id, rating)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

