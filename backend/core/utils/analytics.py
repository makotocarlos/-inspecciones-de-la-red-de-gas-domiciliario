"""
Business Intelligence and Advanced Analytics Module
Professional analytics, KPIs, and business metrics for Gas Inspection Management.
"""

from django.db.models import (
    Count, Avg, Sum, Q, F, ExpressionWrapper,
    FloatField, DurationField, Case, When, Value
)
from django.utils import timezone
from datetime import timedelta, datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger('inspections')


class InspectionAnalytics:
    """
    Advanced analytics for inspection operations.
    Provides business intelligence and KPI tracking.
    """
    
    @staticmethod
    def get_completion_rate(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Calculate inspection completion rate for a period.
        
        Returns:
            Dict with total, completed, pending, and completion percentage
        """
        from inspections.models import Inspection, InspectionStatus
        
        inspections = Inspection.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        total = inspections.count()
        completed = inspections.filter(status=InspectionStatus.COMPLETED).count()
        pending = inspections.filter(status=InspectionStatus.PENDING).count()
        in_progress = inspections.filter(status=InspectionStatus.IN_PROGRESS).count()
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            'total_inspections': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'completion_rate': round(completion_rate, 2),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    @staticmethod
    def get_inspector_performance(inspector_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Analyze inspector performance metrics.
        
        Returns:
            Comprehensive performance statistics
        """
        from inspections.models import Inspection, InspectionStatus, InspectionResult
        
        start_date = timezone.now() - timedelta(days=days)
        
        inspections = Inspection.objects.filter(
            inspector_id=inspector_id,
            scheduled_date__gte=start_date
        )
        
        total = inspections.count()
        completed = inspections.filter(status=InspectionStatus.COMPLETED).count()
        
        # Result distribution
        approved = inspections.filter(result=InspectionResult.APPROVED).count()
        approved_conditions = inspections.filter(result=InspectionResult.APPROVED_WITH_CONDITIONS).count()
        rejected = inspections.filter(result=InspectionResult.REJECTED).count()
        
        # Average completion time
        completed_inspections = inspections.filter(
            status=InspectionStatus.COMPLETED,
            completion_date__isnull=False
        )
        
        avg_completion_time = None
        if completed_inspections.exists():
            completion_times = []
            for inspection in completed_inspections:
                if inspection.completion_date and inspection.scheduled_date:
                    delta = (inspection.completion_date - inspection.scheduled_date).total_seconds() / 3600  # hours
                    completion_times.append(delta)
            
            if completion_times:
                avg_completion_time = round(sum(completion_times) / len(completion_times), 2)
        
        # Quality score (based on approved rate)
        quality_score = (approved / completed * 100) if completed > 0 else 0
        
        return {
            'inspector_id': inspector_id,
            'period_days': days,
            'total_assigned': total,
            'completed': completed,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
            'results': {
                'approved': approved,
                'approved_with_conditions': approved_conditions,
                'rejected': rejected,
            },
            'approval_rate': round((approved / completed * 100) if completed > 0 else 0, 2),
            'quality_score': round(quality_score, 2),
            'avg_completion_time_hours': avg_completion_time,
            'productivity_score': calculate_productivity_score(total, completed, days),
        }
    
    @staticmethod
    def get_trending_issues(days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Identify most common inspection issues/failures.
        
        Returns:
            List of issues sorted by frequency
        """
        from inspections.models import InspectionItem, ItemStatus
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Get failed items with annotations
        failed_items = InspectionItem.objects.filter(
            inspection__scheduled_date__gte=start_date,
            status=ItemStatus.FAIL
        ).values(
            'description'
        ).annotate(
            count=Count('id'),
            failure_rate=Count('id') * 100.0 / Count('inspection__id', distinct=True)
        ).order_by('-count')[:limit]
        
        return list(failed_items)
    
    @staticmethod
    def get_geographic_distribution() -> List[Dict[str, Any]]:
        """
        Analyze inspection distribution by geographic location.
        
        Returns:
            List of locations with inspection counts
        """
        from inspections.models import Inspection
        
        distribution = Inspection.objects.values(
            'address_department',
            'address_city'
        ).annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            pending=Count('id', filter=Q(status='PENDING'))
        ).order_by('-total')
        
        return list(distribution)
    
    @staticmethod
    def get_gas_type_statistics() -> Dict[str, Any]:
        """
        Analyze inspections by gas type.
        
        Returns:
            Statistics grouped by gas type
        """
        from inspections.models import Inspection, InspectionResult
        
        gas_types = Inspection.objects.values('gas_type').annotate(
            total=Count('id'),
            approved=Count('id', filter=Q(result=InspectionResult.APPROVED)),
            rejected=Count('id', filter=Q(result=InspectionResult.REJECTED)),
            avg_score=Avg('inspection_score')
        ).order_by('-total')
        
        return {
            'by_gas_type': list(gas_types),
            'total_types': gas_types.count()
        }
    
    @staticmethod
    def get_time_series_data(days: int = 90, interval: str = 'day') -> List[Dict[str, Any]]:
        """
        Generate time series data for inspections.
        
        Args:
            days: Number of days to include
            interval: 'day', 'week', or 'month'
        
        Returns:
            Time series data with counts per interval
        """
        from inspections.models import Inspection
        from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
        
        start_date = timezone.now() - timedelta(days=days)
        
        trunc_function = {
            'day': TruncDate,
            'week': TruncWeek,
            'month': TruncMonth
        }.get(interval, TruncDate)
        
        data = Inspection.objects.filter(
            created_at__gte=start_date
        ).annotate(
            period=trunc_function('created_at')
        ).values('period').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            pending=Count('id', filter=Q(status='PENDING'))
        ).order_by('period')
        
        return list(data)
    
    @staticmethod
    def get_revenue_projections(months: int = 12) -> Dict[str, Any]:
        """
        Calculate revenue projections based on inspection fees.
        
        Args:
            months: Number of months to project
        
        Returns:
            Revenue analysis and projections
        """
        from inspections.models import Inspection
        
        # Historical data (last 6 months)
        historical_start = timezone.now() - timedelta(days=180)
        historical_inspections = Inspection.objects.filter(
            created_at__gte=historical_start
        )
        
        avg_inspections_per_month = historical_inspections.count() / 6
        avg_inspection_fee = Decimal('150000')  # COP
        
        # Projections
        monthly_projected_revenue = avg_inspections_per_month * avg_inspection_fee
        annual_projected_revenue = monthly_projected_revenue * 12
        
        return {
            'historical_period_months': 6,
            'avg_inspections_per_month': round(avg_inspections_per_month, 2),
            'avg_fee_cop': float(avg_inspection_fee),
            'monthly_projected_revenue_cop': float(monthly_projected_revenue),
            'annual_projected_revenue_cop': float(annual_projected_revenue),
            'projection_period_months': months,
        }


class KPIDashboard:
    """
    Key Performance Indicators Dashboard
    Provides real-time KPIs for management.
    """
    
    @staticmethod
    def get_current_kpis() -> Dict[str, Any]:
        """
        Get current KPIs for the dashboard.
        
        Returns:
            Comprehensive KPI metrics
        """
        from inspections.models import Inspection
        from users.models import CustomUser
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=now.weekday())
        month_start = now.replace(day=1)
        
        # Daily KPIs
        today_inspections = Inspection.objects.filter(scheduled_date__gte=today_start).count()
        today_completed = Inspection.objects.filter(
            scheduled_date__gte=today_start,
            status='COMPLETED'
        ).count()
        
        # Weekly KPIs
        week_inspections = Inspection.objects.filter(scheduled_date__gte=week_start).count()
        week_completed = Inspection.objects.filter(
            scheduled_date__gte=week_start,
            status='COMPLETED'
        ).count()
        
        # Monthly KPIs
        month_inspections = Inspection.objects.filter(scheduled_date__gte=month_start).count()
        month_completed = Inspection.objects.filter(
            scheduled_date__gte=month_start,
            status='COMPLETED'
        ).count()
        
        # Active users
        active_inspectors = CustomUser.objects.filter(
            role='INSPECTOR',
            is_active=True
        ).count()
        
        active_clients = CustomUser.objects.filter(
            role='USER',
            is_active=True
        ).count()
        
        return {
            'timestamp': now.isoformat(),
            'daily': {
                'inspections_scheduled': today_inspections,
                'inspections_completed': today_completed,
                'completion_rate': round((today_completed / today_inspections * 100) if today_inspections > 0 else 0, 2)
            },
            'weekly': {
                'inspections_scheduled': week_inspections,
                'inspections_completed': week_completed,
                'completion_rate': round((week_completed / week_inspections * 100) if week_inspections > 0 else 0, 2)
            },
            'monthly': {
                'inspections_scheduled': month_inspections,
                'inspections_completed': month_completed,
                'completion_rate': round((month_completed / month_inspections * 100) if month_inspections > 0 else 0, 2)
            },
            'resources': {
                'active_inspectors': active_inspectors,
                'active_clients': active_clients,
            }
        }
    
    @staticmethod
    def get_alerts() -> List[Dict[str, Any]]:
        """
        Get system alerts and warnings.
        
        Returns:
            List of active alerts
        """
        from inspections.models import Inspection
        
        alerts = []
        now = timezone.now()
        
        # Overdue inspections
        overdue = Inspection.objects.filter(
            status='PENDING',
            scheduled_date__lt=now
        ).count()
        
        if overdue > 0:
            alerts.append({
                'type': 'warning',
                'category': 'operations',
                'message': f'{overdue} inspecciones vencidas requieren atención',
                'count': overdue,
                'priority': 'high'
            })
        
        # Inspections due today
        today = Inspection.objects.filter(
            status='PENDING',
            scheduled_date__date=now.date()
        ).count()
        
        if today > 0:
            alerts.append({
                'type': 'info',
                'category': 'schedule',
                'message': f'{today} inspecciones programadas para hoy',
                'count': today,
                'priority': 'medium'
            })
        
        # Low completion rate (< 70% this week)
        week_start = now - timedelta(days=now.weekday())
        week_inspections = Inspection.objects.filter(scheduled_date__gte=week_start)
        week_total = week_inspections.count()
        week_completed = week_inspections.filter(status='COMPLETED').count()
        
        if week_total > 0:
            completion_rate = (week_completed / week_total) * 100
            if completion_rate < 70:
                alerts.append({
                    'type': 'warning',
                    'category': 'performance',
                    'message': f'Tasa de completación semanal baja: {completion_rate:.1f}%',
                    'value': completion_rate,
                    'priority': 'high'
                })
        
        return alerts


def calculate_productivity_score(total: int, completed: int, days: int) -> float:
    """
    Calculate productivity score based on completions.
    
    Args:
        total: Total assignments
        completed: Completed inspections
        days: Time period in days
    
    Returns:
        Productivity score (0-100)
    """
    if total == 0 or days == 0:
        return 0.0
    
    completion_rate = (completed / total) * 100
    daily_average = completed / days
    
    # Expected: 3 inspections per day
    expected_daily = 3
    efficiency = (daily_average / expected_daily) * 100
    
    # Weighted score: 60% completion rate + 40% efficiency
    score = (completion_rate * 0.6) + (min(efficiency, 100) * 0.4)
    
    return round(min(score, 100), 2)


def generate_executive_summary(days: int = 30) -> Dict[str, Any]:
    """
    Generate executive summary report.
    
    Args:
        days: Number of days to include in report
    
    Returns:
        Comprehensive executive summary
    """
    start_date = timezone.now() - timedelta(days=days)
    end_date = timezone.now()
    
    analytics = InspectionAnalytics()
    kpi = KPIDashboard()
    
    completion_data = analytics.get_completion_rate(start_date, end_date)
    gas_stats = analytics.get_gas_type_statistics()
    trending_issues = analytics.get_trending_issues(days)
    current_kpis = kpi.get_current_kpis()
    alerts = kpi.get_alerts()
    
    return {
        'report_date': timezone.now().isoformat(),
        'period': {
            'days': days,
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'overview': completion_data,
        'current_kpis': current_kpis,
        'gas_type_analysis': gas_stats,
        'trending_issues': trending_issues,
        'alerts': alerts,
    }
