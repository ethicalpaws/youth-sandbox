# git


>💡 新手必记的 6 个核心指令
>如果只记 6 个，记这些就能完成 90% 的日常操作：

```bash
git status              # 看状态
git add .               # 加暂存
git commit -m "msg"     # 提交
git pull                # 拉更新
git push                # 推远程
git log --oneline       # 看历史
```

## 一、 仓库创建与克隆
指令	说明
git init	在当前目录初始化一个新的 Git 仓库（生成 .git 文件夹）
git clone <url>	克隆远程仓库到本地
git clone <url> <folder>	克隆到指定文件夹

## 二、 日常提交（最常用）
指令	说明
git status	查看当前状态（哪些文件被修改、暂存、未跟踪）
git add <file>	将指定文件添加到暂存区
git add .	添加所有修改和新文件到暂存区
git commit -m "msg"	提交暂存区内容，msg 为提交说明
git commit -am "msg"	（快捷） 添加已跟踪文件的修改并提交（不含新文件）
git commit --amend	修改最近一次提交（常用于修改 commit message 或补漏文件）

## 三、 查看历史与差异
指令	说明
git log	查看提交历史
git log --oneline	（推荐） 单行简洁显示历史
git log --graph --oneline --all	图形化显示所有分支历史
git diff	查看工作区与暂存区的差异
git diff --staged	查看暂存区与最后一次提交的差异
git show <commit>	查看某次提交的具体修改内容

## 四、 分支管理
指令	说明
git branch	查看本地分支
git branch -a	查看所有分支（含远程）
git branch <name>	创建新分支
git checkout <branch>	切换分支
git checkout -b <branch>	（常用） 创建并切换到新分支
git switch <branch>	切换分支（Git 2.23+ 新指令，更语义化）
git switch -c <branch>	创建并切换分支（新指令）
git merge <branch>	将指定分支合并到当前分支
git branch -d <branch>	删除已合并的分支
git branch -D <branch>	强制删除分支（未合并也删）

## 五、 远程协作
指令	说明
git remote -v	查看远程仓库地址
git remote add origin <url>	添加远程仓库
git pull	拉取远程更新并合并到本地
git pull --rebase	拉取远程更新并以变基方式合并（历史更整洁）
git push	推送本地提交到远程
git push -u origin <branch>	首次推送并建立追踪关系
git push origin --delete <branch>	删除远程分支

## 六、 撤销与回退（高危操作，慎用）
指令	说明
git restore <file>	撤销工作区的修改（Git 2.23+）
git restore --staged <file>	将文件从暂存区撤回到工作区
git reset --soft HEAD~1	撤销最近一次 commit，保留修改在暂存区
git reset --mixed HEAD~1	撤销最近一次 commit，保留修改在工作区（默认）
git reset --hard HEAD~1	（危险） 撤销最近一次 commit，丢弃所有修改
git revert <commit>	（安全） 创建一个新 commit 来抵消指定 commit 的修改

## 七、 暂存工作区（临时切换任务）
指令	说明
git stash	保存当前工作区修改，回到干净状态
git stash list	查看 stash 列表
git stash pop	恢复最近的 stash 并删除该记录
git stash apply	恢复最近的 stash 但保留记录

## 八、 标签
指令	说明
git tag	查看所有标签
git tag v1.0	创建轻量标签
git tag -a v1.0 -m "msg"	创建附注标签
git push origin v1.0	推送标签到远程
git push origin --tags	推送所有标签

