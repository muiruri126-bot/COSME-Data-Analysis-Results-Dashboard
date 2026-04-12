export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  is_active: boolean;
  roles: string[];
  budget_holder_id?: string;
}

export interface BudgetHolder {
  id: string;
  name: string;
}

export interface IntermediateOutcome {
  id: string;
  code: string;
  description: string;
  immediate_outcomes?: ImmediateOutcome[];
}

export interface ImmediateOutcome {
  id: string;
  code: string;
  description: string;
  intermediate_outcome_id: string;
  outputs?: Output[];
}

export interface Output {
  id: string;
  code: string;
  description: string;
  immediate_outcome_id: string;
  activities?: Activity[];
}

export interface Activity {
  id: string;
  code: string;
  description: string;
  output_id: string;
  budget_holder_id?: string;
  budget_holder?: BudgetHolder;
  status: string;
}

export interface Task {
  id: string;
  name: string;
  activity_id: string;
  activity_code?: string;
  responsible_id?: string;
  responsible_person?: string;
  responsible?: User;
  plan_actual: 'Planned' | 'Actual';
  start_date: string;
  end_date: string;
  start_date_iso?: string;
  end_date_iso?: string;
  status: string;
  completion_evidence?: string;
  created_by?: string;
  creator?: string;
  comment_count?: number;
  attachment_count?: number;
  created_at?: string;
  updated_at?: string;
  comments?: TaskComment[];
  attachments?: Attachment[];
}

export interface TaskComment {
  id: string;
  task_id: string;
  parent_comment_id?: string;
  author_id: string;
  author?: User;
  body: string;
  mentions?: string[];
  replies?: TaskComment[];
  created_at: string;
  updated_at?: string;
}

export interface Attachment {
  id: string;
  task_id: string;
  file_name: string;
  file_type: string;
  file_size_bytes: number;
  uploaded_by?: string;
  uploader?: string;
  created_at?: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  body?: string;
  reference_type?: string;
  reference_id?: string;
  is_read: boolean;
  created_at: string;
}

export interface GanttBar {
  id: string;
  label: string;
  activity_code?: string;
  start_date: string;
  end_date: string;
  plan_actual: string;
  status: string;
  responsible?: string;
  color: string;
  duration_days: number;
  variance_days?: number;
}

export interface KPIs {
  total_tasks: number;
  complete: number;
  in_progress: number;
  pending: number;
  delayed: number;
  cancelled: number;
  percent_complete: number;
  on_time_rate: number;
  avg_days_overdue: number;
  tasks_by_status: Record<string, number>;
}
