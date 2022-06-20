from http import HTTPStatus
import http
from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class RecipePublishResource(Resource):
    #레시피를 공개한다.(is_publish컬럼을 1로 변경)
    def put(self, recipe_id):
        try:
            # db접속
            connection = get_connection()

            # 쿼리작성
            query='''update recipe
                    set is_publish=1
                    where id=%s
                    ; '''

            #record=(recipe_id,)
            #여러행 데이터 변수
            record=[(recipe_id,)]

            # 커서
            cursor=connection.cursor()

            # 실행
            #cursor.execute(query, record)
            # 여러행 데이터변수 일괄 실행
            cursor.executemany(query, record)

            print(str(cursor.rowcount) + '행 처리')

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

        # finally:
        #     if connection.is_connected():
        #         cursor.close()
        #         connection.close()

        return {"result":"success"}, HTTPStatus.OK

    #레시피를 임시저장한다.(is_publish컬럼을 0으로 변경)
    def delete(self, recipe_id):
        try:
            # db접속
            connection = get_connection()

            # 쿼리작성
            query='''update recipe
                    set is_publish=0
                    where id=%s
                    ; '''

            #record=(recipe_id,)
            #여러행 데이터 변수
            record=[(recipe_id,)]

            # 커서
            cursor=connection.cursor()

            # 실행
            #cursor.execute(query, record)
            # 여러행 데이터변수 일괄 실행
            cursor.executemany(query, record)

            print(str(cursor.rowcount) + '행 처리')
            
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

        # finally:
        #     if connection.is_connected():
        #         cursor.close()
        #         connection.close()

        return {"result":"success"}, HTTPStatus.OK
