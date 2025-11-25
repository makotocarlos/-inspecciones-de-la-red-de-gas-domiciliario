"""
Email Service
Handles sending emails with templates
"""
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.conf import settings
from django.utils import timezone
from .models import Notification, EmailTemplate
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails
    """
    
    @staticmethod
    def send_email(
        to_email,
        subject,
        html_content,
        text_content=None,
        from_email=None,
        user=None,
        inspection=None
    ):
        """
        Send an email and create notification record
        """
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content or html_content,
                from_email=from_email,
                to=[to_email]
            )
            
            # Attach HTML version
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            
            # Send email
            msg.send(fail_silently=False)
            
            # Create notification record
            if user:
                Notification.objects.create(
                    user=user,
                    notification_type=Notification.Type.EMAIL,
                    status=Notification.Status.SENT,
                    title=subject,
                    message=text_content or html_content[:500],
                    email_to=to_email,
                    email_subject=subject,
                    inspection=inspection,
                    sent_at=timezone.now()
                )
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            
            # Create failed notification record
            if user:
                Notification.objects.create(
                    user=user,
                    notification_type=Notification.Type.EMAIL,
                    status=Notification.Status.FAILED,
                    title=subject,
                    message=text_content or html_content[:500],
                    email_to=to_email,
                    email_subject=subject,
                    inspection=inspection,
                    error_message=str(e)
                )
            
            return False, str(e)
    
    @staticmethod
    def send_template_email(template_type, to_email, context_data, user=None, inspection=None):
        """
        Send an email using a template
        """
        try:
            # Get template
            email_template = EmailTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
            
            # Render subject
            subject_template = Template(email_template.subject)
            subject = subject_template.render(Context(context_data))
            
            # Render HTML content
            html_template = Template(email_template.html_content)
            html_content = html_template.render(Context(context_data))
            
            # Render text content
            text_content = None
            if email_template.text_content:
                text_template = Template(email_template.text_content)
                text_content = text_template.render(Context(context_data))
            
            # Send email
            return EmailService.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                user=user,
                inspection=inspection
            )
            
        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template not found: {template_type}")
            return False, f"Template not found: {template_type}"
        except Exception as e:
            logger.error(f"Error sending template email: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        context = {
            'user_name': user.get_full_name() or user.email,
            'email': user.email,
            'site_url': settings.FRONTEND_URL,
        }
        
        return EmailService.send_template_email(
            template_type=EmailTemplate.TemplateType.WELCOME,
            to_email=user.email,
            context_data=context,
            user=user
        )
    
    @staticmethod
    def send_verification_email(user, verification_token):
        """Send email verification"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        context = {
            'user_name': user.get_full_name() or user.email,
            'verification_url': verification_url,
            'site_url': settings.FRONTEND_URL,
        }
        
        return EmailService.send_template_email(
            template_type=EmailTemplate.TemplateType.VERIFICATION,
            to_email=user.email,
            context_data=context,
            user=user
        )
    
    @staticmethod
    def send_password_reset_email(user, reset_token):
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        context = {
            'user_name': user.get_full_name() or user.email,
            'reset_url': reset_url,
            'site_url': settings.FRONTEND_URL,
        }
        
        return EmailService.send_template_email(
            template_type=EmailTemplate.TemplateType.PASSWORD_RESET,
            to_email=user.email,
            context_data=context,
            user=user
        )
    
    @staticmethod
    def send_inspection_scheduled_email(inspection):
        """Send email when inspection is scheduled"""
        context = {
            'user_name': inspection.user.get_full_name() or inspection.user.email,
            'inspector_name': inspection.inspector.get_full_name() if inspection.inspector else 'Por asignar',
            'inspection_date': inspection.scheduled_date.strftime('%d/%m/%Y %H:%M') if inspection.scheduled_date else 'Por definir',
            'address': inspection.address,
            'site_url': settings.FRONTEND_URL,
            'inspection_url': f"{settings.FRONTEND_URL}/inspections/{inspection.id}",
        }
        
        return EmailService.send_template_email(
            template_type=EmailTemplate.TemplateType.INSPECTION_SCHEDULED,
            to_email=inspection.user.email,
            context_data=context,
            user=inspection.user,
            inspection=inspection
        )
    
    @staticmethod
    def send_inspection_reminder_email(inspection):
        """Send reminder email before inspection"""
        context = {
            'user_name': inspection.user.get_full_name() or inspection.user.email,
            'inspector_name': inspection.inspector.get_full_name() if inspection.inspector else 'Inspector',
            'inspection_date': inspection.scheduled_date.strftime('%d/%m/%Y %H:%M') if inspection.scheduled_date else 'Fecha',
            'address': inspection.address,
            'site_url': settings.FRONTEND_URL,
            'inspection_url': f"{settings.FRONTEND_URL}/inspections/{inspection.id}",
        }
        
        return EmailService.send_template_email(
            template_type=EmailTemplate.TemplateType.INSPECTION_REMINDER,
            to_email=inspection.user.email,
            context_data=context,
            user=inspection.user,
            inspection=inspection
        )
    
    @staticmethod
    def send_inspection_completed_email(inspection):
        """Send email when inspection is completed"""
        context = {
            'user_name': inspection.user.get_full_name() or inspection.user.email,
            'inspector_name': inspection.inspector.get_full_name() if inspection.inspector else 'Inspector',
            'result': inspection.get_result_display() if inspection.result else 'Pendiente',
            'score': f"{inspection.total_score}/100" if inspection.total_score else 'N/A',
            'site_url': settings.FRONTEND_URL,
            'inspection_url': f"{settings.FRONTEND_URL}/inspections/{inspection.id}",
        }
        
        template_type = EmailTemplate.TemplateType.INSPECTION_COMPLETED
        if inspection.result == 'APPROVED':
            template_type = EmailTemplate.TemplateType.INSPECTION_APPROVED
        elif inspection.result == 'REJECTED':
            template_type = EmailTemplate.TemplateType.INSPECTION_REJECTED
        
        return EmailService.send_template_email(
            template_type=template_type,
            to_email=inspection.user.email,
            context_data=context,
            user=inspection.user,
            inspection=inspection
        )
    
    @staticmethod
    def send_report_ready_email(report):
        """Send email when report is ready for download"""
        context = {
            'user_name': report.inspection.user.get_full_name() or report.inspection.user.email,
            'report_number': report.report_number,
            'site_url': settings.FRONTEND_URL,
            'report_url': f"{settings.FRONTEND_URL}/reports/{report.id}/download",
        }
        
        return EmailService.send_template_email(
            template_type=EmailTemplate.TemplateType.REPORT_READY,
            to_email=report.inspection.user.email,
            context_data=context,
            user=report.inspection.user,
            inspection=report.inspection
        )
