# coding=utf-8
"""
同步服务 API 视图

提供 bookmarks 资源组的 pull/push 接口
"""
from datetime import datetime
from flask import request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_

from . import bp
from .models import BookmarkResource
from app.db import db


@bp.route('/bookmarks/pull', methods=['GET'])
@login_required
def bookmarks_pull():
    """
    拉取 bookmarks 资源组增量
    
    请求参数：
    - last_sync_time: 上次同步时间戳（ISO 格式或 0）
    
    返回：
    - changes: 增量变更列表
    - latest_sync_time: 本次同步的最新时间戳
    """
    # 1. 获取并解析 last_sync_time
    last_sync_time_str = request.args.get('last_sync_time', '0')
    
    if last_sync_time_str == '0' or not last_sync_time_str:
        # 首次同步，从最早时间开始
        last_sync_time = datetime.min
    else:
        try:
            # 解析 ISO 格式时间戳
            last_sync_time = datetime.fromisoformat(last_sync_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid last_sync_time format'}), 400
    
    # 2. 查询增量数据
    records = BookmarkResource.query.filter(
        and_(
            BookmarkResource.user_id == current_user.id,
            BookmarkResource.updated_at > last_sync_time
        )
    ).order_by(BookmarkResource.updated_at.asc()).all()
    
    # 3. 构造响应
    changes = [record.to_dict() for record in records]
    
    # 计算 latest_sync_time
    if records:
        latest_sync_time = max(r.updated_at for r in records).isoformat()
    else:
        # 没有新数据，回传原时间
        latest_sync_time = last_sync_time_str if last_sync_time_str != '0' else None
    
    return jsonify({
        'changes': changes,
        'latest_sync_time': latest_sync_time
    })


@bp.route('/bookmarks/push', methods=['POST'])
@login_required
def bookmarks_push():
    """
    上传 bookmarks 资源组变更
    
    请求体：
    - changes: 变更列表，每条包含 resource_id, op, payload, created_at, updated_at, deleted_at
    
    返回：
    - applied: 成功应用的 resource_id 列表
    - failed: 失败的条目及原因
    """
    data = request.get_json()
    if not data or 'changes' not in data:
        return jsonify({'error': 'Missing changes field'}), 400
    
    changes = data['changes']
    applied = []
    failed = []
    
    try:
        for change in changes:
            resource_id = change.get('resource_id')
            op = change.get('op')
            payload = change.get('payload')
            
            # 解析时间戳
            try:
                created_at = datetime.fromisoformat(change.get('created_at', '').replace('Z', '+00:00')) if change.get('created_at') else datetime.utcnow()
                updated_at = datetime.fromisoformat(change.get('updated_at', '').replace('Z', '+00:00')) if change.get('updated_at') else datetime.utcnow()
                deleted_at_str = change.get('deleted_at')
                deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00')) if deleted_at_str else None
            except (ValueError, AttributeError) as e:
                failed.append({'resource_id': resource_id, 'reason': f'invalid_timestamp: {str(e)}'})
                continue
            
            # 查找现有记录
            record = BookmarkResource.query.filter_by(
                user_id=current_user.id,
                resource_id=resource_id
            ).first()
            
            if not record:
                # 新建记录
                record = BookmarkResource(
                    user_id=current_user.id,
                    resource_id=resource_id,
                    payload=payload or {},
                    created_at=created_at,
                    updated_at=updated_at,
                    deleted_at=deleted_at
                )
                db.session.add(record)
                applied.append(resource_id)
            else:
                # 更新现有记录
                if op == 'upsert':
                    record.payload = payload
                    record.updated_at = updated_at
                    record.deleted_at = None
                    if not record.created_at:
                        record.created_at = created_at
                    applied.append(resource_id)
                elif op == 'delete':
                    record.deleted_at = deleted_at
                    record.updated_at = updated_at
                    applied.append(resource_id)
                else:
                    failed.append({'resource_id': resource_id, 'reason': f'unknown_op: {op}'})
        
        # 统一提交
        db.session.commit()
        
        return jsonify({
            'applied': applied,
            'failed': failed
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
