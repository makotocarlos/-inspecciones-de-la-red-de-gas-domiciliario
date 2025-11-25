"""
Script to create initial email templates
Run with: python manage.py shell < create_email_templates.py
"""
from notifications.models import EmailTemplate

templates = [
    {
        'name': 'Bienvenida',
        'template_type': EmailTemplate.TemplateType.WELCOME,
        'subject': 'Bienvenido al Sistema de Inspecciones de Gas',
        'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2c5282; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f7fafc; }
        .button { display: inline-block; padding: 12px 24px; background: #4299e1; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Bienvenido!</h1>
        </div>
        <div class="content">
            <h2>Hola {{ user_name }},</h2>
            <p>Gracias por registrarte en nuestro Sistema de Gestión de Inspecciones de Gas Domiciliario.</p>
            <p>Tu cuenta ha sido creada exitosamente con el email: <strong>{{ email }}</strong></p>
            <p>Ahora puedes acceder al sistema y comenzar a gestionar tus inspecciones.</p>
            <a href="{{ site_url }}" class="button">Ir al Sistema</a>
        </div>
        <div class="footer">
            <p>Este es un email automático, por favor no responder.</p>
            <p>&copy; 2024 Sistema de Inspecciones de Gas</p>
        </div>
    </div>
</body>
</html>
        ''',
        'text_content': 'Hola {{ user_name }},\n\nBienvenido al Sistema de Inspecciones de Gas.\nTu email: {{ email }}\n\nAccede en: {{ site_url }}',
        'variables': ['user_name', 'email', 'site_url']
    },
    {
        'name': 'Verificación de Email',
        'template_type': EmailTemplate.TemplateType.VERIFICATION,
        'subject': 'Verifica tu cuenta - Sistema de Inspecciones',
        'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2c5282; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f7fafc; }
        .button { display: inline-block; padding: 12px 24px; background: #48bb78; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Verificación de Cuenta</h1>
        </div>
        <div class="content">
            <h2>Hola {{ user_name }},</h2>
            <p>Por favor verifica tu dirección de email para activar tu cuenta.</p>
            <a href="{{ verification_url }}" class="button">Verificar Email</a>
            <p>O copia este enlace en tu navegador:</p>
            <p><small>{{ verification_url }}</small></p>
        </div>
        <div class="footer">
            <p>Si no creaste esta cuenta, puedes ignorar este email.</p>
        </div>
    </div>
</body>
</html>
        ''',
        'text_content': 'Hola {{ user_name }},\n\nVerifica tu email: {{ verification_url }}',
        'variables': ['user_name', 'verification_url', 'site_url']
    },
    {
        'name': 'Recuperación de Contraseña',
        'template_type': EmailTemplate.TemplateType.PASSWORD_RESET,
        'subject': 'Recuperación de Contraseña',
        'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2c5282; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f7fafc; }
        .button { display: inline-block; padding: 12px 24px; background: #ed8936; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Recuperación de Contraseña</h1>
        </div>
        <div class="content">
            <h2>Hola {{ user_name }},</h2>
            <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
            <a href="{{ reset_url }}" class="button">Restablecer Contraseña</a>
            <p>Este enlace es válido por 1 hora.</p>
        </div>
        <div class="footer">
            <p>Si no solicitaste esto, puedes ignorar este email.</p>
        </div>
    </div>
</body>
</html>
        ''',
        'text_content': 'Hola {{ user_name }},\n\nRestablece tu contraseña: {{ reset_url }}',
        'variables': ['user_name', 'reset_url', 'site_url']
    },
    {
        'name': 'Inspección Programada',
        'template_type': EmailTemplate.TemplateType.INSPECTION_SCHEDULED,
        'subject': 'Tu Inspección ha sido Programada',
        'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2c5282; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f7fafc; }
        .info-box { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4299e1; }
        .button { display: inline-block; padding: 12px 24px; background: #4299e1; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Inspección Programada</h1>
        </div>
        <div class="content">
            <h2>Hola {{ user_name }},</h2>
            <p>Tu inspección de gas ha sido programada con los siguientes detalles:</p>
            <div class="info-box">
                <p><strong>Fecha:</strong> {{ inspection_date }}</p>
                <p><strong>Dirección:</strong> {{ address }}</p>
                <p><strong>Inspector:</strong> {{ inspector_name }}</p>
            </div>
            <p>Por favor asegúrate de estar disponible en la fecha programada.</p>
            <a href="{{ inspection_url }}" class="button">Ver Detalles</a>
        </div>
        <div class="footer">
            <p>Para cualquier cambio, contacta con nosotros.</p>
        </div>
    </div>
</body>
</html>
        ''',
        'text_content': 'Hola {{ user_name }},\n\nInspección programada:\nFecha: {{ inspection_date }}\nDirección: {{ address }}\nInspector: {{ inspector_name }}\n\nVer: {{ inspection_url }}',
        'variables': ['user_name', 'inspector_name', 'inspection_date', 'address', 'site_url', 'inspection_url']
    },
    {
        'name': 'Inspección Completada - Aprobada',
        'template_type': EmailTemplate.TemplateType.INSPECTION_APPROVED,
        'subject': '✅ Tu Inspección ha sido Aprobada',
        'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #48bb78; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f7fafc; }
        .success-box { background: #c6f6d5; padding: 15px; margin: 15px 0; border-left: 4px solid #48bb78; }
        .button { display: inline-block; padding: 12px 24px; background: #48bb78; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Felicitaciones!</h1>
        </div>
        <div class="content">
            <h2>Hola {{ user_name }},</h2>
            <div class="success-box">
                <p><strong>Tu instalación de gas ha sido APROBADA</strong></p>
                <p>Puntuación: {{ score }}</p>
                <p>Inspector: {{ inspector_name }}</p>
            </div>
            <p>Tu instalación de gas cumple con todos los requisitos de seguridad.</p>
            <a href="{{ inspection_url }}" class="button">Ver Detalles</a>
        </div>
        <div class="footer">
            <p>Pronto recibirás el reporte completo.</p>
        </div>
    </div>
</body>
</html>
        ''',
        'text_content': 'Hola {{ user_name }},\n\n¡Tu inspección ha sido APROBADA!\nPuntuación: {{ score }}\nInspector: {{ inspector_name }}\n\nVer: {{ inspection_url }}',
        'variables': ['user_name', 'inspector_name', 'result', 'score', 'site_url', 'inspection_url']
    },
    {
        'name': 'Reporte Disponible',
        'template_type': EmailTemplate.TemplateType.REPORT_READY,
        'subject': 'Tu Reporte de Inspección está Disponible',
        'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2c5282; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f7fafc; }
        .button { display: inline-block; padding: 12px 24px; background: #4299e1; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #718096; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reporte Disponible</h1>
        </div>
        <div class="content">
            <h2>Hola {{ user_name }},</h2>
            <p>Tu reporte de inspección <strong>{{ report_number }}</strong> ya está disponible para descargar.</p>
            <a href="{{ report_url }}" class="button">Descargar Reporte PDF</a>
        </div>
        <div class="footer">
            <p>Guarda este reporte para tus registros.</p>
        </div>
    </div>
</body>
</html>
        ''',
        'text_content': 'Hola {{ user_name }},\n\nTu reporte {{ report_number }} está listo.\nDescargar: {{ report_url }}',
        'variables': ['user_name', 'report_number', 'site_url', 'report_url']
    }
]

print("Creando plantillas de email...")
created = 0
updated = 0

for template_data in templates:
    obj, created_flag = EmailTemplate.objects.get_or_create(
        template_type=template_data['template_type'],
        defaults=template_data
    )
    
    if created_flag:
        created += 1
        print(f"✓ Creada: {template_data['name']}")
    else:
        updated += 1
        # Actualizar si ya existe
        for key, value in template_data.items():
            setattr(obj, key, value)
        obj.save()
        print(f"↻ Actualizada: {template_data['name']}")

print(f"\n✅ Proceso completado: {created} creadas, {updated} actualizadas")
