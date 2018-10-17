# 鱼书

慕课网教程：[Python Flask高级编程](https://coding.imooc.com/class/194.html)
- 七月老师又一力作，带你迈入Python高级编程
- [教程成品展示](http://yushu.im/)

本教程使用作者所提供API，学习完后有必要改为豆瓣API，二者格式基本兼容。

个人评价：
- 的确讲了些Flask底层实现，但是并不是带你逐行读代码。重点在于Python高级应用和Flask原理知识。
- 关于线程隔离部分废话太多，把`1+1`都讲一遍，有必要吗？
- Jinja2模板语言讲解的受众是完全没有用过Jinja2的新手，这种基础知识不应该放到高级课程里面来
    - 过滤器也被称作高级使用技巧？！
- 总结：勉强算是高级课程

## Chap 3
API测试

```
http GET http://t.yushu.im/v2/book/isbn/9787501524044
```

逻辑组合判断的循序很重要，其尽量将高耗时查询放到后边。
视图函数代码不要太长，方便理解。
源代码阅读要分层去看，之后再查看详细实现细节，先理清代码结构、功能。

简化条件判断长度：
- `statement if ... else...`
- `if`非对称，后边继续return

`@staticmethod`, `@classmethod`
- 使用`cls`时采用`@classmethod`
- 将方法封装到`staticmethod`中方便扩展

关键词上键入`Alt+Enter`在PyCharm中自动导入。

端点调试时关闭`DEBUG`，debug模式存在两次启动。

endpoint有助于反向构建URL。即函数对应的URL。
`url_map` Map中存储URL到端点函数的关联信息，`view_functions`记录函数名到函数对象的关联信息。

![img/0301.jpg](../assets/img/0301.jpg?raw=true)

Python导入时，同一个模块只会被导入一次。

## Chap 4
Blueprint不是用于分拆route定义，而是用于分拆功能。

获取查询参数：
- `count = request.args.get('count', 15, type=int)`
- `request.args.to_ditct()`

利用Form验证查询参数，`form = SearchFrom(request.args)`。直接使用`WTForms`，继承自`Form`类。`Flask-WTF`中`FlaskForm`存在csrf_token验证。

是否封装为函数不是根据代码量来判断，而是根据其功能。

数据表创建方式
- db first
- model first
- code first
    - 关注业务模型的设计，而不是数据库设计。

面试问题：业务逻辑应该写在MVC中哪一层？
最好在Model模型层内。

## Chap 5
`F12`在PyCharm中查看源代码。`Ctrl+Alt+Left`向外层跳转出来。

`LocalProxy`与Flask上下文

application context, request context. 上下文本质上是一个对象，分别是对于`Flask`和`Request`的封装。分别存储于源码中的`AppContext`和`RequestContext`对象中。

在上下文中绑定了额外的外部参数、对象，而不是属于对象本身。

使用时请求上下文对象中间接访问、获取`Flask`, `Request`相关对象。`LocalProxy`提供了其间接接触二者的能力。

注：作者使用了[Process On](https://processon.com/)作流程图。

![img/0501.jpg](../assets/img/0501.jpg?raw=true)

在`RequestContext`对象入栈之前，会先检查`AppContext`是否为空。若其为空，先推入`AppContext`入栈。

**`current_app`, `request`本地代理永远指向其对应的栈顶**。若栈顶为空，则会出现`Not Found`、`Working outside application context`错误。所以，测试代码时先推送上下文`app.app_context.push()`，因为其**未在一个请求中使用**。（离线应用、单元测试）
- `with app.app_context():`

`current_app`, `request`最终获得的是真正对象，而不是上下文对象，实际在上下文中寻找栈属性。见`globals.py`。

`with`语句实现：
- `__enter__`，返回值赋值给`as`后对象。
- `__exit__`，释放资源，处理异常。
- `with`语句实现了类似`try...except`释放资源。

```python
    # exc_value: 异常信息
    # tb: traceback
    def __exit__(self, exc_type, exc_value, tb):
        ...
        return True
        # return False # 在外部再次抛出异常
        # return None # equivalent to False
```

防御性编程？默认参数。`dict.setdefault(key, value)`

建议：**看源代码分析问题**。

## Chap 6: Flask中的多线程与线程隔离技术
进程
计算机资源时稀缺的，应用竞争操作系统的资源。进程是计算机竞争计算机资源的基本单位。

进程调度：在不同应用程序进程之间切换。（参考书籍：《操作系统原理》相关书籍）
进程调度对于系统开销时非常大的，保存、恢复相关上下文耗时。

线程
线程是进程的一部分。进程管理资源粒度太大，引入更小的CPU资源。线程切换时开销相对进程小。
进程分配资源，线程利用CPU执行代码。线程本身不能管理或拥有资源，但可访问进程的资源。（Python不是有全局线程锁吗？）

多线程
主线程启动子线程，线程默认不是顺序执行。多线程编程更加充分地应用CPU的性能优势，防止阻断执行。多线程编程也是异步编程的一种形态。

作者的话：不要盲目崇拜异步编程，异步编程的管理、维护、调试成本是非常的大。同步解决不了的问题再换异步编程。

Python全局解释器锁GIL，导致Python多线程最多可以利用一个核。
多个线程共享进程的资源，从而存在线程不安全。锁，锁定资源仅当前线程所用。
细粒度的锁，主动在程序中加锁。粗粒度锁，在Python解释器上加锁，即GIL。Python解释器上只允许占用CPU。

GIL只在一定程度上保证了线程安全，因为程序执行存在更小单位bytecode。GIL全局解释器锁只存在于CPython解释器。

多进程管理的资源之间互相不能访问，共享变量需要设计进程通信技术。且进程之间切换成本较线程切换大。

对IO密集型，单CPU多线程也是有意义的。
常见IO操作：数据库查询、网络资源请求、文档读写。
- Web应用查询瓶颈更多时候还是在数据库查询上。
- 主要时间用于等待。多线程可以削减等待时间。
- NodeJS也是只适用于IO密集型程序。

Flask多线程
Flask多线程是由webserver开启的。Flask存在内置webserver，默认启动单进程单线程模式。

```python
app.run(..., threaded=True)
# flask run --with-threads
```

**注**：
- 根据查询[Builtin Configuration Values](http://flask.pocoo.org/docs/1.0/config/#builtin-configuration-values)，不存在`threaded=True`对应的环境变量。
- PyCharm新版可以调试多线程，Frame中。

客户端请求与处理请求的线程
每个请求信息存储在`Request`实例中，多线程时需要一种方案，利用`request`对应不同请求`Request`实例。

线程隔离
- dict，多线程唯一标识（线程ID）作为字典键。

作者的话：框架复杂不在于原理，而在于其要考虑全面。

`werkzeug.local`模块下`Local`对象，利用字典实现线程隔离，以线程ID作为键。（不是有`threading.local()`吗？）

`_request_ctx_stack`, `_app_ctx_stack`均为`werkzeug`中`LocalStack`实例，基于`werkzeug.local.Local`封装实现的站结构。

作者的话：多次封装。

`LocalStack`使用，`.push()`, `.pop()`, `.top`。（`werkzueg.local.LocalStack`）


使用线程隔离的意义在于：使当前线程正确引用到他自己所创建的对象，而不是引用到其他线程所创建的对象。（MD这章这么多废话，就是为了将这玩意儿？这不废话嘛。主要还是为了把请求等相关对象绑定在线程隔离对象上作为属性，也变成隔离：**被线程隔离的对象**）

`setattr()`, `getattr()`.

`app` Flask核心对象只有一个。`current_app`不能成为线程隔离对象。
- `app`绑定数据可以作为全局，但是存在线程安全问题。

总结：
- `werkzeug.local.Local`是以线程ID作为字典键实现，`werkzeug.local.LocalStack`是基于`Local`实现的栈类。
- `AppContext`, `RequestContext`上下文类基于`LocalStack`类实现。`Flask`实例/核心对象作为`AppContext`实例属性被保存。`Request`实例被作为`RequestContext`实例属性保存。
- `current_app`指向栈顶`AppContext.top.app`，即`Flask`核心对象，`request`指向`RequestContext.top.request`属性，`Request`实例。

## Chap 7: 书籍详情页面的构建
页面需求可能和原始数据不对应，`ViewModel`对原始数据进行转换：
- 裁剪
- 修饰
- 合并

![img/0701.jpg](../assets/img/0701.jpg?raw=true)

作者建议：要不要处理列表为字符串？前后端分离可以直接交给前端，模板渲染建议直接转换好。

对单项数据编写处理函数，对于多项数据（列表）**复用**单项数据处理函数。

一个类应该具有描述特征（类变量、实例变量）和行为（方法）两部分，只有后面的方法而没有变量，其实还是在面向过程（伪面向对象）。
- 一个类中大量staticmethod或者classmethod，可能此类就是面向过程

`__dict__`函数返回对象的字典。

![img/0702.jpg](../assets/img/0702.jpg?raw=true)

函数式编程思维，将代码解释权交给调用方。`json.dumps(books, default=lambda o:o.__dict__)`。

> If specified, *default* should be a function that gets called for objects that can’t otherwise be serialized. It should return a JSON encodable version of the object or raise a `TypeError`. If not specified, `TypeError` is raised. 即`default`在对象不能被序列化时调用，作为别用序列化方案。

作者建议：团队合作时，不要过于关注页面，而关注视图函数的返回，不管是API而是网站。

返回数据中
- Javascript、 CSS、图片属于静态文件，因其不需要被填充，不需要加工。
- 普通网站页面渲染由服务器
- 单页面网站，数据渲染交给客户端，由JavaScript实现

![img/0703.jpg](../assets/img/0703.jpg?raw=true)

问题：单页面和多页面网站的主要区别？
- 渲染，前者在客户端，后者在服务端
- 业务逻辑/渲染，前者交由JavaScript，后者交由视图函数
    - 前端框架AngularJS、Vue就具备前端业务能力：数据填充、模板渲染能力

## Chap 8: Jinja2模板语言
本章节过于基础，配不上高级编程的课程名字。

### 静态文件
静态文件默认设置，静态文件夹位于应用根目录下`static/`文件夹，应用程序根目录基于`Flask(__name__)`。查看`_get_static_url_path`函数可知，URL取路径最后一部分。

```python
app = Flask(__name__, static_folder='')
# static_url_path='' 指定静态文件夹URL值
```

静态文件同样有2个层级：应用程序级别的静态文件，和蓝图层级的静态文件。（蓝图`Blueprint`类相关方法基本复制了Flask API）

```
web = Blueprint('web', __name__, static_foler='', static_url_path='')
```

`send_static_file()`函数负责读取返回静态文件。可以**包装`send_static_file()`做积分限制下载文件。**

### 模板渲染
```python
render_template('template_name', key1=value1, key2=value2)

context = {
    'key1': value1,
    'key2': value2
}
render_template('template_name', **context)
```

指定模板文件夹位置，分离模板到蓝图。

```python
app = Flask(__name__, template_folder='')
web = Blueprint('web', __name__, template_folder='')
```

作者建议：
- 模板文件夹可以分离，静态文件夹推荐只使用应用级别一个文件夹，因为通常静态文件会被各个蓝图共享使用。
- 模板未找到的错误提示较常见，不必在意。解决方案是，**在Pycharm标记对应文件夹为`templates`文件夹**。

### 模板语言
Pycharm中模板语言可以设置。

Jinja2 文档中重点学习**Template Designer Documentation**.

这部分太基础，本人已经读过[Jinja2文档](http://jinja.pocoo.org/docs/2.10/)，此节可以略过。

过滤器：
- `default('value')`
- `length()`

反向解析URL
- `url_for`通过endpoint机制反向构建URL
- `{{ url_for('static', filename='custom.css') }}`

`flash('message', category='message')`
- 分类：`error`，`warning`

```html
{% set messages = get_flashed_messages() %}
{% for message in messages %}

{% endfor %}

{% set messages = get_flashed_messages(category_filter=['error','warning']) %}
```

Flask中的session会话是存储在客户端的。

模板语言中`set`和`with`区别在于，`with`有显示作用域限制，`set`使用默认作用域范围——一个模板块内。

## Chap 9: 用户登录与注册
Jinja2过滤器`default(value, default_value=u'', boolean=False)`
- `boolean=True`参数使得在求值为False时也使用默认值。

在模板语言中拼接字段较为复杂，因为存在字段为空判断的问题。模板中拼接字段可以放到view_models中。

```html
<span>{{ [book.author | d(''), book.publisher | d('', true) , '￥' + book.price | d('')] | join(' / ') }}</span>
```


```python
class BookViewModel(object):
   # ...

    @property
    def intro(self):
        intro = filter(
            lambda x: True if x else False, [self.author, self.publisher, self.price]
        )
        return " / ".join(intro)
```

书籍详情页面，赠送、请求书籍业务逻辑。

![img/0901.jpg](../assets/img/0901.jpg?raw=true)


利用抽象基类定义一些共有属性，如激活状态表示软删除。

```python
class Base(db.Model):
    __abstract__ = True # No table creation
    # soft deletion
    status = db.Column(db.SmallInteger, default=1)
```

动态赋值

```python
    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key not in ["id"]:
                setattr(self, key, value)
```

`@property`设置只写属性password（这TMD不是常识吗？）

```python
    password_hash = db.Column("password", db.String(128))

    @property
    def password(self):
        raise AttributeError("password is a write-only attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
```

cookie更多地应用于精准广告投放。默认机制是，网站拿到自己网站相关cookie.
- TODO: 了解跨网站cookie共享

![img/0902.jpg](../assets/img/0902.jpg?raw=true)

[Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- 写入用户票据，写入用户ID
- `get_id`等类用户函数定义可以通过直接继承`UserMixin`省去继承的麻烦。
- `login_manager.user_loader`返回用户
- `login_rewquired`装饰器限制权限

中间Flask-Login使用介绍全是废话，这不就是其Document基本内容吗。

flask-login 模块结构

![img/0903.jpg](../assets/img/0903.jpg?raw=true)


非法重定向：如登录后重定向至钓鱼网站。

疑难：`hasattr(user, 'password')` returns `False`. `hasattr(User, 'password')`, `hasattr(user, 'password')`表现不同。

参考
- [hasattr实现调用getattr](https://stackoverflow.com/questions/30143957/why-does-hasattr-execute-the-property-decorator-code-block/55118101#55118101)
- [Why does hasattr behave differently on classes and instances with @property method?](https://stackoverflow.com/questions/55118728/why-does-hasattr-behave-differently-on-classes-and-instances-with-property-meth)

目前看来，实例（仅限实例）调用`getattr`会先调用`hasattr`，由于此时会执行`property`方法，只写属性方法抛出异常。在类上调用`getattr`实际只会判断类有没有此方法，而不必去执行此方法，故不会抛出异常，返回属性对象。可以使用`.__class__`使二者表现一致。

```python
class User(Base, UserMixin):
    @property
    def password(self):
        raise AttributeError("password is a read-only attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

hasattr(User, 'password')
# True

u1=User()
hasattr(u1, 'password')
# False
```

## Chap 10: 书籍交易模型
事务
- `db.session.commit()`, `db.session.rollback()`
- `contextmanager`装饰器免去`__enter__`, `__exit__`类方法定义

```python
try:
    # db operations
    db.session.commit()
except Exception as e:
    db.session.rollback()
    raise e
```

```python
class MyResource:
    def query(self):
        print('query data')

from contextlib import contextmanager

@contextmanager
def make_myresourse():
    print('connect to resource') # equivalent to __enter__
    yield MyResource() # 中断
    print('close resource connection') # equivalent to __exit__

with make_myresource() as r:
    r.query()
```

作者：实际上`contextmanager`可能反而复杂了原有写法（并非简化了原有的定义）。但其优势是不需要操作原有类（引用的库）。

Tips:
- 学习知识本身时，独立文件做示例
- 高级编程并不是指学习高级语法，而是运用其写出好的代码（知识综合应用）
- 写不出高级代码很正常，多模仿，多看优秀框架源码

数据库记录条目创建时间，类构造函数赋当前时间。（为嘛不用`default`）
此处作者使用**错误**，`default`赋值函数名`datatime.utcnow`, 而不是执行函数返回其结果。

Ajax
- 避免重定向回到当前页面
- 减少不必要的渲染，从而改善服务器性能

![img/1001.jpg](../assets/img/1001.jpg?raw=true)

最消耗页面性能的部分在于**模板渲染**。解决方案：缓存为静态页面。

MVC v.s. MVT
- Model, View, Controller
- Model, Template,

**业务逻辑**应该写在`MVC`中Model层，即作为模型层方法。模型层和数据层（ORM已经涵盖了数据层）。另外，数据层还可以进一步分层，如分为服务Service层和逻辑Logic层。但实际中，控制层也会写业务逻辑。模型层不等价于数据层，ORM已经完成了数据层统一接口封装。

**重写基类实现自定义业务逻辑**

查询时，注意查询数据状态，如是否被软删除。自定义`filter_by`，默认只查询非软删除数据。

先搞清继承关系：`query`对象`BaseQuery`(flask-sqlalchemy), 继承自`orm.Query`, sqlalchemy `Query`下`filter_by`方法。自定义`Query`类继承`BaseQuery`，重写`filter_by`逻辑。

```python
class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        # 是否返回对象，查看父类中方法
        return super().filter_by(**kwargs)

db = SQLAlchemy(query_class=Query)
```

再查询`SQLAlchemy`源码，发现`flask_sqlalchemy/__init__.py`中`__init__`构造函数可以传参`query_class`.

Datetime 字符串转换为 datetime类型，吃饱撑的？直接定义模型时使用`db.Datetime`不就完了。

## 教程错误总结
Model中`default`参数使用错误，记录默认时间传递函数对象，即不带括号执行函数。

时间记录、显示没有考虑时区，解决方法：`datetime.utcnow()`， `Flask-Moment`应用。

数据类型转换，教程中使用ViewModel自定义类型转换。生产中已经有较好的解决方案[marshmallow: simplified object serialization](https://marshmallow.readthedocs.io/en/latest/index.html)