from http import HTTPStatus
from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class RecipeResource(Resource):
    #클라이언트로부터 URL/recipes/1, URL/recipes/2, URL/recipes/3.... 이런식으로 호출된다.
    #경로(path)끝에 숫자로 된 경로를 정의한 변수명(recipe_id)으로 변경하여 처리해 준다.
    def get(self, recipe_id):
        try:
            # db접속
            connection = get_connection()

            query='''select *
                    from recipe
                    where id=%s
                    ;'''
            recode=(recipe_id, )

            # 커서(딕셔너리 셋으로 가져와라)
            #select문은 dictionary=True 한다.
            cursor=connection.cursor(dictionary=True)

            # 실행
            cursor.execute(query, recode)

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
                #"count":len(result_list),
                "info":result_list[0]}, HTTPStatus.OK
    
    #데이터를 업데이트하는 api들은 put함수를 사용한다.
    def put(self, recipe_id):
        #클라이언트에서 보낸 body의 json데이터를 받아오는 코드
        data=request.get_json()
        #print(data)

        try:
            # db접속
            connection = get_connection()

            # 쿼리작성
            query='''update recipe
                    set name=%s
                        ,description=%s
                        ,cook_time=%s
                        ,direction=%s
                    where id=%s
                    ; '''

            name=data['name']
            description=data['description']
            cook_time=data['cook_time']
            direction=data['direction']

            record=(name, description, cook_time, direction, recipe_id)

            # 커서
            cursor=connection.cursor()

            # 실행
            cursor.execute(query, record)

            # 커밋
            connection.commit()

            # 자원해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            print(e)
            connection.rollback()
            cursor.close()
            connection.close()
            return {"error":str(e)}, HTTPStatus.SERVICE_UNAVAILABLE

        return {"result":"success"}, HTTPStatus.OK

    #데이터를 삭제하는 api들은 delete함수를 사용한다.
    def delete(self, recipe_id):
        try:
            # db접속
            connection = get_connection()

            # 쿼리작성
            query='''delete from recipe
                    where id=%s
                    ; '''

            record=(recipe_id,)

            # 커서
            cursor=connection.cursor()

            # 실행
            cursor.execute(query, record)

            # 커밋
            connection.commit()

            # 자원해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            print(e)
            connection.rollback()
            cursor.close()
            connection.close()
            return {"error":str(e)}, HTTPStatus.SERVICE_UNAVAILABLE

        return {"result":"success"}, HTTPStatus.OK