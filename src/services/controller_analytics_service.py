from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
import src.domain.model as m
from src.adapters.repository import EmpresaRepository
from src.queries.queries import SignalQueries

class ControllerAnalyticsService:
    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        signal_queries: SignalQueries
    ):
        self.empresa_repo = empresa_repo
        self.signal_queries = signal_queries

    def get_uptime_downtime(self, controller_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate uptime/downtime intervals for a controller"""
        signals = self.signal_queries.get_by_timerange(controller_id, start_date, end_date)
        controller = self.empresa_repo.get_by_id(controller_id)
        
        if not signals:
            return self._create_empty_activity_data(start_date, end_date)

        daily_activity = self._process_uptime_intervals(signals, start_date, end_date)
        
        return {
            "controller_name": controller.name,
            "daily_activity": daily_activity
        }

    def get_operational_hours(self, controller_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate operational hours heatmap"""
        signals = self.signal_queries.get_by_timerange(controller_id, start_date, end_date)
        controller = self.empresa_repo.get_by_id(controller_id)
        
        heatmap_data = self._calculate_hourly_activity(signals, start_date, end_date)
        
        return {
            "controller_name": controller.name,
            "heatmap_data": heatmap_data,
            "sensor_config": controller.config
        }

    def get_sensor_correlation(self, controller_id: str, hours: int = 24) -> Dict:
        """Calculate correlation between sensors"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        signals = self.signal_queries.get_by_timerange(controller_id, start_time, end_time)
        
        return self._calculate_sensor_correlation(signals)

    def get_sensor_changes(self, controlador_id: str) -> List[Dict]:
        """Get sensor state changes for a controller"""
        signals = self.signal_queries.get_signals_in_timeframe(
            controlador_id,
            datetime.now() - timedelta(days=7),
            datetime.now()
        )
        
        changes = []
        prev_values = None
        
        for signal in signals:
            if prev_values:
                signal_changes = []
                for sensor_name, current_value in signal.values.items():
                    if sensor_name in prev_values and prev_values[sensor_name] != current_value:
                        signal_changes.append({
                            "sensor": sensor_name,
                            "old_value": bool(prev_values[sensor_name]),
                            "new_value": bool(current_value)
                        })
                
                if signal_changes:
                    changes.append({
                        "timestamp": signal.tstamp.isoformat(),
                        "changes": signal_changes
                    })
            
            prev_values = signal.values.copy()
        
        return changes

    def get_controller_timeline(self, controlador_id: str) -> Dict:
        """Get timeline data for a controller"""
        controller = self.empresa_repo.get_controlador(controlador_id)
        signals = self.signal_queries.get_signals_in_timeframe(
            controlador_id,
            datetime.now() - timedelta(days=7),
            datetime.now()
        )
        
        return {
            "sensor_config": controller.config,
            "timeline": [
                {
                    **signal.to_dict(),
                    "status": "connected" if self._check_connection_status(signal.tstamp) else "disconnected"
                }
                for signal in signals
            ]
        }

    def _process_uptime_intervals(self, signals: List, start_date: datetime, end_date: datetime) -> Dict:
        daily_activity = {}
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            daily_activity[current_date.isoformat()] = []
            current_date += timedelta(days=1)

        last_signal_time = None
        for signal in signals:
            if last_signal_time and (signal.tstamp - last_signal_time).total_seconds() > 300:
                self._add_interval(daily_activity, last_signal_time, signal.tstamp, 'downtime')
            
            self._add_interval(daily_activity, signal.tstamp, 
                             signal.tstamp + timedelta(minutes=5), 'uptime')
            
            last_signal_time = signal.tstamp

        return daily_activity

    def _calculate_hourly_activity(self, signals: List, start_date: datetime, end_date: datetime) -> Dict:
        heatmap_data = {}
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            heatmap_data[current_date.isoformat()] = [0] * 24
            current_date += timedelta(days=1)

        for signal in signals:
            signal_date = signal.tstamp.date()
            signal_hour = signal.tstamp.hour
            if self._is_signal_active(signal):
                heatmap_data[signal_date.isoformat()][signal_hour] += 5

        return heatmap_data

    def _calculate_sensor_correlation(self, signals: List) -> Dict:
        if not signals:
            return self._create_empty_correlation_matrix()

        sensor_values = {
            f'value_sensor{i}': [getattr(s, f'value_sensor{i}') for s in signals]
            for i in range(1, 7)
        }

        correlation_matrix = {}
        for s1 in sensor_values.keys():
            correlation_matrix[s1] = {}
            for s2 in sensor_values.keys():
                if s1 != s2:
                    correlation = np.corrcoef(sensor_values[s1], sensor_values[s2])[0, 1]
                    correlation_matrix[s1][s2] = float(correlation)
                else:
                    correlation_matrix[s1][s2] = 1.0

        return correlation_matrix

    @staticmethod
    def _is_signal_active(signal) -> bool:
        return any([
            signal.value_sensor1, signal.value_sensor2, signal.value_sensor3,
            signal.value_sensor4, signal.value_sensor5, signal.value_sensor6
        ])

    @staticmethod
    def _create_empty_correlation_matrix() -> Dict:
        sensors = [f'value_sensor{i}' for i in range(1, 7)]
        return {s1: {s2: 0.0 for s2 in sensors} for s1 in sensors} 