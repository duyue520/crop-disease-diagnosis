"""
管理员工具 —— 查看用户、重置密码、管理反馈

用法:
    python admin.py              # 交互菜单
    python admin.py users        # 查看所有用户
    python admin.py reset 用户名 新密码   # 重置某用户密码
    python admin.py feedback     # 查看和回复反馈
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ['TORCH_HOME'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weights')

from server.database import SessionLocal, init_db
from server.models.db_models import User, Feedback, DiagnosisRecord
from server.services.auth_service import hash_password

init_db()


def show_users():
    """显示所有注册用户"""
    db = SessionLocal()
    users = db.query(User).order_by(User.id).all()
    print("\n" + "=" * 70)
    print(" 📋 所有注册用户")
    print("=" * 70)
    print(f"{'ID':<5} {'用户名':<20} {'邮箱':<25} {'诊断次数':<8} {'注册时间'}")
    print("-" * 70)
    for u in users:
        count = len(u.diagnoses)
        print(f"{u.id:<5} {u.username:<20} {u.email:<25} {count:<8} {u.created_at.strftime('%Y-%m-%d %H:%M')}")
    print("-" * 70)
    print(f" 共 {len(users)} 个用户")
    db.close()


def reset_password(username, new_password):
    """重置用户密码"""
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f" ❌ 用户 '{username}' 不存在")
        db.close()
        return
    user.hashed_password = hash_password(new_password)
    db.commit()
    print(f" ✅ 用户 '{username}' 的密码已重置为: {new_password}")
    db.close()


def show_feedback():
    """查看反馈"""
    db = SessionLocal()
    feedbacks = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    print("\n" + "=" * 70)
    print(" 📋 用户反馈")
    print("=" * 70)
    for fb in feedbacks:
        user = db.query(User).filter(User.id == fb.user_id).first()
        uname = user.username if user else "未知"
        print(f"\n [{fb.category}] {fb.title}")
        print(f" 来自: {uname} | 时间: {fb.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f" 内容: {fb.content}")
        if fb.reply:
            print(f" ✅ 已回复: {fb.reply}")
        else:
            print(f" ⏳ 待回复")
    print("-" * 70)
    db.close()


def reply_feedback(feedback_id, reply_text):
    """回复反馈"""
    db = SessionLocal()
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        print(f" ❌ 反馈 #{feedback_id} 不存在")
        db.close()
        return
    fb.reply = reply_text
    from datetime import datetime
    fb.replied_at = datetime.utcnow()
    db.commit()
    print(f" ✅ 已回复反馈 #{feedback_id}")
    db.close()


def interactive():
    """交互菜单"""
    while True:
        print("\n" + "=" * 40)
        print(" 🛠️  管理员工具")
        print("=" * 40)
        print(" 1. 查看所有用户")
        print(" 2. 重置用户密码")
        print(" 3. 查看反馈")
        print(" 4. 回复反馈")
        print(" 0. 退出")
        print("=" * 40)
        choice = input(" 请选择: ").strip()

        if choice == '1':
            show_users()
        elif choice == '2':
            uname = input(" 用户名: ").strip()
            pwd = input(" 新密码: ").strip()
            if uname and pwd:
                reset_password(uname, pwd)
        elif choice == '3':
            show_feedback()
        elif choice == '4':
            show_feedback()
            fid = input(" 输入要回复的反馈ID: ").strip()
            reply = input(" 回复内容: ").strip()
            if fid and reply:
                reply_feedback(int(fid), reply)
        elif choice == '0':
            print(" 再见!")
            break
        else:
            print(" 无效选择")
        input("\n 按回车继续...")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == 'users':
            show_users()
        elif cmd == 'reset' and len(sys.argv) >= 4:
            reset_password(sys.argv[2], sys.argv[3])
        elif cmd == 'feedback':
            show_feedback()
        elif cmd == 'reply' and len(sys.argv) >= 4:
            reply_feedback(int(sys.argv[2]), sys.argv[3])
        else:
            print("用法: python admin.py [users|reset 用户名 新密码|feedback|reply 反馈ID 回复内容]")
    else:
        interactive()
