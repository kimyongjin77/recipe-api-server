from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config

from resources.recipe import RecipeListResource
from resources.recipe_info import RecipeResource
from resources.recipe_publish import RecipePublishResource
from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource, jwt_blacklist

app=Flask(__name__)

#환경파일 변수 셋팅
app.config.from_object(Config)
#JWT 토큰 라이브러리 만들기
jwt=JWTManager(app)

#로그아웃된 토큰을 검색해라..
#로그아웃된 토큰이 들어있는 set을 jwt에 알려준다.
#api호출시 토큰을 먼저 로그아웃set에 들어 있는 토큰인지 먼저 확인한다. 왜.. 로그아웃한 토큰이 사용되면 안되니까~
#api호출 시 마다 로그아웃된 토큰을 확인하여 있으면 {"msg": "Token has been revoked"}, 401 을 리턴한다.
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti=jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

#경로(path)와 리소스(api코드)를 연결한다.
api.add_resource(RecipeListResource, '/recipes')
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')
api.add_resource(UserRegisterResource, '/users/register')
api.add_resource(UserLoginResource, '/users/login')
api.add_resource(UserLogoutResource, '/users/logout')

if __name__=='__main__':
    app.run()