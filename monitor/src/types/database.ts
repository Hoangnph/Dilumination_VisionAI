// Database types and interfaces
export interface Session {
  id: string;
  session_name: string;
  input_source: string;
  status: 'active' | 'completed' | 'error';
  start_time: string;
  end_time?: string;
  total_people_entered: number;
  total_people_exited: number;
  current_people_count: number;
}

export interface PeopleMovement {
  id: string;
  session_id: string;
  person_id: number;
  movement_direction: 'in' | 'out';
  movement_time: string;
  centroid_x: number;
  centroid_y: number;
  bounding_box_x1: number;
  bounding_box_y1: number;
  bounding_box_x2: number;
  bounding_box_y2: number;
  confidence_score: number;
  frame_number: number;
}

export interface RealtimeMetrics {
  id: string;
  session_id: string;
  timestamp: string;
  people_entered_last_minute: number;
  people_exited_last_minute: number;
  current_people_count: number;
  average_processing_fps: number;
  detection_confidence_avg: number;
}

export interface AlertLog {
  id: string;
  session_id: string;
  alert_type: 'threshold_exceeded' | 'system_error' | 'performance_warning';
  alert_message: string;
  alert_time: string;
  threshold_value?: number;
  current_value?: number;
  resolved: boolean;
}

export interface DashboardStats {
  total_sessions: number;
  active_sessions: number;
  total_people_today: number;
  peak_hour: string;
  average_session_duration: number;
  system_uptime: number;
}

export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface TimeSeriesData {
  label: string;
  data: ChartDataPoint[];
  color?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'movement' | 'metrics' | 'alert' | 'session_update';
  data: PeopleMovement | RealtimeMetrics | AlertLog | Session;
  timestamp: string;
}

export interface MovementMessage extends WebSocketMessage {
  type: 'movement';
  data: PeopleMovement;
}

export interface MetricsMessage extends WebSocketMessage {
  type: 'metrics';
  data: RealtimeMetrics;
}

export interface AlertMessage extends WebSocketMessage {
  type: 'alert';
  data: AlertLog;
}

export interface SessionUpdateMessage extends WebSocketMessage {
  type: 'session_update';
  data: Session;
}
