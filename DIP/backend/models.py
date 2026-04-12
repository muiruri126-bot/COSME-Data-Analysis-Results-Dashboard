import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return str(uuid.uuid4())


# ── Association Tables ──────────────────────────────────────────

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.String(36), db.ForeignKey('roles.id'), primary_key=True),
)

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.String(36), db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.String(36), db.ForeignKey('permissions.id'), primary_key=True),
)


# ── Users & RBAC ────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    budget_holder_id = db.Column(db.String(36), db.ForeignKey('budget_holders.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    reset_token = db.Column(db.String(100), nullable=True, unique=True)
    reset_token_expires = db.Column(db.DateTime(timezone=True), nullable=True)

    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    budget_holder = db.relationship('BudgetHolder', backref='users')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(r.name == role_name for r in self.roles)

    def has_permission(self, resource, action):
        for role in self.roles:
            for perm in role.permissions:
                if perm.resource == resource and perm.action == action:
                    return True
        return False

    def to_dict(self, include_roles=True):
        d = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'budget_holder_id': self.budget_holder_id,
            'budget_holder': self.budget_holder.to_dict() if self.budget_holder else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_roles:
            d['roles'] = [r.name for r in self.roles]
        return d


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': [p.to_dict() for p in self.permissions],
        }


class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    resource = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)

    __table_args__ = (db.UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),)

    def to_dict(self):
        return {'id': self.id, 'resource': self.resource, 'action': self.action}


# ── Budget Holders ──────────────────────────────────────────────

class BudgetHolder(db.Model):
    __tablename__ = 'budget_holders'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


# ── Results Framework ───────────────────────────────────────────

class IntermediateOutcome(db.Model):
    __tablename__ = 'intermediate_outcomes'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    immediate_outcomes = db.relationship('ImmediateOutcome', backref='intermediate_outcome', lazy='dynamic')

    def to_dict(self, include_children=False):
        d = {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'sort_order': self.sort_order,
        }
        if include_children:
            d['immediate_outcomes'] = [io.to_dict() for io in
                                       self.immediate_outcomes.filter_by(is_deleted=False).order_by(ImmediateOutcome.sort_order).all()]
        return d


class ImmediateOutcome(db.Model):
    __tablename__ = 'immediate_outcomes'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    intermediate_outcome_id = db.Column(db.String(36), db.ForeignKey('intermediate_outcomes.id'), nullable=False, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    outputs = db.relationship('Output', backref='immediate_outcome', lazy='dynamic')

    def to_dict(self, include_children=False):
        d = {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'intermediate_outcome_id': self.intermediate_outcome_id,
            'sort_order': self.sort_order,
        }
        if include_children:
            d['outputs'] = [o.to_dict() for o in
                            self.outputs.filter_by(is_deleted=False).order_by(Output.sort_order).all()]
        return d


class Output(db.Model):
    __tablename__ = 'outputs'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    immediate_outcome_id = db.Column(db.String(36), db.ForeignKey('immediate_outcomes.id'), nullable=False, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    activities = db.relationship('Activity', backref='output', lazy='dynamic')

    def to_dict(self, include_children=False):
        d = {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'immediate_outcome_id': self.immediate_outcome_id,
            'sort_order': self.sort_order,
        }
        if include_children:
            d['activities'] = [a.to_dict() for a in
                               self.activities.filter_by(is_deleted=False).order_by(Activity.sort_order).all()]
        return d


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    output_id = db.Column(db.String(36), db.ForeignKey('outputs.id'), nullable=False, index=True)
    budget_holder_id = db.Column(db.String(36), db.ForeignKey('budget_holders.id'), nullable=True, index=True)
    status = db.Column(db.String(20), default='Active')
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    budget_holder = db.relationship('BudgetHolder', backref='activities')
    tasks = db.relationship('Task', backref='activity', lazy='dynamic')

    def to_dict(self, include_tasks=False):
        d = {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'output_id': self.output_id,
            'budget_holder_id': self.budget_holder_id,
            'budget_holder': self.budget_holder.to_dict() if self.budget_holder else None,
            'status': self.status,
            'sort_order': self.sort_order,
            'task_count': self.tasks.filter_by(is_deleted=False).count(),
        }
        if include_tasks:
            d['tasks'] = [t.to_dict() for t in
                          self.tasks.filter_by(is_deleted=False).order_by(Task.start_date).all()]
        return d


# ── Tasks ───────────────────────────────────────────────────────

TASK_STATUSES = ('Pending', 'In progress', 'Complete', 'Delayed', 'Cancelled')
PLAN_ACTUAL_CHOICES = ('Planned', 'Actual')


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    activity_id = db.Column(db.String(36), db.ForeignKey('activities.id'), nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    responsible_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)
    responsible_person = db.Column(db.String(255), nullable=True)
    plan_actual = db.Column(db.String(10), nullable=False, default='Planned')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending', index=True)
    completion_evidence = db.Column(db.Text)
    baseline_id = db.Column(db.String(36), db.ForeignKey('baselines.id'), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    responsible = db.relationship('User', foreign_keys=[responsible_id], backref='assigned_tasks')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('TaskComment', backref='task', lazy='dynamic', order_by='TaskComment.created_at')
    attachments = db.relationship('Attachment', backref='task', lazy='dynamic')
    revisions = db.relationship('TaskRevision', backref='task', lazy='dynamic')

    __table_args__ = (
        db.CheckConstraint('end_date >= start_date', name='chk_task_dates'),
        db.Index('idx_tasks_dates', 'start_date', 'end_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'activity_code': self.activity.code if self.activity else None,
            'name': self.name,
            'responsible_id': self.responsible_id,
            'responsible_person': self.responsible_person or (self.responsible.full_name if self.responsible else None),
            'responsible': self.responsible.to_dict(include_roles=False) if self.responsible else None,
            'plan_actual': self.plan_actual,
            'start_date': self.start_date.strftime('%d/%m/%Y') if self.start_date else None,
            'end_date': self.end_date.strftime('%d/%m/%Y') if self.end_date else None,
            'start_date_iso': self.start_date.isoformat() if self.start_date else None,
            'end_date_iso': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'completion_evidence': self.completion_evidence,
            'created_by': self.created_by,
            'creator': self.creator.full_name if self.creator else None,
            'comment_count': self.comments.filter_by(is_deleted=False).count(),
            'attachment_count': self.attachments.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ── Comments ────────────────────────────────────────────────────

class TaskComment(db.Model):
    __tablename__ = 'task_comments'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False, index=True)
    parent_comment_id = db.Column(db.String(36), db.ForeignKey('task_comments.id'), nullable=True)
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    mentions = db.Column(db.JSON, default=list)  # list of user IDs
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    author = db.relationship('User', backref='comments')
    replies = db.relationship('TaskComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self, include_replies=True):
        d = {
            'id': self.id,
            'task_id': self.task_id,
            'parent_comment_id': self.parent_comment_id,
            'author_id': self.author_id,
            'author': self.author.to_dict(include_roles=False) if self.author else None,
            'body': self.body,
            'mentions': self.mentions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_replies:
            d['replies'] = [r.to_dict(include_replies=False) for r in
                            self.replies.filter_by(is_deleted=False).order_by(TaskComment.created_at).all()]
        return d


# ── Attachments ─────────────────────────────────────────────────

class Attachment(db.Model):
    __tablename__ = 'attachments'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    uploader = db.relationship('User', backref='uploads')

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size_bytes': self.file_size_bytes,
            'uploaded_by': self.uploaded_by,
            'uploader': self.uploader.full_name if self.uploader else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ── Baselines & Revisions ──────────────────────────────────────

class Baseline(db.Model):
    __tablename__ = 'baselines'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Draft')  # Draft, Submitted, Approved, Locked
    submitted_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    approved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    submitted_at = db.Column(db.DateTime(timezone=True))
    approved_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'submitted_by': self.submitted_by,
            'approved_by': self.approved_by,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TaskRevision(db.Model):
    __tablename__ = 'task_revisions'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False, index=True)
    baseline_id = db.Column(db.String(36), db.ForeignKey('baselines.id'), nullable=False)
    changed_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    changer = db.relationship('User', backref='revisions')


# ── Audit Log ───────────────────────────────────────────────────

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.String(36), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    changes = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)

    user = db.relationship('User', backref='audit_logs')

    __table_args__ = (
        db.Index('idx_audit_entity', 'entity_type', 'entity_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.full_name if self.user else None,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'changes': self.changes,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ── Notifications ───────────────────────────────────────────────

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.String(36))
    is_read = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ── Schedule Flags (from Gantt Chart X marks) ──────────────────

class ScheduleFlag(db.Model):
    __tablename__ = 'schedule_flags'

    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    activity_id = db.Column(db.String(36), db.ForeignKey('activities.id'), nullable=False, index=True)
    quarter = db.Column(db.String(5), nullable=False)
    is_planned = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    activity = db.relationship('Activity', backref='schedule_flags')
