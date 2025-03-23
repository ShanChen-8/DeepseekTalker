from flask import Flask

# 创建Flask应用
app = Flask(__name__)

# 定义路由和函数
@app.route("/")  # 绑定路径 "/" 和下面的 index() 函数
def index():
    return "欢迎来到首页！"

@app.route("/about")  # 绑定路径 "/about" 和下面的 about() 函数
def about():
    return "这是关于页面！"

# 启动Flask应用
if __name__ == "__main__":
    app.run(debug=True)