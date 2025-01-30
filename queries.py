from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import text, func
from sqlalchemy.orm import Session
import model as m

@dataclass
class SignalSummary:
    controlador_id: int
    controlador_name: str
    last_signal_time: datetime
    signal_count: int
    latest_values: Dict[str, Any]

class SignalQueries:
    def __init__(self, session: Session):
        self.session = session
    
    def get_latest_by_controlador(
        self, 
        controlador_id: int,
        user_permissions: List[str]  # Inject permissions
    ) -> Optional[m.Signal]:
        if 'view_signals' not in user_permissions:
            return None
            
        return self.session.query(m.Signal)\
            .filter_by(controlador_id=controlador_id)\
            .order_by(m.Signal.tstamp.desc())\
            .first()
    
    def get_signals_in_timeframe(
        self,
        controlador_id: int,
        start_time: datetime,
        end_time: datetime,
        user_permissions: List[str]
    ) -> List[m.Signal]:
        if 'view_signals' not in user_permissions:
            return []
            
        return self.session.query(m.Signal)\
            .filter(
                m.Signal.controlador_id == controlador_id,
                m.Signal.tstamp.between(start_time, end_time)
            ).order_by(m.Signal.tstamp).all()
    
    def get_controlador_summary(
        self,
        empresa_id: int,
        user_permissions: List[str]
    ) -> List[SignalSummary]:
        if 'view_dashboard' not in user_permissions:
            return []
            
        # Complex query joining controladores and signals
        result = self.session.execute(
            text("""
                SELECT  
                    c.id,
                    c.name,
                    MAX(s.tstamp) as last_signal,
                    COUNT(s.id) as signal_count,
                    s.values as latest_values
                FROM controladores c
                LEFT JOIN signals s ON s.controlador_id = c.id
                WHERE c.empresa_id = :empresa_id
                GROUP BY c.id, c.name, s.values
                ORDER BY last_signal DESC
            """),
            {"empresa_id": empresa_id}
        )
        
        return [SignalSummary(*row) for row in result] 