"""
PDF Generation Service
Professional PDF reports with ReportLab
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Image, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
from django.utils import timezone
from io import BytesIO
import os


class InspectionReportGenerator:
    """
    Generate professional PDF reports for gas inspections
    """
    
    def __init__(self, inspection):
        self.inspection = inspection
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#4299e1'),
            borderWidth=0,
            borderPadding=5,
            backColor=colors.HexColor('#ebf8ff')
        ))
    
    def _create_header(self):
        """Create report header"""
        elements = []
        
        # Company logo (if exists)
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            elements.append(logo)
            elements.append(Spacer(1, 0.2*inch))
        
        # Title
        title = Paragraph(
            "REPORTE DE INSPECCIÓN DE GAS DOMICILIARIO",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        # Report info table
        report_data = [
            ['Número de Reporte:', self.inspection.id],
            ['Fecha de Emisión:', timezone.now().strftime('%d/%m/%Y %H:%M')],
            ['Estado:', self.inspection.get_status_display()],
            ['Resultado:', self.inspection.get_result_display() if self.inspection.result else 'Pendiente']
        ]
        
        report_table = Table(report_data, colWidths=[2.5*inch, 4*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(report_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_client_info(self):
        """Create client information section"""
        elements = []
        
        elements.append(Paragraph("1. INFORMACIÓN DEL CLIENTE", self.styles['SectionHeader']))
        
        client = self.inspection.user
        client_data = [
            ['Nombre Completo:', client.get_full_name()],
            ['Email:', client.email],
            ['Teléfono:', str(client.phone_number) if client.phone_number else 'N/A'],
            ['DNI:', client.dni or 'N/A'],
            ['Dirección:', self.inspection.address],
            ['Barrio:', self.inspection.neighborhood],
            ['Ciudad:', self.inspection.city],
        ]
        
        client_table = Table(client_data, colWidths=[2.5*inch, 4*inch])
        client_table.setStyle(self._get_info_table_style())
        
        elements.append(client_table)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_installation_info(self):
        """Create installation details section"""
        elements = []
        
        elements.append(Paragraph("2. DETALLES DE LA INSTALACIÓN", self.styles['SectionHeader']))
        
        installation_data = [
            ['Tipo de Gas:', self.inspection.get_gas_type_display()],
            ['Año de Instalación:', str(self.inspection.installation_year) if self.inspection.installation_year else 'N/A'],
            ['Material de Tubería:', self.inspection.pipeline_material or 'N/A'],
            ['Presión (PSI):', str(self.inspection.pressure) if self.inspection.pressure else 'N/A'],
            ['Fecha Programada:', self.inspection.scheduled_date.strftime('%d/%m/%Y %H:%M') if self.inspection.scheduled_date else 'N/A'],
            ['Fecha de Inicio:', self.inspection.started_at.strftime('%d/%m/%Y %H:%M') if self.inspection.started_at else 'N/A'],
            ['Fecha de Finalización:', self.inspection.completed_at.strftime('%d/%m/%Y %H:%M') if self.inspection.completed_at else 'N/A'],
        ]
        
        installation_table = Table(installation_data, colWidths=[2.5*inch, 4*inch])
        installation_table.setStyle(self._get_info_table_style())
        
        elements.append(installation_table)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_inspector_info(self):
        """Create inspector information section"""
        elements = []
        
        if not self.inspection.inspector:
            return elements
        
        elements.append(Paragraph("3. INFORMACIÓN DEL INSPECTOR", self.styles['SectionHeader']))
        
        inspector = self.inspection.inspector
        inspector_data = [
            ['Nombre:', inspector.get_full_name()],
            ['Licencia:', inspector.license_number or 'N/A'],
            ['Email:', inspector.email],
            ['Teléfono:', str(inspector.phone_number) if inspector.phone_number else 'N/A'],
        ]
        
        inspector_table = Table(inspector_data, colWidths=[2.5*inch, 4*inch])
        inspector_table.setStyle(self._get_info_table_style())
        
        elements.append(inspector_table)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_inspection_items(self):
        """Create inspection checklist items section"""
        elements = []
        
        items = self.inspection.items.all().order_by('category', 'order')
        
        if not items.exists():
            return elements
        
        elements.append(Paragraph("4. ITEMS DE INSPECCIÓN", self.styles['SectionHeader']))
        
        # Group by category
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        for category, category_items in categories.items():
            # Category header
            elements.append(Paragraph(f"<b>{category}</b>", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Items table
            item_data = [['Item', 'Conforme', 'Puntuación', 'Observaciones']]
            
            for item in category_items:
                item_data.append([
                    item.item_name,
                    '✓ Sí' if item.is_compliant else '✗ No',
                    f"{item.score}/10",
                    item.observations[:50] + '...' if len(item.observations) > 50 else item.observations
                ])
            
            items_table = Table(item_data, colWidths=[2*inch, 1*inch, 1*inch, 2.5*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299e1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_results_section(self):
        """Create results and recommendations section"""
        elements = []
        
        elements.append(Paragraph("5. RESULTADOS Y RECOMENDACIONES", self.styles['SectionHeader']))
        
        # Score
        if self.inspection.total_score:
            score_text = f"<b>Puntuación Total:</b> {self.inspection.total_score}/100"
            elements.append(Paragraph(score_text, self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Result
        if self.inspection.result:
            result_color = {
                'APPROVED': '#48bb78',
                'CONDITIONAL': '#ed8936',
                'REJECTED': '#f56565'
            }.get(self.inspection.result, '#000000')
            
            result_text = f"<b>Resultado:</b> <font color='{result_color}'>{self.inspection.get_result_display()}</font>"
            elements.append(Paragraph(result_text, self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Observations
        if self.inspection.observations:
            elements.append(Paragraph("<b>Observaciones del Inspector:</b>", self.styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph(self.inspection.observations, self.styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Recommendations
        if self.inspection.recommendations:
            elements.append(Paragraph("<b>Recomendaciones:</b>", self.styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph(self.inspection.recommendations, self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_photos_section(self):
        """Create photos section"""
        elements = []
        
        photos = self.inspection.photos.all()
        
        if not photos.exists():
            return elements
        
        elements.append(PageBreak())
        elements.append(Paragraph("6. EVIDENCIA FOTOGRÁFICA", self.styles['SectionHeader']))
        
        for photo in photos:
            try:
                img_path = photo.photo.path
                if os.path.exists(img_path):
                    img = Image(img_path, width=4*inch, height=3*inch)
                    elements.append(img)
                    
                    if photo.caption:
                        caption = Paragraph(f"<i>{photo.caption}</i>", self.styles['Normal'])
                        elements.append(caption)
                    
                    elements.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        return elements
    
    def _create_footer(self):
        """Create report footer with signature"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Signature line
        signature_data = [
            ['_' * 40, '', '_' * 40],
            ['Firma del Inspector', '', 'Firma del Cliente'],
            [self.inspection.inspector.get_full_name() if self.inspection.inspector else '', '', self.inspection.user.get_full_name()],
            [f'Licencia: {self.inspection.inspector.license_number}' if self.inspection.inspector and self.inspection.inspector.license_number else '', '', f'DNI: {self.inspection.user.dni}' if self.inspection.user.dni else '']
        ]
        
        signature_table = Table(signature_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(signature_table)
        
        # Legal disclaimer
        elements.append(Spacer(1, 0.3*inch))
        disclaimer = Paragraph(
            "<i><font size=8>Este reporte ha sido generado por el Sistema de Gestión de Inspecciones de Gas Domiciliario. "
            "La información contenida en este documento es confidencial y está protegida por las leyes aplicables. "
            "Fecha de generación: {}</font></i>".format(timezone.now().strftime('%d/%m/%Y %H:%M:%S')),
            self.styles['Normal']
        )
        elements.append(disclaimer)
        
        return elements
    
    def _get_info_table_style(self):
        """Get common style for info tables"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ])
    
    def generate(self):
        """Generate the PDF report"""
        # Create document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        # Build story
        story = []
        
        # Add sections
        story.extend(self._create_header())
        story.extend(self._create_client_info())
        story.extend(self._create_installation_info())
        story.extend(self._create_inspector_info())
        story.extend(self._create_inspection_items())
        story.extend(self._create_results_section())
        story.extend(self._create_photos_section())
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_data
