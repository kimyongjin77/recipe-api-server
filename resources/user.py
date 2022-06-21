from datetime import timedelta
from http import HTTPStatus
import http
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector
from email_validator import validate_email, EmailNotValidError

from utils import check_password, hash_password

#회원가입저장
# 메소드 : post
# 경로 : users/register
# 데이터 : username, email, password
class UserRegisterResource(Resource):
    def post(self):
        #클라이언트에서 보낸 body의 json데이터를 받아오는 코드
        # {
        #     "username": "홍길동",
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }
        data=request.get_json()
        #print(data)

        username=data['username']
        email=data['email']
        password=data['password']

        #이메일 주소형식이 제대로 된 주소형식인지 확인하는 코드 작성.
        try:
            # Validate & take the normalized form of the email
            # address for all logic beyond this point (especially
            # before going to a database query where equality
            # does not take into account normalization).
            validated_email = validate_email(email).email
            #print(validated_email)
            #return {"validate_email":"success"}, HTTPStatus.OK
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            #print('error : ' + str(e))
            return {"error":str(e)}, HTTPStatus.BAD_REQUEST

        #비밀번호 정책을 확인한다. 자리수는 4자리이상 12자리 이하로 가능하게...
        if len(password)<4 or len(password)>12:
            return {"error":'비밀번호 길이(4~12)를 확인하세요.'}, HTTPStatus.BAD_REQUEST

        #비밀번호를 암호화 한다.
        hashed_password=hash_password(password)
        #print(hashed_password)
        #print(check_password(password, hashed_password))

        try:
            # 데이터 인서트
            # db접속
            connection = get_connection()

            # 쿼리작성
            query='''insert into user
                    (username, email, password)
                    values
                    (%s,%s,%s)
                    ; '''

            record=(username, validated_email, hashed_password)

            # 커서
            cursor=connection.cursor()

            # 실행
            cursor.execute(query, record)

            # 커밋
            connection.commit()

            # db에 저장된 아이디값 가져오기.
            # 자동증가된 id컬럼 값
            user_id=cursor.lastrowid

            # 자원해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            print(e)
            connection.rollback()
            cursor.close()
            connection.close()
            return {"error":str(e)}, HTTPStatus.SERVICE_UNAVAILABLE

        #클라이언트에 user_id도 포함하여 응답해야 한다.
        #return {"result":"success", "user_id":user_id}, HTTPStatus.OK
        #user_id값은 보안이 중요하다, 해킹 가능성이 있으므로
        #JWT로 암호화해서 보낸다.
        access_token=create_access_token(user_id)

        return {"result":"success", "access_token":access_token}, HTTPStatus.OK

#로그인
# 메소드 : post
# 경로 : users/login
# 데이터 : email, password
class UserLoginResource(Resource):
    def post(self):
        #1.요청 body에서 데이터를 가져온다.
        #클라이언트에서 보낸 body의 json데이터를 받아오는 코드
        # {
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }
        data=request.get_json()
        #print(data)

        email=data['email']
        password=data['password']

        #2.이메일 검증
        #이메일 주소형식이 제대로 된 주소형식인지 확인하는 코드 작성.
        try:
            # Validate & take the normalized form of the email
            # address for all logic beyond this point (especially
            # before going to a database query where equality
            # does not take into account normalization).
            validated_email = validate_email(email).email
            #print(validated_email)
            #return {"validate_email":"success"}, HTTPStatus.OK
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            #print('error : ' + str(e))
            return {"error":"이메일 형식을 확인해 주세요"}, HTTPStatus.BAD_REQUEST

        #3.비밀번호 정책 확인
        #비밀번호 정책을 확인한다. 자리수는 4자리이상 12자리 이하로 가능하게...
        if len(password)<4 or len(password)>12:
            return {"error":'비밀번호 길이(4~12)를 확인하세요.'}, HTTPStatus.BAD_REQUEST

        #4.이메일로 사용자정보 조회
        try:
            # db접속
            connection = get_connection()

            query='''select *
                    from user
                    where email=%s
                    ;'''

            record=(validated_email,)

            # 커서(딕셔너리 셋으로 가져와라)
            #select문은 dictionary=True 한다.
            cursor=connection.cursor(dictionary=True)

            # 실행
            cursor.execute(query, record)
            
            # 데이터fetch : select문은 아래함수를 이용해서 데이터를 가져온다.
            result_list=cursor.fetchall()
            #print(result_list)

            if len(result_list) != 1:
                return {"error":"회원정보가 없습니다. 회원가입을 먼저 하세요"}, HTTPStatus.BAD_REQUEST

            #5.비밀번호 비교
            check=check_password(password, result_list[0]['password'])
            if check==False:
                return {"error":"비밀번호가 틀립니다. 확인하세요."}, HTTPStatus.BAD_REQUEST

            #중요! db에서 가져온 timestamp데이터타입은 파이썬의 datetime으로 자동 변경된다.
            #이 데이터는 json으로 바로 보낼 수 없으므로 문자열로 바꿔서 다시 저장해서 보낸다.
            i=0
            for record in result_list:
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                i=i+1

            #6.응답
            # return {"result":"success",
            #         "count":len(result_list),
            #         "result_list":result_list}, HTTPStatus.OK
            
            user_id=result_list[0]['id']
            username=result_list[0]['username']
            #user_id값은 보안이 중요하다, 해킹 가능성이 있으므로
            #JWT로 암호화해서 보낸다.
            access_token=create_access_token(user_id)
            #토큰 유효기한 셋팅
            #access_token=create_access_token(user_id, expires_delta=timedelta(minutes=1))
            
            return {"result":"success", "access_token":access_token, "username":username}, HTTPStatus.OK


        except mysql.connector.Error as e:
            print(e)
            return {"error":str(e)}, HTTPStatus.SERVICE_UNAVAILABLE

        finally:
            # 자원해제
            #print('finally')
            cursor.close()
            connection.close()


#로그아웃(토큰 취소)
jwt_blacklist=set()     #로그아웃 한 토큰 집합(데이터)
# 메소드 : post
# 경로 : users/logout
# 데이터 : Header user_id토큰
#로그인시 JWT라이브러리로 토큰을 발행하는데 유효기간이 들어 있다.
#로그아웃을 하면 해당 토큰을 set에 넣는다. 해당 토큰은 revoke(취소) 되었다는 의미이다.
class UserLogoutResource(Resource):
    @jwt_required(optional=False)
    def post(self):
        jti=get_jwt()['jti']        #토큰을 가져온다.
        #print(jti)

        jwt_blacklist.add(jti)      #토큰을 집합에 넣는다.

        return {"result":"success"}, HTTPStatus.OK