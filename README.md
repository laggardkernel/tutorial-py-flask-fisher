# 鱼书

慕课网教程：[Python Flask高级编程](https://coding.imooc.com/class/194.html)
- 七月老师又一力作，带你迈入Python高级编程
- [教程成品展示](http://yushu.im/)

本教程使用作者所提供API，学习完后有必要改为豆瓣API，二者格式基本兼容。

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

## Chap 04
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

## Chap 05
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
