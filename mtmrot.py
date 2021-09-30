from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mtmrot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 關聯表，左側的 user 正在關注右側的 user
association_table_follow = db.Table("association_table_follow",
            db.Column("follower_id", db.Integer, db.ForeignKey("user.id")), # 左側
            db.Column("followed_id", db.Integer, db.ForeignKey("user.id"))  # 右側
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # 建立好 association_table_follow 這個 Table 後，需要把 association_table_follow 和 User 做聯接，故須在這邊添加 relationship
    # followed 意思為 User 關注了誰
    # 也就是說，當使用 User.followed 只的是，顯示 User 關注了哪些人
    followed = db.relationship(
        # 從 User 要往誰去連？要連去另一個 User 所以下面也是 "User"
        "User", secondary=association_table_follow,
        primaryjoin=(association_table_follow.c.follower_id == id),
        secondaryjoin=(association_table_follow.c.followed_id == id),
        backref=db.backref('followers', lazy=True), lazy=True
        # 因為 backref 是 followers，意思為 User 有哪些追隨者
        # 也就是說，當使用 User.followers 只的是，顯示 User 的追隨者有哪些人
    )

# 到 python3 shell 進行測試：讓 u1 追隨 u2
# >>> from app.models import db
# >>> db.create_all()                                  # 更新資料庫結構
# >>> from app.models import User
# >>> u1 = User(username='0001')                       # 新建測試用 u1
# >>> u2 = User(username='0002')                       # 新建測試用 u2
# >>> db.session.add(u1)
# >>> db.session.add(u2)
# >>> db.session.commit()


# >>> u1.followed                                      # 查看 u1 追隨哪些人
# []                                                   # 空
# >>> u1.follower                                      # 查看 u1 被誰追隨
# []                                                   # 空

# >>> u1.followed.append(u2)                           # 使用 append() 讓 u1 追隨 u2 
# >>> u1.followed                                      # 再次查看 u1 追隨哪些人
# [<User 'u2'>]                                        # u1 追隨了 u2
# >>> u2.followers                                     # 查看 u2 被誰追隨
# [<User 'u1'>]                                        # u2 被 u1 追隨
# 只在 u1 做 append() 修改，但可以發現 u2 的資料也發生了改變

# 查看資料庫表格變化
# >>> db.session.commit()
# 可以看到
#
# follower_id   followed_id
#           1             2
#
# 符合上述：關聯表，左側的 user 正在關注右側的 user

# >>> u1.followed.remove(u2)                           # 使用 remove() 讓 u1 取消追隨 u2
# >>> u1.followed                                      # 再次查看 u1 追誰哪些人 
# []                                                   # 空
# >>> u2.followers                                     # 查看 u2 被誰追隨
# []                                                   # 空
