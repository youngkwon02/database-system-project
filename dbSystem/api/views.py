import json
from django.http import JsonResponse
from .status import *
from .message import *
from .res import *
import sys


# GET /api/select
# desc: 레코드 검색 또는 컬럼 검색
# error:
#   1. 잘못된 HTTP METHOD
#   2. 필요한 값이 없는 경우


def select(request):
    # error 1. 잘못된 HTTP METHOD
    if request.method != 'GET':
        return JsonResponse(fail(BAD_REQUEST, WRONG_METHOD))

    # error 2. 필요한 값이 없는 경우
    if('table' not in request.GET.keys()):
        return JsonResponse(fail(BAD_REQUEST, NULL_VALUE))

    file_path = f"./disk/{request.GET['table']}.json"
    db_table = {}
    with open(file_path, 'r') as file:
        db_table = json.load(file)
