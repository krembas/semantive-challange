import json
from json import JSONDecodeError
from typing import Optional, Tuple

import lxml
from lxml.html.clean import Cleaner
import requests

from django.db import Error as DjangoDatabaseOperationError
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.core.files.base import ContentFile

from djangoapp.apps.pages.models import PageTask, PageImage


class BaseView(View):

    def error_response(self, status: int, msg: str, exc: Optional[Exception] = None) -> JsonResponse:
        """Common command error handler that returns response with appropriate message"""
        e_msg = f"\nOriginally catched exception is: {exc.__class__.__name__}  ({exc})" \
            if exc and isinstance(exc, Exception) else ''
        return JsonResponse({'error_msg': msg or '' + (e_msg if settings.DEBUG else '')}, status=status)

    def update_or_create_task_object(self, url: str,
                                     page_body_content: Optional[str] = None,
                                     images_in_progress: Optional[bool] = None) \
            -> Tuple[Optional[PageTask], Optional[bool], Optional[JsonResponse]]:

        defaults = {}
        if page_body_content is not None:
            defaults['text_content'] = page_body_content
        if images_in_progress is not None:
            defaults['images_in_progress'] = images_in_progress

        try:
            page, created = PageTask.objects.update_or_create(url=url, defaults=defaults)
        except DjangoDatabaseOperationError as e:
            return None, None, self.error_response(500, f"Error during saving page data in db!", exc=e)
        return page, created, None

    def get_page_object_or_error_response(self, task_id: int) -> Tuple[Optional[PageTask], Optional[JsonResponse]]:
        try:
            page = PageTask.objects.get(id=task_id)
        except PageTask.DoesNotExist as e:
            return None, self.error_response(400, f"Taks ID={task_id} not found!", exc=e)
        except DjangoDatabaseOperationError as e:
            return None, self.error_response(500, f"Error during loading task data from db!", exc=e)
        return page, None


class TaskView(BaseView):
    """View for handling creating new task API call"""

    def post(self, request):

        # handle url argument
        try:
            url = json.loads(request.body)['url']
        except (JSONDecodeError, KeyError):
            return self.error_response(400, 'No `url` request argument or passed not in JSON format!')

        # get page content
        resp = requests.get(url)
        if resp.status_code != 200:
            msg = f"Problem with retrieving a page data from {url}: HTTP status code is {resp.status_code}"
            return self.error_response(400, msg)

        # create task with initial statuses
        page, created, err_resp = self.update_or_create_task_object(url=url, page_body_content=None, images_in_progress=True)
        if err_resp:
            return err_resp

        # parse page body
        try:
            page_body_etree = lxml.html.fromstring(resp.content).xpath('//body')[0]
        except Exception as e:
            return self.error_response(500, f"Error during retrieving or parsing data from {url} !", exc=e)

        # Cleans page body data (removes any <script> tags and any Javascript, like an onclick attribute) and
        # convert result to plain text (removes any HTML tags).
        page_body_content = Cleaner(scripts=True, javascript=True).clean_html(page_body_etree).text_content()

        # update task with page content
        page, created, err_resp = self.update_or_create_task_object(url=url, page_body_content=page_body_content)
        if err_resp:
            return err_resp

        # remove previously gathered images
        if not created:
            for el in PageImage.objects.filter(page=page).all():
                el.delete()

        # get all images urls
        images_urls = set()  # do not duplicate same urls
        for img in page_body_etree.xpath('//img'):
            images_urls.add(img.get('src'))

        # save images sequentially ("images downloading may be slow" ;)
        for img_url in images_urls:
            try:
                resp = requests.get(img_url)
                if resp.status_code != 200:
                    continue  # just skip errors ;)
                file_name = img_url.split('/')[-1]
                image_content = ContentFile(resp.content)
                imgobj = PageImage(page=page)
                imgobj.image.save(file_name, image_content, save=True)
                imgobj.save()
            except DjangoDatabaseOperationError as e:
                return self.error_response(500, f"Error during saving page image data in db!", exc=e)

        # update image gathering status
        page.images_in_progress = False
        page.save()

        return JsonResponse({'task_id': page.pk, 'url': page.url}, status=200)


class TaskStatusView(BaseView):
    """View that  handles get task status APO call"""
    def get(self, request, task_id):
        page, err_resp = self.get_page_object_or_error_response(task_id)
        if err_resp:
            return err_resp

        return JsonResponse({
            'task_id': page.pk,
            'url': page.url,
            'text_ready': page.text_content is not None,
            'images_ready': not page.images_in_progress,
        }, status=200)


class PageContentView(BaseView):
    """View that handles get page text API call"""

    def get(self, request, task_id):
        page, err_resp = self.get_page_object_or_error_response(task_id)
        if err_resp:
            return err_resp

        return JsonResponse({'task_id': page.pk, 'url': page.url, 'text': page.text_content},
                            status=200 if page.text_content else 202)


class PageImagesView(BaseView):
    """View that handles get page images API call """
    def get(self, request, task_id):
        page, err_resp = self.get_page_object_or_error_response(task_id)
        if err_resp:
            return err_resp

        images_urls = []
        for el in PageImage.objects.filter(page=page):
            images_urls.append(el.image.url)

        return JsonResponse({'task_id': page.pk, 'url': page.url, 'images_urls': images_urls},
                            status=202 if page.images_in_progress else 200)
