1. 尝试直接在本地创建 yaml 文件并设置 py 文件与之关联。
    - 但是上传代码后 actions 列表中没有任何内容
2. 通过 GitHub 引导创建一个 yaml 文件后 actions 中成功出现合法 action
    - pull 到本地， 删除 GitHub 创建的 yaml 再次 push ， 观察到 actions 列表中的 actions 并没有消失
    - 恢复刚删除的 yaml 文件
    - 拷贝一个副本， 修改 yaml 中关于 action 命名代码， 执行 push
        - 重新点击 Actions 标签， 即可看到新的 action
3. 所以接下来我们需要了解语法细节了，因为自托管的 action ，没有出现在 Actions 列表中，也没有执行