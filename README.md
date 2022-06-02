# database-system-project
Project for database system class in 2022-1

---

### 🦋 Table 생성 요청 및 응답 (CREATE Query)
<img width="500" alt="스크린샷 2022-06-02 오후 4 42 14" src="https://user-images.githubusercontent.com/39653584/171579649-a5111c7e-99c6-4bca-8b5b-ec1a0e28ed0f.png">

### 🦋 Table 생성 결과 (*.json) 

 ```JSON
  {
	"meta_data": {
		"columns": {
			"fixed": {
				"id": "CHAR(5)",
				"price": "CHAR(7)"
			},
			"variable": {
				"model": "VARCHAR",
				"released": "VARCHAR"
			}
		},
		"size_of_page": 4000,
		"max_record_of_slot": 4,
		"size_of_slot": 4,
		"created_at": "2022-06-02 16:43:33",
		"updated_at": "2022-06-02 16:43:33"
	},
	"slotted_pages": [
		{
			"entities": {
				"start_of_fs": 4,
				"size_of_fs": 3996
			},
			"slots": [],
			"records": {}
		}
	]
}
```

<br>

---

<br>

### ☀️ Record 추가 요청 및 응답 (INSERT Query)
<img width="500" alt="스크린샷 2022-06-02 오후 4 46 36" src="https://user-images.githubusercontent.com/39653584/171580489-8d087d89-ce09-49dd-a7ed-1dbcc48f18a9.png">


### ☀️ Record 추가 결과 (*.json) 

 ```JSON
{
	"meta_data": {
		"columns": {
			"fixed": {
				"id": "CHAR(5)",
				"price": "CHAR(7)"
			},
			"variable": {
				"model": "VARCHAR",
				"released": "VARCHAR"
			}
		},
		"size_of_page": 4000,
		"max_record_of_slot": 4,
		"size_of_slot": 4,
		"created_at": "2022-06-02 16:43:33",
		"updated_at": "2022-06-02 16:47:27"
	},
	"slotted_pages": [
		{
			"entities": {
				"start_of_fs": 8,
				"size_of_fs": 3921
			},
			"slots": [
				3959
			],
			"records": {
				"3959": {
					"nb": {
						"value": "0000",
						"location": 0,
						"size": 1
					},
					"ptrs": [
						{
							"value": [21, 13],
							"location": 1,
							"size": 4
						},
						{
							"value": [34, 7],
							"location": 5,
							"size": 4
						}
					],
					"fixed_data": [
						{
							"value": "10000",
							"location": 9,
							"size": 5
						},
						{
							"value": "1200000",
							"location": 14,
							"size": 7
						}
					],
					"variable_data": {
						"21": "iPhone 12 Pro",
						"34": "2020-11"
					}
				}
			}
		}
	]
}
```

<br>

---

<br>

### ☀️ Record 조회, 컬럼 탕색 요청 및 응답 (SELECT Query)
<img width="500" alt="스크린샷 2022-06-02 오후 4 50 22" src="https://user-images.githubusercontent.com/39653584/171581210-718dcb94-d578-4432-a30f-5b885502f511.png">
