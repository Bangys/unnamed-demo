## bbs system

###页面部分
- 首页 index
- 文章详情页 detail
- 文章编辑页 edit
- 个人页 profile

### 数据模型

- 文章 post: content, user, ct, mt, 
- 用户 user: name, email, passwd, avatar
- 评论 comment:content, user_id, post_id

### 主要逻辑
- 首页获取全部文章页
- 在文章编辑页点击提交
- 编辑文章
- 删除文章

