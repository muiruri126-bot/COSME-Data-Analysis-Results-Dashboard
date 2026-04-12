"""Results Framework routes: cascading hierarchy CRUD."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import (
    db, IntermediateOutcome, ImmediateOutcome, Output, Activity
)
from auth_utils import require_permission, log_audit, get_current_user

framework_bp = Blueprint('framework', __name__, url_prefix='/api/v1')


# ── Intermediate Outcomes ───────────────────────────────────────

@framework_bp.get('/intermediate-outcomes')
@jwt_required()
def list_intermediate_outcomes():
    items = IntermediateOutcome.query.filter_by(is_deleted=False)\
        .order_by(IntermediateOutcome.sort_order).all()
    return jsonify({'data': [i.to_dict() for i in items]}), 200


@framework_bp.get('/intermediate-outcomes/<string:io_id>')
@jwt_required()
def get_intermediate_outcome(io_id):
    item = IntermediateOutcome.query.get_or_404(io_id)
    return jsonify(item.to_dict(include_children=True)), 200


@framework_bp.post('/intermediate-outcomes')
@require_permission('intermediate_outcome', 'create')
def create_intermediate_outcome():
    data = request.get_json()
    if not data or not data.get('code') or not data.get('description'):
        return jsonify({'error': 'code and description required'}), 400

    if IntermediateOutcome.query.filter_by(code=data['code']).first():
        return jsonify({'error': f'Code {data["code"]} already exists'}), 409

    item = IntermediateOutcome(
        code=data['code'],
        description=data['description'],
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(item)
    log_audit(get_jwt_identity(), 'intermediate_outcome', item.id, 'create')
    db.session.commit()
    return jsonify(item.to_dict()), 201


@framework_bp.put('/intermediate-outcomes/<string:io_id>')
@require_permission('intermediate_outcome', 'update')
def update_intermediate_outcome(io_id):
    item = IntermediateOutcome.query.get_or_404(io_id)
    data = request.get_json()
    changes = {}
    for field in ('code', 'description', 'sort_order'):
        if field in data and getattr(item, field) != data[field]:
            changes[field] = {'old': getattr(item, field), 'new': data[field]}
            setattr(item, field, data[field])
    if changes:
        log_audit(get_jwt_identity(), 'intermediate_outcome', item.id, 'update', changes)
    db.session.commit()
    return jsonify(item.to_dict()), 200


@framework_bp.delete('/intermediate-outcomes/<string:io_id>')
@require_permission('intermediate_outcome', 'delete')
def delete_intermediate_outcome(io_id):
    item = IntermediateOutcome.query.get_or_404(io_id)
    item.is_deleted = True
    log_audit(get_jwt_identity(), 'intermediate_outcome', item.id, 'delete')
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ── Immediate Outcomes (filtered by intermediate) ──────────────

@framework_bp.get('/intermediate-outcomes/<string:io_id>/immediate-outcomes')
@jwt_required()
def list_immediate_outcomes(io_id):
    items = ImmediateOutcome.query.filter_by(
        intermediate_outcome_id=io_id, is_deleted=False
    ).order_by(ImmediateOutcome.sort_order).all()
    return jsonify({'data': [i.to_dict() for i in items]}), 200


@framework_bp.get('/immediate-outcomes/<string:imo_id>')
@jwt_required()
def get_immediate_outcome(imo_id):
    item = ImmediateOutcome.query.get_or_404(imo_id)
    return jsonify(item.to_dict(include_children=True)), 200


@framework_bp.post('/immediate-outcomes')
@require_permission('immediate_outcome', 'create')
def create_immediate_outcome():
    data = request.get_json()
    required = ('code', 'description', 'intermediate_outcome_id')
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': 'code, description, and intermediate_outcome_id required'}), 400

    item = ImmediateOutcome(
        code=data['code'],
        description=data['description'],
        intermediate_outcome_id=data['intermediate_outcome_id'],
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(item)
    log_audit(get_jwt_identity(), 'immediate_outcome', item.id, 'create')
    db.session.commit()
    return jsonify(item.to_dict()), 201


@framework_bp.put('/immediate-outcomes/<string:imo_id>')
@require_permission('immediate_outcome', 'update')
def update_immediate_outcome(imo_id):
    item = ImmediateOutcome.query.get_or_404(imo_id)
    data = request.get_json()
    changes = {}
    for field in ('code', 'description', 'sort_order', 'intermediate_outcome_id'):
        if field in data and getattr(item, field) != data[field]:
            changes[field] = {'old': getattr(item, field), 'new': data[field]}
            setattr(item, field, data[field])
    if changes:
        log_audit(get_jwt_identity(), 'immediate_outcome', item.id, 'update', changes)
    db.session.commit()
    return jsonify(item.to_dict()), 200


# ── Outputs (filtered by immediate outcome) ────────────────────

@framework_bp.get('/immediate-outcomes/<string:imo_id>/outputs')
@jwt_required()
def list_outputs(imo_id):
    items = Output.query.filter_by(
        immediate_outcome_id=imo_id, is_deleted=False
    ).order_by(Output.sort_order).all()
    return jsonify({'data': [i.to_dict() for i in items]}), 200


@framework_bp.get('/outputs/<string:out_id>')
@jwt_required()
def get_output(out_id):
    item = Output.query.get_or_404(out_id)
    return jsonify(item.to_dict(include_children=True)), 200


@framework_bp.post('/outputs')
@require_permission('output', 'create')
def create_output():
    data = request.get_json()
    required = ('code', 'description', 'immediate_outcome_id')
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': 'code, description, and immediate_outcome_id required'}), 400

    item = Output(
        code=data['code'],
        description=data['description'],
        immediate_outcome_id=data['immediate_outcome_id'],
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(item)
    log_audit(get_jwt_identity(), 'output', item.id, 'create')
    db.session.commit()
    return jsonify(item.to_dict()), 201


@framework_bp.put('/outputs/<string:out_id>')
@require_permission('output', 'update')
def update_output(out_id):
    item = Output.query.get_or_404(out_id)
    data = request.get_json()
    changes = {}
    for field in ('code', 'description', 'sort_order', 'immediate_outcome_id'):
        if field in data and getattr(item, field) != data[field]:
            changes[field] = {'old': getattr(item, field), 'new': data[field]}
            setattr(item, field, data[field])
    if changes:
        log_audit(get_jwt_identity(), 'output', item.id, 'update', changes)
    db.session.commit()
    return jsonify(item.to_dict()), 200


# ── Activities (filtered by output) ────────────────────────────

@framework_bp.get('/outputs/<string:out_id>/activities')
@jwt_required()
def list_activities(out_id):
    user = get_current_user()
    query = Activity.query.filter_by(output_id=out_id, is_deleted=False)

    # Budget holders only see own portfolio activities (if they have a budget_holder_id)
    if (user.has_role('Budget_Holder')
            and not user.has_role('Admin')
            and not user.has_role('ME_Specialist')
            and not user.has_role('Viewer')
            and user.budget_holder_id):
        query = query.filter_by(budget_holder_id=user.budget_holder_id)

    items = query.order_by(Activity.sort_order).all()
    return jsonify({'data': [i.to_dict() for i in items]}), 200


@framework_bp.get('/activities/<string:act_id>')
@jwt_required()
def get_activity(act_id):
    item = Activity.query.get_or_404(act_id)
    return jsonify(item.to_dict(include_tasks=True)), 200


@framework_bp.post('/activities')
@require_permission('activity', 'create')
def create_activity():
    data = request.get_json()
    required = ('code', 'description', 'output_id')
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': 'code, description, and output_id required'}), 400

    item = Activity(
        code=data['code'],
        description=data['description'],
        output_id=data['output_id'],
        budget_holder_id=data.get('budget_holder_id'),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(item)
    log_audit(get_jwt_identity(), 'activity', item.id, 'create')
    db.session.commit()
    return jsonify(item.to_dict()), 201


@framework_bp.put('/activities/<string:act_id>')
@require_permission('activity', 'update')
def update_activity(act_id):
    item = Activity.query.get_or_404(act_id)
    data = request.get_json()
    changes = {}
    for field in ('code', 'description', 'sort_order', 'output_id', 'budget_holder_id', 'status'):
        if field in data and getattr(item, field) != data[field]:
            changes[field] = {'old': getattr(item, field), 'new': data[field]}
            setattr(item, field, data[field])
    if changes:
        log_audit(get_jwt_identity(), 'activity', item.id, 'update', changes)
    db.session.commit()
    return jsonify(item.to_dict()), 200


@framework_bp.delete('/activities/<string:act_id>')
@require_permission('activity', 'delete')
def delete_activity(act_id):
    item = Activity.query.get_or_404(act_id)
    item.is_deleted = True
    log_audit(get_jwt_identity(), 'activity', item.id, 'delete')
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


# ── Budget Holders (read-only for dropdowns) ───────────────────

@framework_bp.get('/budget-holders')
@jwt_required()
def list_budget_holders():
    from models import BudgetHolder
    items = BudgetHolder.query.order_by(BudgetHolder.name).all()
    return jsonify({'data': [bh.to_dict() for bh in items]}), 200


# ── Users list (for responsible dropdown) ──────────────────────

@framework_bp.get('/users')
@jwt_required()
def list_users():
    from models import User
    users = User.query.filter_by(is_active=True).order_by(User.full_name).all()
    return jsonify({'data': [u.to_dict(include_roles=False) for u in users]}), 200
