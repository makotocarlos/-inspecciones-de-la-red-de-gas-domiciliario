"""
Views for Reports app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from django.core.files.base import ContentFile
from core.utils.permissions import IsAdminOrInspector, IsOwnerOrInspectorOrAdmin
from core.utils.response import APIResponse
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer
from .services import InspectionReportGenerator
import logging

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PDF reports
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'generate']:
            return [IsAdminOrInspector()]
        return [IsOwnerOrInspectorOrAdmin()]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Report.objects.select_related(
            'inspection', 'generated_by', 'inspection__user', 'inspection__inspector'
        )
        
        if user.is_admin:
            return queryset
        elif user.is_inspector:
            return queryset.filter(inspection__inspector=user)
        else:
            return queryset.filter(inspection__user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportSerializer
    
    def create(self, request, *args, **kwargs):
        """Create and generate a report"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create report
        report = serializer.save(generated_by=request.user, status=Report.Status.GENERATING)
        
        try:
            # Generate PDF
            generator = InspectionReportGenerator(report.inspection)
            pdf_data = generator.generate()
            
            # Save PDF file
            filename = f"reporte_{report.report_number}.pdf"
            report.file.save(filename, ContentFile(pdf_data), save=False)
            report.file_size = len(pdf_data)
            report.status = Report.Status.COMPLETED
            report.save()
            
            logger.info(f"Report {report.report_number} generated successfully by {request.user.email}")
            
            return APIResponse.created(
                ReportSerializer(report).data,
                message="Reporte generado exitosamente"
            )
            
        except Exception as e:
            logger.error(f"Error generating report {report.id}: {str(e)}")
            report.status = Report.Status.FAILED
            report.error_message = str(e)
            report.save()
            
            return APIResponse.error(
                message="Error al generar el reporte",
                details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download PDF report"""
        report = self.get_object()
        
        if report.status != Report.Status.COMPLETED:
            return APIResponse.error(
                message="El reporte aún no está disponible",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not report.file:
            return APIResponse.error(
                message="Archivo no encontrado",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            return FileResponse(
                report.file.open('rb'),
                as_attachment=True,
                filename=f"reporte_{report.report_number}.pdf",
                content_type='application/pdf'
            )
        except Exception as e:
            logger.error(f"Error downloading report {report.id}: {str(e)}")
            return APIResponse.error(
                message="Error al descargar el reporte",
                details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate a report"""
        report = self.get_object()
        
        # Check permissions
        if not (request.user.is_admin or report.inspection.inspector == request.user):
            return APIResponse.forbidden(
                message="No tiene permisos para regenerar este reporte"
            )
        
        try:
            report.status = Report.Status.GENERATING
            report.save()
            
            # Generate PDF
            generator = InspectionReportGenerator(report.inspection)
            pdf_data = generator.generate()
            
            # Update PDF file
            filename = f"reporte_{report.report_number}.pdf"
            report.file.save(filename, ContentFile(pdf_data), save=False)
            report.file_size = len(pdf_data)
            report.status = Report.Status.COMPLETED
            report.error_message = ''
            report.save()
            
            logger.info(f"Report {report.report_number} regenerated by {request.user.email}")
            
            return APIResponse.success(
                ReportSerializer(report).data,
                message="Reporte regenerado exitosamente"
            )
            
        except Exception as e:
            logger.error(f"Error regenerating report {report.id}: {str(e)}")
            report.status = Report.Status.FAILED
            report.error_message = str(e)
            report.save()
            
            return APIResponse.error(
                message="Error al regenerar el reporte",
                details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
