from aiohttp.web_exceptions import HTTPConflict, HTTPUnauthorized, HTTPForbidden, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import docs, request_schema, response_schema, querystring_schema
from aiohttp_session import get_session

from app.quiz.schemes import (
    ThemeSchema, ThemeListSchema, QuestionSchema, ListQuestionSchema, ThemeIdSchema,
)
from app.web.app import View
from app.web.utils import json_response, check_basic_auth


# TODO: добавить проверку авторизации для этого View
class ThemeAddView(View):
    # TODO: добавить валидацию с помощью aiohttp-apispec и marshmallow-схем
    @docs(tags=['VKChat'], summary='Add theme', description='add theme')
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['key'])
        if not user or session['key'] != user.email:
            raise HTTPForbidden
        else:
            title = self.data['title']
            theme = await self.store.quizzes.get_theme_by_title(title)
            if theme:
                raise HTTPConflict
            theme = await self.store.quizzes.create_theme(title=title)
            return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    @docs(tags=['VKChat'], summary='List themes', description='list themes')
    @response_schema(ThemeListSchema)
    async def get(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['key'])
        if not user or session['key'] != user.email:
            raise HTTPForbidden
        else:
            themes = await self.store.quizzes.list_themes()
            raw_themes = [ThemeSchema().dump(theme) for theme in themes]
            return json_response(data={'themes': raw_themes})


class QuestionAddView(View):
    @docs(tags=['VKChat'], summary='Add question', description='add question to theme')
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['key'])
        if not user or session['key'] != user.email:
            raise HTTPForbidden
        else:
            title = self.data['title']
            theme_id = self.data['theme_id']
            answers = self.data['answers']
            only_answer: bool = False
            for answer in answers:
                if answer['is_correct']:
                    if only_answer:
                        raise HTTPBadRequest
                    only_answer = True
            if not only_answer:
                raise HTTPBadRequest
            if len(answers) == 1:
                raise HTTPBadRequest
            if not await self.store.quizzes.get_theme_by_id(theme_id):
                raise HTTPNotFound
            if await self.store.quizzes.get_question_by_title(title):
                raise HTTPConflict
            question = await self.store.quizzes.create_question(title, theme_id, answers)
            return json_response(data=({'id': question.id} | self.data))


class QuestionListView(View):
    @docs(tags=['VKChat'], summary='List questions', description='list questions by theme')
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['key'])
        if not user or session['key'] != user.email:
            raise HTTPForbidden
        else:
            theme_id = self.request.query.get('theme_id')
            questions = await self.store.quizzes.list_questions(theme_id)
            raw_questions = [QuestionSchema().dump(question) for question in questions]
            return json_response(data={'questions': raw_questions})
