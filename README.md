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

