"""Task management routes: CRUD, bulk ops, comments, attachments."""
import os
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import (
    db, Task, Activity, TaskComment, Attachment, User,
    TASK_STATUSES, PLAN_ACTUAL_CHOICES
)
from auth_utils import (
    require_permission, require_roles, log_audit,
    get_current_user, create_notification
)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/v1')


def parse_date(date_str):
    """Parse dd/mm/yyyy or yyyy-mm-dd date string."""
    if not date_str:
        return None
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', set())


# ── Task CRUD ───────────────────────────────────────────────────

@tasks_bp.get('/activities/<string:act_id>/tasks')
@jwt_required()
def list_tasks(act_id):
    user = get_current_user()
    query = Task.query.filter_by(activity_id=act_id, is_deleted=False)

    # Filter by status
    status = request.args.get('status')
    if status and status in TASK_STATUSES:
        query = query.filter_by(status=status)

    # Filter by plan_actual
    plan_actual = request.args.get('plan_actual')
    if plan_actual and plan_actual in PLAN_ACTUAL_CHOICES:
        query = query.filter_by(plan_actual=plan_actual)

    # Filter by responsible
    responsible_id = request.args.get('responsible_id')
    if responsible_id:
        query = query.filter_by(responsible_id=responsible_id)

    # Implementers only see own tasks (unless they also have Viewer/Admin/ME roles)
    if (user.has_role('Implementer')
            and not user.has_role('Admin')
            and not user.has_role('ME_Specialist')
            and not user.has_role('Viewer')
            and not user.has_role('Budget_Holder')):
        query = query.filter_by(responsible_id=user.id)

    tasks = query.order_by(Task.start_date).all()
    return jsonify({'data': [t.to_dict() for t in tasks]}), 200


@tasks_bp.post('/activities/<string:act_id>/tasks')
@jwt_required()
def create_task(act_id):
    user = get_current_user()
    if not user.has_permission('task', 'create'):
        return jsonify({'error': 'Insufficient permissions'}), 403

    activity = Activity.query.get_or_404(act_id)

    # Budget holders can only create under own portfolio
    if user.has_role('Budget_Holder') and not user.has_role('Admin') and not user.has_role('ME_Specialist'):
        if activity.budget_holder_id != user.budget_holder_id:
            return jsonify({'error': 'Cannot create tasks outside your portfolio'}), 403

    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Task name is required'}), 400

    start_date = parse_date(data.get('start_date'))
    end_date = parse_date(data.get('end_date'))

    if not start_date or not end_date:
        return jsonify({'error': 'Valid start_date and end_date required (dd/mm/yyyy)'}), 400

    if end_date < start_date:
        return jsonify({'error': 'end_date must be >= start_date'}), 400

    plan_actual = data.get('plan_actual', 'Planned')
    if plan_actual not in PLAN_ACTUAL_CHOICES:
        return jsonify({'error': f'plan_actual must be one of: {PLAN_ACTUAL_CHOICES}'}), 400

    status = data.get('status', 'Pending')
    if status not in TASK_STATUSES:
        return jsonify({'error': f'status must be one of: {TASK_STATUSES}'}), 400

    # Complete requires evidence or end_date
    if status == 'Complete' and not data.get('completion_evidence') and not end_date:
        return jsonify({'error': 'Status "Complete" requires completion evidence or an end date'}), 400

    task = Task(
        activity_id=act_id,
        name=data['name'].strip(),
        responsible_id=data.get('responsible_id'),
        responsible_person=data.get('responsible_person'),
        plan_actual=plan_actual,
        start_date=start_date,
        end_date=end_date,
        status=status,
        completion_evidence=data.get('completion_evidence'),
        created_by=user.id,
    )
    db.session.add(task)
    db.session.flush()
    log_audit(user.id, 'task', task.id, 'create')

    # Notify responsible person
    if task.responsible_id and task.responsible_id != user.id:
        create_notification(
            task.responsible_id, 'task_assigned',
            f'You have been assigned: {task.name}',
            body=f'Activity: {activity.code} - {activity.description}',
            ref_type='task', ref_id=task.id,
        )

    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.get('/tasks/<string:task_id>')
@jwt_required()
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = task.to_dict()
    data['comments'] = [c.to_dict() for c in
                        task.comments.filter_by(is_deleted=False, parent_comment_id=None)
                        .order_by(TaskComment.created_at).all()]
    data['attachments'] = [a.to_dict() for a in task.attachments.all()]
    return jsonify(data), 200


@tasks_bp.put('/tasks/<string:task_id>')
@jwt_required()
def update_task(task_id):
    user = get_current_user()
    task = Task.query.get_or_404(task_id)

    # Check permissions
    if not user.has_permission('task', 'update'):
        return jsonify({'error': 'Insufficient permissions'}), 403

    # Implementers can only update own tasks
    if user.has_role('Implementer') and not user.has_role('Admin') and not user.has_role('ME_Specialist'):
        if task.responsible_id != user.id:
            return jsonify({'error': 'Can only update your own tasks'}), 403

    data = request.get_json()
    changes = {}

    # Update simple fields
    for field in ('name', 'responsible_id', 'responsible_person', 'plan_actual', 'status', 'completion_evidence'):
        if field in data and getattr(task, field) != data[field]:
            # Validate
            if field == 'plan_actual' and data[field] not in PLAN_ACTUAL_CHOICES:
                return jsonify({'error': f'Invalid plan_actual value'}), 400
            if field == 'status' and data[field] not in TASK_STATUSES:
                return jsonify({'error': f'Invalid status value'}), 400

            changes[field] = {'old': str(getattr(task, field)), 'new': str(data[field])}
            setattr(task, field, data[field])

    # Update dates
    for date_field in ('start_date', 'end_date'):
        if date_field in data:
            new_date = parse_date(data[date_field])
            if new_date and getattr(task, date_field) != new_date:
                changes[date_field] = {
                    'old': getattr(task, date_field).isoformat() if getattr(task, date_field) else None,
                    'new': new_date.isoformat()
                }
                setattr(task, date_field, new_date)

    # Validate dates
    if task.end_date < task.start_date:
        return jsonify({'error': 'end_date must be >= start_date'}), 400

    # Complete validation
    if task.status == 'Complete' and not task.completion_evidence and not task.end_date:
        return jsonify({'error': 'Complete requires evidence or end_date'}), 400

    if changes:
        log_audit(user.id, 'task', task.id, 'update', changes)

        # Notify on status change to Delayed/Cancelled
        if 'status' in changes and changes['status']['new'] in ('Delayed', 'Cancelled'):
            activity = task.activity
            if activity and activity.budget_holder_id:
                bh_users = User.query.filter_by(budget_holder_id=activity.budget_holder_id, is_active=True).all()
                for bh_user in bh_users:
                    create_notification(
                        bh_user.id, 'status_change',
                        f'Task status changed to {changes["status"]["new"]}: {task.name}',
                        ref_type='task', ref_id=task.id,
                    )

        # Notify on reassignment
        if 'responsible_id' in changes and task.responsible_id and task.responsible_id != user.id:
            create_notification(
                task.responsible_id, 'task_assigned',
                f'You have been assigned: {task.name}',
                ref_type='task', ref_id=task.id,
            )

    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.delete('/tasks/<string:task_id>')
@require_permission('task', 'delete')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_deleted = True
    log_audit(get_jwt_identity(), 'task', task.id, 'delete')
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ── Bulk Operations ─────────────────────────────────────────────

@tasks_bp.post('/tasks/bulk-assign')
@require_roles('Admin', 'ME_Specialist', 'Budget_Holder')
def bulk_assign():
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    responsible_id = data.get('responsible_id')
    if not task_ids or not responsible_id:
        return jsonify({'error': 'task_ids and responsible_id required'}), 400

    user = get_current_user()
    updated = 0
    for tid in task_ids:
        task = Task.query.get(tid)
        if task and not task.is_deleted:
            old_val = task.responsible_id
            task.responsible_id = responsible_id
            log_audit(user.id, 'task', task.id, 'update',
                      {'responsible_id': {'old': old_val, 'new': responsible_id}})
            if responsible_id != user.id:
                create_notification(
                    responsible_id, 'task_assigned',
                    f'You have been assigned: {task.name}',
                    ref_type='task', ref_id=task.id,
                )
            updated += 1
    db.session.commit()
    return jsonify({'message': f'{updated} tasks updated'}), 200


@tasks_bp.post('/tasks/bulk-shift-dates')
@require_roles('Admin', 'ME_Specialist')
def bulk_shift_dates():
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    shift_days = data.get('shift_days', 0)
    if not task_ids or not shift_days:
        return jsonify({'error': 'task_ids and shift_days required'}), 400

    user = get_current_user()
    delta = timedelta(days=int(shift_days))
    updated = 0
    for tid in task_ids:
        task = Task.query.get(tid)
        if task and not task.is_deleted:
            old_start = task.start_date.isoformat()
            old_end = task.end_date.isoformat()
            task.start_date = task.start_date + delta
            task.end_date = task.end_date + delta
            log_audit(user.id, 'task', task.id, 'update', {
                'start_date': {'old': old_start, 'new': task.start_date.isoformat()},
                'end_date': {'old': old_end, 'new': task.end_date.isoformat()},
            })
            updated += 1
    db.session.commit()
    return jsonify({'message': f'{updated} tasks shifted by {shift_days} days'}), 200


@tasks_bp.post('/tasks/bulk-status')
@require_roles('Admin', 'ME_Specialist', 'Budget_Holder')
def bulk_status():
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    new_status = data.get('status')
    if not task_ids or not new_status or new_status not in TASK_STATUSES:
        return jsonify({'error': 'task_ids and valid status required'}), 400

    user = get_current_user()
    updated = 0
    for tid in task_ids:
        task = Task.query.get(tid)
        if task and not task.is_deleted:
            old_status = task.status
            task.status = new_status
            log_audit(user.id, 'task', task.id, 'update',
                      {'status': {'old': old_status, 'new': new_status}})
            updated += 1
    db.session.commit()
    return jsonify({'message': f'{updated} tasks updated to {new_status}'}), 200


# ── My Tasks (Implementer) ─────────────────────────────────────

@tasks_bp.get('/tasks/my-tasks')
@jwt_required()
def my_tasks():
    user_id = get_jwt_identity()
    query = Task.query.filter_by(responsible_id=user_id, is_deleted=False)

    status = request.args.get('status')
    if status and status in TASK_STATUSES:
        query = query.filter_by(status=status)

    tasks = query.order_by(Task.end_date).all()
    return jsonify({'data': [t.to_dict() for t in tasks]}), 200


# ── Comments ────────────────────────────────────────────────────

@tasks_bp.get('/tasks/<string:task_id>/comments')
@jwt_required()
def list_comments(task_id):
    comments = TaskComment.query.filter_by(
        task_id=task_id, is_deleted=False, parent_comment_id=None
    ).order_by(TaskComment.created_at).all()
    return jsonify({'data': [c.to_dict() for c in comments]}), 200


@tasks_bp.post('/tasks/<string:task_id>/comments')
@jwt_required()
def create_comment(task_id):
    user = get_current_user()
    if not user.has_permission('comment', 'create'):
        return jsonify({'error': 'Insufficient permissions'}), 403

    Task.query.get_or_404(task_id)

    data = request.get_json()
    if not data or not data.get('body'):
        return jsonify({'error': 'Comment body required'}), 400

    comment = TaskComment(
        task_id=task_id,
        author_id=user.id,
        body=data['body'],
        parent_comment_id=data.get('parent_comment_id'),
        mentions=data.get('mentions', []),
    )
    db.session.add(comment)

    # Notify mentioned users
    for mentioned_id in (data.get('mentions') or []):
        if mentioned_id != user.id:
            create_notification(
                mentioned_id, 'mention',
                f'{user.full_name} mentioned you in a comment',
                body=data['body'][:200],
                ref_type='task', ref_id=task_id,
            )

    db.session.commit()
    return jsonify(comment.to_dict()), 201


@tasks_bp.put('/comments/<string:comment_id>')
@jwt_required()
def update_comment(comment_id):
    user = get_current_user()
    comment = TaskComment.query.get_or_404(comment_id)
    if comment.author_id != user.id and not user.has_role('Admin'):
        return jsonify({'error': 'Can only edit own comments'}), 403

    data = request.get_json()
    if data.get('body'):
        comment.body = data['body']
    db.session.commit()
    return jsonify(comment.to_dict()), 200


@tasks_bp.delete('/comments/<string:comment_id>')
@jwt_required()
def delete_comment(comment_id):
    user = get_current_user()
    comment = TaskComment.query.get_or_404(comment_id)
    if comment.author_id != user.id and not user.has_role('Admin'):
        return jsonify({'error': 'Can only delete own comments'}), 403
    comment.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ── Attachments ─────────────────────────────────────────────────

@tasks_bp.post('/tasks/<string:task_id>/attachments')
@jwt_required()
def upload_attachment(task_id):
    user = get_current_user()
    if not user.has_permission('attachment', 'create'):
        return jsonify({'error': 'Insufficient permissions'}), 403

    Task.query.get_or_404(task_id)

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Allowed: pdf, jpg, png, xlsx, docx'}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}_{filename}"

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], task_id)
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, unique_name)
    file.save(filepath)

    file_size = os.path.getsize(filepath)

    attachment = Attachment(
        task_id=task_id,
        file_name=filename,
        file_type=ext,
        file_size_bytes=file_size,
        storage_path=filepath,
        uploaded_by=user.id,
    )
    db.session.add(attachment)
    db.session.commit()
    return jsonify(attachment.to_dict()), 201


@tasks_bp.get('/attachments/<string:att_id>/download')
@jwt_required()
def download_attachment(att_id):
    attachment = Attachment.query.get_or_404(att_id)
    if not os.path.exists(attachment.storage_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(attachment.storage_path, as_attachment=True, download_name=attachment.file_name)


@tasks_bp.delete('/attachments/<string:att_id>')
@jwt_required()
def delete_attachment(att_id):
    user = get_current_user()
    attachment = Attachment.query.get_or_404(att_id)
    if attachment.uploaded_by != user.id and not user.has_role('Admin'):
        return jsonify({'error': 'Can only delete own attachments'}), 403

    if os.path.exists(attachment.storage_path):
        os.remove(attachment.storage_path)

    db.session.delete(attachment)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200
