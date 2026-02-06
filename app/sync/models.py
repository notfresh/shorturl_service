# coding=utf-8
"""
同步服务数据模型
"""
from datetime import datetime
from app.db import db


class BookmarkResource(db.Model):
    """
    Bookmarks 资源组通用存储表
    
    字段说明：
    - resource_id: 客户端自定义的稳定 ID（UUID）
    - payload: 完整的 bookmark 聚合体（书签字段、tag 列表等）序列化为 JSON
    - created_at/updated_at/deleted_at: 客户端提供的时间戳，服务端直接接受
    - deleted_at 为空表示有效，非空表示软删
    """
    __tablename__ = 'bookmark_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.String(64), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource_id', name='uq_user_resource'),
        db.Index('idx_user_updated', 'user_id', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<BookmarkResource {self.resource_id} user={self.user_id}>"
    
    def to_dict(self):
        """转换为 API 响应格式"""
        return {
            'resource_id': self.resource_id,
            'op': 'delete' if self.deleted_at else 'upsert',
            'payload': self.payload if not self.deleted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }
