from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

# -----------------------------
# MODELOS USER
# -----------------------------

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120))
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow, nullable=False)

    # relaciones 1-a-N
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # relaciones N-a-N 
    followers: Mapped[list["Follow"]] = relationship(
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan",
    )
    following: Mapped[list["Follow"]] = relationship(
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

# -----------------------------
# MODELOS POSTS
# -----------------------------

class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow, nullable=False)

    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

# -----------------------------
# MODELOS COMMENTS
# -----------------------------

class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow, nullable=False)

    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")

    # ejemplo de restricción adicional (opcional)
    __table_args__ = (
        # Evitar duplicar el mismo id por post (ilustrativo)
        UniqueConstraint("id", "post_id", name="uq_comment_per_post"),
    )

# -----------------------------
# MODELOS LIKES
# -----------------------------


class Like(db.Model):
    """
    Tabla de asociación con PK compuesta:
    - Un usuario solo puede dar 1 like por post.
    """
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["Post"] = relationship(back_populates="likes")


# -----------------------------
# MODELOS FOLLOWS
# -----------------------------

class Follow(db.Model):
    """
    Self-join N-a-N: relaciones de seguimiento entre usuarios.
    PK compuesta evita que una pareja se repita.
    """
    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow, nullable=False)

    follower: Mapped["User"] = relationship(
        foreign_keys=[follower_id], back_populates="following"
    )
    followed: Mapped["User"] = relationship(
        foreign_keys=[followed_id], back_populates="followers"
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "followed_id", name="uq_follow_once"),
    )

# -----------------------------
# DIAGRAMA
# -----------------------------
if __name__ == "__main__":
    try:
        from eralchemy2 import render_er
        render_er(db.Model, "diagram.png")
        print("✅ diagrama generado en diagram.png")
    except Exception as e:
        print("⚠️ No se pudo generar el diagrama:", e)
