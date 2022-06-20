from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

# API 를 만들기 위한 클래스 작성
# class(클래스)란?? 변수와 함수로 구성된 묶음!

# 클래스는 상속이 가능하다.
# API를 만들기 위한 클래스는 flask_restful 라이브러리의
# Resource 클래스를 상속해서 만들어야 한다.
class RecipeListResource(Resource):
    #restful api의 메소드에 해당하는 함수 작성
    #api를 사용/호출 할려면 헤더에 인증키/값 토큰이 있어야 한다.
    @jwt_required()
    def post(self):     #함수명은 프레임워크의 정의이다.
        #api 실행 코드를 여기에 작성
        
        #클라이언트에서 보낸 body의 json데이터를 받아오는 코드
        data=request.get_json()
        #print(data)

        #user_id를 create_access_token(user_id)로 암호화 했다.
        #인증토큰을 복호화 한다.
        user_id=get_jwt_identity()

        try:
            # 데이터 인서트
            # db접속
            connection = get_connection()

            # 쿼리작성
            query='''insert into recipe
                    (name, description, cook_time, direction, user_id)
                    values
                    (%s,%s,%s,%s,%s)
                    ; '''

            name=data['name']
            description=data['description']
            cook_time=data['cook_time']
            direction=data['direction']
            #user_id=data['user_id']

            record=(name, description, cook_time, direction, user_id)

            # 커서
            cursor=connection.cursor()

            # 실행
            cursor.execute(query, record)

            # 커밋
            connection.commit()

            # db에 저장된 아이디값 가져오기.
            # 자동증가된 id컬럼 값
            recipe_id=cursor.lastrowid

            # 자원해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            print(e)
            connection.rollback()
            cursor.close()
            connection.close()
            return {"error":str(e)}, HTTPStatus.SERVICE_UNAVAILABLE

        return {"result":"success", "recipe_id":recipe_id}, HTTPStatus.OK

    def get(self):
        #쿼리스트링으로 오는 데이터는 아래처럼 처리해 준다.
        #요청 데이터 파라메터
        offset=request.args.get('offset')
        limit=request.args.get('limit')
        #print(offset, limit)

        try:
            # db접속
            connection = get_connection()

            query='''select *
                    from recipe
                    where is_publish=1
                    limit '''+offset+''','''+limit+''';'''

            # 커서(딕셔너리 셋으로 가져와라)
            #select문은 dictionary=True 한다.
            cursor=connection.cursor(dictionary=True)

            # 실행
            cursor.execute(query)

            # 데이터fetch : select문은 아래함수를 이용해서 데이터를 가져온다.
            result_list=cursor.fetchall()
            #print(result_list)

            #중요! db에서 가져온 timestamp데이터타입은 파이썬의 datetime으로 자동 변경된다.
            #이 데이터는 json으로 바로 보낼 수 없으므로 문자열로 바꿔서 다시 저장해서 보낸다.
            i=0
            for record in result_list:
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                i=i+1

            # 자원해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, HTTPStatus.SERVICE_UNAVAILABLE

        return {"result":"success",
                "count":len(result_list),
                "result_list":result_list}, HTTPStatus.OK