import json
from datetime import datetime
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
        return JsonResponse(success(OK, SELECT_RECORD_SUCCESS, res_data))

    except:
        return JsonResponse(fail(INTERNAL_SERVER_ERROR, SERVER_ERROR))


# POST /api/insert
# desc: 레코드 삽입
# error:
#   1. 잘못된 HTTP METHOD
#   2. 필요한 값이 없는 경우
#   3. 필요한 컬럼에 대한 값이 전달되지 않은 경우

def insert(request):
    # error 1. 잘못된 HTTP METHOD
    if request.method != 'POST':
        return JsonResponse(fail(BAD_REQUEST, WRONG_METHOD))

    # Request-Body를 utf-8 방식으로 디코딩 (한국어(receiverName) 디코딩을 위해)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    # error 2. 필요한 값이 없는 경우
    if('table' not in body):
        return JsonResponse(fail(BAD_REQUEST, NULL_VALUE))

    file_path = f"./disk/{body['table']}.json"
    db_table = {}
    with open(file_path, 'r') as file:
        db_table = json.load(file)

    try:
        meta = db_table.get('meta_data')
        var_cols = list(meta.get('columns').get('variable').keys())
        fixed_cols = list(meta.get('columns').get('fixed').keys())
        cols = var_cols + fixed_cols
        nb = ""
        value = {}
        target_page = db_table.get('slotted_pages')[-1]
        page_entities = target_page.get('entities')

        for col in cols:
            if col not in body.keys():
                # error 3. 필요한 컬럼에 대한 값이 전달되지 않은 경우
                return JsonResponse(fail(BAD_REQUEST, OUT_OF_VALUE))
            if body.get(col) == 'null':
                nb += '1'
            else:
                nb += '0'
            value[col] = body.get(col)

        current_offset = 1
        new_ptrs = []
        fixed_data = []
        variable_data = {}
        for col in cols:
            # 가변길이 Column
            if col in var_cols and value[col] != 'null':
                new_ptr = {
                    "value": [],
                    "location": current_offset,
                    "size": meta.get('size_of_slot')
                }
                current_offset += meta.get('size_of_slot')
                new_ptrs.append(new_ptr)
            # 고정길이 Column
            if col in fixed_cols and value[col] != 'null':
                fixed_data.append({
                    "value": value[col],
                    "location": current_offset,
                    "size": len(value[col])
                })
                current_offset += len(value[col])
        ptr_index = 0
        for v_col in var_cols:
            if value[v_col] != 'null':
                new_ptrs[ptr_index]['value'] = [
                    current_offset, len(value[v_col])]
                variable_data[current_offset] = value[v_col]
                current_offset += len(value[v_col])
                ptr_index += 1

        page_entities['size_of_fs'] -= current_offset
        new_offset = page_entities.get(
            'start_of_fs') + page_entities['size_of_fs']

        new_record = {
            "nb": {
                "value": nb,
                "location": 0,
                "size": 1,
            },
            "ptrs": new_ptrs,
            "fixed_data": fixed_data,
            "variable_data": variable_data
        }

        new_record_size = 0
        for key in new_record.keys():
            attr = new_record.get(key)
            if key == 'nb':
                new_record_size += attr.get('size')
            elif key == 'ptrs':
                for ptr in attr:
                    new_record_size += ptr.get('size')
            elif key == 'fixed_data':
                for fd in attr:
                    new_record_size += fd.get('size')
            else:
                # variable length column data
                addr = sorted(
                    list(map(lambda x: int(x), attr)))
                if len(addr) != 0:
                    new_record_size += (addr[-1] - addr[0])

        if len(db_table['slotted_pages'][-1]['slots']) < meta.get('max_record_of_slot'):
            db_table['slotted_pages'][-1]['slots'] = [new_offset] + \
                db_table['slotted_pages'][-1]['slots']
            db_table['slotted_pages'][-1]['records'][new_offset] = new_record
            db_table['slotted_pages'][-1]['entities']['start_of_fs'] += db_table['meta_data']['size_of_slot']
            db_table['slotted_pages'][-1]['entities']['size_of_fs'] -= new_record_size
        else:
            new_offset = db_table.get('size_of_page') - new_record_size
            db_table['slotted_pages'].append({
                "entities": {
                    "start_of_fs": 8,
                    "size_of_fs": new_offset - 8
                },
                "slots": [new_offset],
                "records": {
                    new_offset: new_record
                }
            })
        db_table['meta_data']['updated_at'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(db_table, file, indent="\t")

        return JsonResponse(success(OK, CREATE_RECORD_SUCCESS))

    except:
        return JsonResponse(fail(INTERNAL_SERVER_ERROR, SERVER_ERROR))


# POST /api/create
# desc: 테이블 생성
# error:
#   1. 잘못된 HTTP METHOD
#   2. 필요한 값이 없는 경우
#   3. 올바르지 않은 컬럼 타입이 전달된 경우

def create(request):
    # error 1. 잘못된 HTTP METHOD
    if request.method != 'POST':
        return JsonResponse(fail(BAD_REQUEST, WRONG_METHOD))

    # Request-Body를 utf-8 방식으로 디코딩 (한국어(receiverName) 디코딩을 위해)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    # error 2. 필요한 값이 없는 경우
    if('table' not in body):
        return JsonResponse(fail(BAD_REQUEST, NULL_VALUE))

    meta_data = {}
    fixed = {}
    variable = {}
    try:
        for k in body.keys():
            if k == 'table':
                continue
            col_type = body.get(k)
            # error 3. 올바르지 않은 컬럼 타입이 전달된 경우
            if col_type != 'VARCHAR' and 'CHAR(' not in col_type:
                return JsonResponse(fail(BAD_REQUEST, OUT_OF_VALUE))

            if col_type == 'VARCHAR':
                variable[k] = 'VARCHAR'
            else:
                fixed[k] = col_type

        columns = {
            'fixed': fixed,
            'variable': variable
        }
        meta_data['columns'] = columns
        meta_data['size_of_page'] = 4000    # Fixed Value
        meta_data['max_record_of_slot'] = 4  # Fixed Value
        meta_data['size_of_slot'] = 4       # Fixed Value
        meta_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        meta_data['updated_at'] = meta_data['created_at']
        slotted_pages = [{
            'entities': {
                'start_of_fs': 4,
                'size_of_fs': 4000 - 4
            },
            'slots': [],
            'records': {}
        }]

        table = {
            'meta_data': meta_data,
            'slotted_pages': slotted_pages
        }

        file_path = f"./disk/{body['table']}.json"
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(table, file, indent="\t")

        return JsonResponse(success(OK, CREATE_TABLE_SUCCESS))

    except:
        return JsonResponse(fail(INTERNAL_SERVER_ERROR, SERVER_ERROR))
