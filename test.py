import mysql.connector
#데이터베이스에 접속해서, 데이터 처리하는 테스트 코드
from mysql_connection import get_connection

name='순두부'
description='순두부찌개 조리법'
cook_time=28
direction='1.순두부를 잘 넣고 끊인다.'

try:
    # 데이터 인서트
    
    # db접속
    connection = get_connection()

    # 쿼리작성
    query='''insert into recipe
            (name, description, cook_time, direction)
            values
            ('된장찌개','된장찌개 조리법', 23, '1. 고기를 볶은 후, 물 넣고, 김치 넣고 끊인다...')
            ; '''

    query1='''insert into recipe
            (name, description, cook_time, direction)
            values
            (%s,%s,%s,%s)
            ; '''

    record=(name, description, cook_time, direction)

    # 커서
    cursor=connection.cursor()

    # 실행
    cursor.execute(query)

    cursor.execute(query1, record)

    # 커밋
    connection.commit()

    # 자원해제
    cursor.close()
    connection.close()

except mysql.connector.Error as e:
    print(e)
    cursor.close()
    connection.close()