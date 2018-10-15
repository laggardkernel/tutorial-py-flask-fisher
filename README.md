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

## Chap 7
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
