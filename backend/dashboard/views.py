"""
Views for Dashboard app
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from core.utils.response import APIResponse
from inspections.models import Inspection
from users.models import CustomUser
from reports.models import Report
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard statistics and metrics
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics based on user role"""
        user = request.user
        
        if user.is_admin:
            return self._get_admin_stats(request)
        elif user.is_inspector:
            return self._get_inspector_stats(request)
        else:
            return self._get_user_stats(request)
    
    def _get_admin_stats(self, request):
        """Get statistics for admin dashboard"""
        # Total counts
        total_inspections = Inspection.objects.count()
        total_users = CustomUser.objects.filter(role=CustomUser.Role.USER).count()
        total_inspectors = CustomUser.objects.filter(role=CustomUser.Role.INSPECTOR).count()
        total_reports = Report.objects.filter(status=Report.Status.COMPLETED).count()
        
        # Inspections by status
        inspections_by_status = {}
        for status_choice in Inspection.Status.choices:
            count = Inspection.objects.filter(status=status_choice[0]).count()
            inspections_by_status[status_choice[0]] = {
                'count': count,
                'label': status_choice[1]
            }
        
        # Inspections by result
        inspections_by_result = {}
        for result_choice in Inspection.Result.choices:
            count = Inspection.objects.filter(result=result_choice[0]).count()
            inspections_by_result[result_choice[0]] = {
                'count': count,
                'label': result_choice[1]
            }
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_inspections = Inspection.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        # Average score
        avg_score = Inspection.objects.filter(
            total_score__isnull=False
        ).aggregate(Avg('total_score'))['total_score__avg'] or 0
        
        # Inspections by gas type
        inspections_by_gas_type = {}
        for gas_type in Inspection.GasType.choices:
            count = Inspection.objects.filter(gas_type=gas_type[0]).count()
            inspections_by_gas_type[gas_type[0]] = {
                'count': count,
                'label': gas_type[1]
            }
        
        # Top inspectors (by completed inspections)
        top_inspectors = CustomUser.objects.filter(
            role=CustomUser.Role.INSPECTOR
        ).annotate(
            completed_count=Count('assigned_inspections', filter=Q(assigned_inspections__status=Inspection.Status.COMPLETED))
        ).order_by('-completed_count')[:5]
        
        top_inspectors_data = [
            {
                'id': str(inspector.id),
                'name': inspector.get_full_name(),
                'completed': inspector.completed_count
            }
            for inspector in top_inspectors
        ]
        
        stats = {
            'totals': {
                'inspections': total_inspections,
                'users': total_users,
                'inspectors': total_inspectors,
                'reports': total_reports
            },
            'inspections_by_status': inspections_by_status,
            'inspections_by_result': inspections_by_result,
            'inspections_by_gas_type': inspections_by_gas_type,
            'recent_activity': {
                'inspections_last_30_days': recent_inspections
            },
            'average_score': round(avg_score, 2),
            'top_inspectors': top_inspectors_data
        }
        
        return APIResponse.success(stats)
    
    def _get_inspector_stats(self, request):
        """Get statistics for inspector dashboard"""
        inspector = request.user
        
        # My inspections counts
        my_inspections = Inspection.objects.filter(inspector=inspector)
        total_assigned = my_inspections.count()
        completed = my_inspections.filter(status=Inspection.Status.COMPLETED).count()
        pending = my_inspections.filter(status=Inspection.Status.PENDING).count()
        in_progress = my_inspections.filter(status=Inspection.Status.IN_PROGRESS).count()
        scheduled = my_inspections.filter(status=Inspection.Status.SCHEDULED).count()
        
        # My inspections by result
        approved = my_inspections.filter(result=Inspection.Result.APPROVED).count()
        conditional = my_inspections.filter(result=Inspection.Result.CONDITIONAL).count()
        rejected = my_inspections.filter(result=Inspection.Result.REJECTED).count()
        
        # Average score
        avg_score = my_inspections.filter(
            total_score__isnull=False
        ).aggregate(Avg('total_score'))['total_score__avg'] or 0
        
        # Upcoming inspections (next 7 days)
        today = timezone.now()
        next_week = today + timedelta(days=7)
        upcoming = my_inspections.filter(
            scheduled_date__gte=today,
            scheduled_date__lte=next_week,
            status__in=[Inspection.Status.SCHEDULED, Inspection.Status.PENDING]
        ).order_by('scheduled_date')[:5]
        
        upcoming_data = [
            {
                'id': str(inspection.id),
                'address': inspection.address,
                'scheduled_date': inspection.scheduled_date.isoformat() if inspection.scheduled_date else None,
                'gas_type': inspection.get_gas_type_display()
            }
            for inspection in upcoming
        ]
        
        # Recent completions (last 10)
        recent_completed = my_inspections.filter(
            status=Inspection.Status.COMPLETED
        ).order_by('-completed_at')[:10]
        
        recent_data = [
            {
                'id': str(inspection.id),
                'address': inspection.address,
                'completed_at': inspection.completed_at.isoformat() if inspection.completed_at else None,
                'result': inspection.get_result_display() if inspection.result else None,
                'score': inspection.total_score
            }
            for inspection in recent_completed
        ]
        
        stats = {
            'totals': {
                'assigned': total_assigned,
                'completed': completed,
                'pending': pending,
                'in_progress': in_progress,
                'scheduled': scheduled
            },
            'by_result': {
                'approved': approved,
                'conditional': conditional,
                'rejected': rejected
            },
            'average_score': round(avg_score, 2),
            'upcoming_inspections': upcoming_data,
            'recent_completions': recent_data
        }
        
        return APIResponse.success(stats)
    
    def _get_user_stats(self, request):
        """Get statistics for user dashboard"""
        user = request.user
        
        # My inspections
        my_inspections = Inspection.objects.filter(user=user)
        total = my_inspections.count()
        pending = my_inspections.filter(status=Inspection.Status.PENDING).count()
        scheduled = my_inspections.filter(status=Inspection.Status.SCHEDULED).count()
        in_progress = my_inspections.filter(status=Inspection.Status.IN_PROGRESS).count()
        completed = my_inspections.filter(status=Inspection.Status.COMPLETED).count()
        
        # Results
        approved = my_inspections.filter(result=Inspection.Result.APPROVED).count()
        conditional = my_inspections.filter(result=Inspection.Result.CONDITIONAL).count()
        rejected = my_inspections.filter(result=Inspection.Result.REJECTED).count()
        
        # Next scheduled inspection
        next_inspection = my_inspections.filter(
            scheduled_date__gte=timezone.now(),
            status__in=[Inspection.Status.SCHEDULED, Inspection.Status.PENDING]
        ).order_by('scheduled_date').first()
        
        next_inspection_data = None
        if next_inspection:
            next_inspection_data = {
                'id': str(next_inspection.id),
                'address': next_inspection.address,
                'scheduled_date': next_inspection.scheduled_date.isoformat() if next_inspection.scheduled_date else None,
                'inspector_name': next_inspection.inspector.get_full_name() if next_inspection.inspector else 'Por asignar'
            }
        
        # Recent inspections
        recent = my_inspections.order_by('-created_at')[:5]
        recent_data = [
            {
                'id': str(inspection.id),
                'address': inspection.address,
                'status': inspection.get_status_display(),
                'created_at': inspection.created_at.isoformat(),
                'result': inspection.get_result_display() if inspection.result else None
            }
            for inspection in recent
        ]
        
        # Available reports
        reports_count = Report.objects.filter(
            inspection__user=user,
            status=Report.Status.COMPLETED
        ).count()
        
        # Unread notifications
        unread_notifications = Notification.objects.filter(
            user=user,
            status__in=[Notification.Status.PENDING, Notification.Status.SENT]
        ).count()
        
        stats = {
            'totals': {
                'all': total,
                'pending': pending,
                'scheduled': scheduled,
                'in_progress': in_progress,
                'completed': completed
            },
            'by_result': {
                'approved': approved,
                'conditional': conditional,
                'rejected': rejected
            },
            'next_inspection': next_inspection_data,
            'recent_inspections': recent_data,
            'reports_count': reports_count,
            'unread_notifications': unread_notifications
        }
        
        return APIResponse.success(stats)
    
    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """Get chart data for dashboard visualizations"""
        user = request.user
        
        if user.is_admin:
            return self._get_admin_chart_data(request)
        elif user.is_inspector:
            return self._get_inspector_chart_data(request)
        else:
            return self._get_user_chart_data(request)
    
    def _get_admin_chart_data(self, request):
        """Get chart data for admin"""
        # Inspections per month (last 12 months)
        months_data = []
        for i in range(11, -1, -1):
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            count = Inspection.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            months_data.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        # Status distribution
        status_data = []
        for status in Inspection.Status.choices:
            count = Inspection.objects.filter(status=status[0]).count()
            status_data.append({
                'status': status[1],
                'count': count
            })
        
        # Result distribution
        result_data = []
        for result in Inspection.Result.choices:
            count = Inspection.objects.filter(result=result[0]).count()
            result_data.append({
                'result': result[1],
                'count': count
            })
        
        return APIResponse.success({
            'monthly_inspections': months_data,
            'status_distribution': status_data,
            'result_distribution': result_data
        })
    
    def _get_inspector_chart_data(self, request):
        """Get chart data for inspector"""
        inspector = request.user
        my_inspections = Inspection.objects.filter(inspector=inspector)
        
        # Completions per month (last 6 months)
        months_data = []
        for i in range(5, -1, -1):
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            count = my_inspections.filter(
                completed_at__gte=month_start,
                completed_at__lt=month_end
            ).count()
            
            months_data.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        # Result distribution
        result_data = []
        for result in Inspection.Result.choices:
            count = my_inspections.filter(result=result[0]).count()
            result_data.append({
                'result': result[1],
                'count': count
            })
        
        return APIResponse.success({
            'monthly_completions': months_data,
            'result_distribution': result_data
        })
    
    def _get_user_chart_data(self, request):
        """Get chart data for user"""
        user = request.user
        my_inspections = Inspection.objects.filter(user=user)
        
        # Status distribution
        status_data = []
        for status in Inspection.Status.choices:
            count = my_inspections.filter(status=status[0]).count()
            if count > 0:
                status_data.append({
                    'status': status[1],
                    'count': count
                })
        
        # Result distribution
        result_data = []
        for result in Inspection.Result.choices:
            count = my_inspections.filter(result=result[0]).count()
            if count > 0:
                result_data.append({
                    'result': result[1],
                    'count': count
                })
        
        return APIResponse.success({
            'status_distribution': status_data,
            'result_distribution': result_data
        })
