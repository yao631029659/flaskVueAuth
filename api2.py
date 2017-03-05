from flask import Flask, g,jsonify,request,url_for
from flask_restful import Api, Resource, reqparse, abort,fields,marshal_with
from flask_httpauth import HTTPTokenAuth,HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from model import db,Users,Customers
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api2.sqlite'
db.init_app(app)
# 添加允许垮站访问
CORS(app)


# 用app的密码加密 token
serializer = Serializer(app.config['SECRET_KEY'], expires_in=1800)
api = Api(app)

# token登陆
auth = HTTPTokenAuth(scheme='Bearer')
# 注册
@app.route('/api/Account/Register',methods=["POST"])
def register():
    print("register 被调用")
    print(request.json)
    username = request.form['email']
    password = request.form['password']
    comfirm_password=request.form['confirmPassword']

    print(username)
    print(password)
    print(comfirm_password)
    newUser=Users(request.form['email'],request.form['password'])
    db.session.add(newUser)
    db.session.commit()
    print('执行道这里')
    return (jsonify({'username': newUser.username}), 201)

# 登陆并获取token
@app.route('/token',methods=['POST'])
def login():
    # 接收来自前端的账号和密码
    # 如果正确 返回token
    username=request.form['username']
    password=request.form['password']
    row=Users.query.filter_by(username=username).first()
    if row == None or row.password != password:
        abort(400)
    # 设置token
    access_token = serializer.dumps({'id':username})
    print(access_token)
    return jsonify({'access_token': access_token.decode('ascii'),'userName':username,'duration': 1800})

@app.route('/api/Account/Logout',methods=['POST'])
def logout():
    # 没想好怎么实现
    # flask可以的return可以返回三个参数 正文、状态码和标头
    return ('',204)


#在访问受保护的资源的时候 会去sessionStorage里面读取accessToken
@auth.verify_token
def verify_token(token):
    g.user = None
    try:
        # 取用户名
        data = serializer.loads(token)
        print(data)
    except:
        return False
    if 'id' in data:
        print(data)
        # 把用户名写入到全局里面去
        g.user = data['id']
        return True
    return False

 # 如果用户名不存在就报错
def abort_if_not_exist(customer_id):
    customer=Customers.query.get(customer_id)
    if customer==None:
        abort(404, message="User {} doesn't exist".format(customer_id))

# 对传入来的参数进行验证
parser = reqparse.RequestParser()
parser.add_argument('customerId', type=int)
parser.add_argument('companyName', type=str)
parser.add_argument('contactName', type=str)
parser.add_argument('phone',type=str)


# 格式化输出 变成json
resource_fields = {
    'customerId':fields.Integer,
    'companyName':fields.String,
    'contactName':fields.String,
    'phone':fields.String
}
#  这些是被保护的资源
@app.route('/api/Values')
@auth.login_required
def protected():
    return jsonify({'sercert':'123456'}),200

# 一个增删改查应用需要两个class才能搞定 一个带参数的一个不带
# 不带参数的提供所有记录查询和记录新增的功能
# 带参数的提供单条记录查询 修改 删除的功能

# 单条记录的操作
class Customer(Resource):
    # 必须登陆才能获取
    decorators = [auth.login_required]
    # 每一个函数都会获取customer_id
    def get(self, customer_id):
        # 如果use_id为空的话 返回404错误
        abort_if_not_exist(customer_id)
        customer=Customers.query.get(customer_id)
        return customer,200
    # 删除
    def delete(self, customer_id):
        abort_if_not_exist(customer_id)
        customer=Customers.query.get(customer_id)
        db.session.delete(customer)
        db.session.commit()
        # 204成功没有资源返回
        return '', 204
    # 修改操作
    def put(self, customer_id):
        abort_if_not_exist(customer_id)
        args = parser.parse_args(strict=True)
        customer=Customers.query.get(customer_id)
        customer.companyName=args['companyName']
        customer.contactName=args['contactName']
        customer.phone=args['phone']
        db.session.commit()
        return '', 201

# 所有记录的操作
class Customerlist(Resource):
    # 查看所有记录
    decorators = [auth.login_required]
    @marshal_with(resource_fields)
    def get(self):
        customers=Customers.query.all()
        return customers,200
    # 新增
    def post(self):
        # 请求中出现未定义的参数，也会返回400错误
        args = parser.parse_args(strict=True)
        # post和put都可以用这种方式读取表单
        new_comstomer=Customers(args['companyName'],args['contactName'],args['phone'])
        db.session.add(new_comstomer)
        db.session.commit()
        return '', 201

# 一个crud对应两个类
api.add_resource(Customerlist, '/api/customers')
api.add_resource(Customer, '/api/customers/<int:customer_id>')
if __name__ == '__main__':
    # 如果没有数据库创建数据库
    if not os.path.exists('api2.sqlite'):
        db.create_all()
    app.run(debug=True)