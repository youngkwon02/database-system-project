import json
from django.http import JsonResponse
from .status import *
from .message import *
from .res import *


# GET /api/select
# desc: 레코드 검색 또는 컬럼 검색
# error:
#   1. 잘못된 HTTP METHOD
#   2. 필요한 값이 없는 경우


def select(request):
    # error 1. 잘못된 HTTP METHOD
    if request.method != 'GET':
        return JsonResponse(fail(BAD_REQUEST, WRONG_METHOD))

    keys = list(request.GET.keys())
    # error 2. 필요한 값이 없는 경우
    if('table' not in keys):
        return JsonResponse(fail(BAD_REQUEST, NULL_VALUE))
    try:
        cond = {}
        for key in keys:
            if key != 'table' and key != 'column':
                cond[key] = request.GET[key]

        t_cols = []
        if('column' in keys):
            t_cols = request.GET['column'].split(',')

        file_path = f"./disk/{request.GET['table']}.json"
        db_table = {}
        with open(file_path, 'r') as file:
            db_table = json.load(file)

        meta = db_table.get('meta_data')
        var_cols = list(meta.get('columns').get('variable').keys())
        var_cols_size = len(var_cols)
        fixed_cols = list(meta.get('columns').get('fixed').keys())
        cols = var_cols + fixed_cols
        slots = db_table.get('slotted_pages')
        res_data = []

        for slot in slots:
            slots = slot.get('slots')
            # slot에 저장된 record의 offset을 읽어옴
            for offset in slots:
                record = slot.get('records')[str(offset)]
                nb = list(record.get('nb').get('value'))
                ptrs = record.get('ptrs')
                null_cnt = [0, 0]
                _result = {}
                cond_pass = True
                for i in range(len(nb)):
                    _col = cols[i]

                    if nb[i] == 1:
                        _result[_col] = "null"
                        if i < var_cols_size:
                            null_cnt[0] += 1
                        else:
                            null_cnt[1] += 1
                    else:
                        # 가변길이 Data
                        if i < var_cols_size:
                            [location, size] = ptrs[i -
                                                    null_cnt[0]].get('value')
                            _result[_col] = record.get('variable_data')[
                                str(location)]

                        # 고정길이 Data
                        else:
                            _result[_col] = record.get('fixed_data')[i -
                                                                     var_cols_size - null_cnt[1]].get('value')

                    # 조건에 맞지 않으면 컬럼 탐색 멈추고 다음 Record 조회
                    if _col in cond.keys() and cond.get(_col) != _result.get(_col):
                        cond_pass = False
                        break

                # 조건을 만족하지 않아서 for loop를 탈출한 경우, Result Set에서 제외
                if cond_pass:
                    # 컬럼 검색
                    result = {}
                    for k in _result.keys():
                        if len(t_cols) == 0 or k in t_cols:
                            result[k] = _result.get(k)
                    res_data.append(result)

    except:
        return JsonResponse(fail(INTERNAL_SERVER_ERROR, SERVER_ERROR))

    return JsonResponse(success(OK, SELECT_RECORD_SUCCESS, res_data))
