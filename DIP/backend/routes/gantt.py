"""Gantt chart API: generate bar data from tasks at multiple roll-up levels."""
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from models import (
    db, Task, Activity, Output, ImmediateOutcome, IntermediateOutcome,
    User, BudgetHolder, TASK_STATUSES
)

gantt_bp = Blueprint('gantt', __name__, url_prefix='/api/v1/gantt')

STATUS_COLORS = {
    'Pending': '#9CA3AF',
    'In progress': '#3B82F6',
    'Complete': '#22C55E',
    'Delayed': '#F97316',
    'Cancelled': '#4B5563',
}


def tasks_to_bars(tasks):
    """Convert task list to Gantt bar data."""
    bars = []
    for t in tasks:
        variance_days = None
        if t.plan_actual == 'Actual' and t.end_date:
            # Find matching planned task
            planned = Task.query.filter_by(
                activity_id=t.activity_id,
                plan_actual='Planned',
                is_deleted=False,
            ).first()
            if planned and planned.end_date:
                variance_days = (t.end_date - planned.end_date).days

        bars.append({
            'id': t.id,
            'label': t.name,
            'activity_code': t.activity.code if t.activity else None,
            'activity_desc': t.activity.description if t.activity else None,
            'planned_start': t.start_date.isoformat() if t.plan_actual == 'Planned' else None,
            'planned_end': t.end_date.isoformat() if t.plan_actual == 'Planned' else None,
            'actual_start': t.start_date.isoformat() if t.plan_actual == 'Actual' else None,
            'actual_end': t.end_date.isoformat() if t.plan_actual == 'Actual' else None,
            'start_date': t.start_date.isoformat(),
            'end_date': t.end_date.isoformat(),
            'plan_actual': t.plan_actual,
            'status': t.status,
            'responsible': t.responsible.full_name if t.responsible else None,
            'variance_days': variance_days,
            'color': STATUS_COLORS.get(t.status, '#9CA3AF'),
            'duration_days': (t.end_date - t.start_date).days + 1,
        })
    return bars


def compute_rollup(tasks):
    """Compute roll-up start/end/progress from a list of tasks."""
    if not tasks:
        return None
    start_dates = [t.start_date for t in tasks if t.start_date]
    end_dates = [t.end_date for t in tasks if t.end_date]
    total = len(tasks)
    complete = sum(1 for t in tasks if t.status == 'Complete')
    return {
        'start_date': min(start_dates).isoformat() if start_dates else None,
        'end_date': max(end_dates).isoformat() if end_dates else None,
        'progress': round(complete / total * 100, 1) if total > 0 else 0,
        'total_tasks': total,
        'complete_tasks': complete,
    }


def apply_filters(query):
    """Common filters for gantt queries."""
    status = request.args.get('status')
    if status and status in TASK_STATUSES:
        query = query.filter(Task.status == status)

    responsible_id = request.args.get('responsible_id')
    if responsible_id:
        query = query.filter(Task.responsible_id == responsible_id)

    start_from = request.args.get('start')
    if start_from:
        try:
            query = query.filter(Task.end_date >= date.fromisoformat(start_from))
        except ValueError:
            pass

    end_to = request.args.get('end')
    if end_to:
        try:
            query = query.filter(Task.start_date <= date.fromisoformat(end_to))
        except ValueError:
            pass

    plan_actual = request.args.get('plan_actual')
    if plan_actual and plan_actual in ('Planned', 'Actual'):
        query = query.filter(Task.plan_actual == plan_actual)

    return query


@gantt_bp.get('/by-activity/<string:act_id>')
@jwt_required()
def gantt_by_activity(act_id):
    activity = Activity.query.get_or_404(act_id)
    query = Task.query.filter_by(activity_id=act_id, is_deleted=False)
    query = apply_filters(query)
    tasks = query.order_by(Task.start_date).all()

    return jsonify({
        'level': 'activity',
        'code': activity.code,
        'description': activity.description,
        'rollup': compute_rollup(tasks),
        'bars': tasks_to_bars(tasks),
    }), 200


@gantt_bp.get('/by-output/<string:out_id>')
@jwt_required()
def gantt_by_output(out_id):
    output = Output.query.get_or_404(out_id)
    activities = Activity.query.filter_by(output_id=out_id, is_deleted=False).all()
    act_ids = [a.id for a in activities]

    query = Task.query.filter(
        Task.activity_id.in_(act_ids), Task.is_deleted == False
    )
    query = apply_filters(query)
    tasks = query.order_by(Task.start_date).all()

    groups = []
    for act in activities:
        act_tasks = [t for t in tasks if t.activity_id == act.id]
        groups.append({
            'code': act.code,
            'description': act.description,
            'level': 'activity',
            'rollup': compute_rollup(act_tasks),
            'bars': tasks_to_bars(act_tasks),
        })

    return jsonify({
        'level': 'output',
        'code': output.code,
        'description': output.description,
        'rollup': compute_rollup(tasks),
        'groups': groups,
    }), 200


@gantt_bp.get('/by-immediate-outcome/<string:imo_id>')
@jwt_required()
def gantt_by_immediate_outcome(imo_id):
    imo = ImmediateOutcome.query.get_or_404(imo_id)
    outputs = Output.query.filter_by(immediate_outcome_id=imo_id, is_deleted=False).all()

    all_tasks = []
    groups = []
    for out in outputs:
        activities = Activity.query.filter_by(output_id=out.id, is_deleted=False).all()
        act_ids = [a.id for a in activities]
        query = Task.query.filter(Task.activity_id.in_(act_ids), Task.is_deleted == False)
        query = apply_filters(query)
        out_tasks = query.order_by(Task.start_date).all()
        all_tasks.extend(out_tasks)

        groups.append({
            'code': out.code,
            'description': out.description,
            'level': 'output',
            'rollup': compute_rollup(out_tasks),
        })

    return jsonify({
        'level': 'immediate_outcome',
        'code': imo.code,
        'description': imo.description,
        'rollup': compute_rollup(all_tasks),
        'groups': groups,
    }), 200


@gantt_bp.get('/by-intermediate-outcome/<string:io_id>')
@jwt_required()
def gantt_by_intermediate_outcome(io_id):
    io = IntermediateOutcome.query.get_or_404(io_id)
    imos = ImmediateOutcome.query.filter_by(intermediate_outcome_id=io_id, is_deleted=False).all()

    all_tasks = []
    groups = []
    for imo in imos:
        outputs = Output.query.filter_by(immediate_outcome_id=imo.id, is_deleted=False).all()
        imo_tasks = []
        for out in outputs:
            activities = Activity.query.filter_by(output_id=out.id, is_deleted=False).all()
            act_ids = [a.id for a in activities]
            query = Task.query.filter(Task.activity_id.in_(act_ids), Task.is_deleted == False)
            query = apply_filters(query)
            imo_tasks.extend(query.all())

        all_tasks.extend(imo_tasks)
        groups.append({
            'code': imo.code,
            'description': imo.description,
            'level': 'immediate_outcome',
            'rollup': compute_rollup(imo_tasks),
        })

    return jsonify({
        'level': 'intermediate_outcome',
        'code': io.code,
        'description': io.description,
        'rollup': compute_rollup(all_tasks),
        'groups': groups,
    }), 200


@gantt_bp.get('/by-budget-holder/<string:bh_id>')
@jwt_required()
def gantt_by_budget_holder(bh_id):
    bh = BudgetHolder.query.get_or_404(bh_id)
    activities = Activity.query.filter_by(budget_holder_id=bh_id, is_deleted=False).all()
    act_ids = [a.id for a in activities]

    query = Task.query.filter(Task.activity_id.in_(act_ids), Task.is_deleted == False)
    query = apply_filters(query)
    tasks = query.order_by(Task.start_date).all()

    groups = []
    for act in activities:
        act_tasks = [t for t in tasks if t.activity_id == act.id]
        if act_tasks:
            groups.append({
                'code': act.code,
                'description': act.description,
                'level': 'activity',
                'rollup': compute_rollup(act_tasks),
                'bars': tasks_to_bars(act_tasks),
            })

    return jsonify({
        'level': 'budget_holder',
        'name': bh.name,
        'rollup': compute_rollup(tasks),
        'groups': groups,
    }), 200


@gantt_bp.get('/by-responsible/<string:user_id>')
@jwt_required()
def gantt_by_responsible(user_id):
    user = User.query.get_or_404(user_id)
    query = Task.query.filter_by(responsible_id=user_id, is_deleted=False)
    query = apply_filters(query)
    tasks = query.order_by(Task.start_date).all()

    return jsonify({
        'level': 'responsible',
        'name': user.full_name,
        'rollup': compute_rollup(tasks),
        'bars': tasks_to_bars(tasks),
    }), 200
