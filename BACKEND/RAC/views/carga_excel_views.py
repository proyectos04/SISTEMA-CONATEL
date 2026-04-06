import io
import openpyxl
import logging
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Prefetch
from RAC.services.constants import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from RAC.models import Employee, AsigTrabajo
from RAC.serializers.carga_excel_serializers import CargaMasivaExcelSerializer

logger = logging.getLogger(__name__)

@extend_schema(
    tags=["Reportes"],
    summary="Generar Excel (XLSX) de carga masiva",
)
@api_view(['GET'])
@permission_classes([AllowAny])
def exportar_beneficios_xlsx(request):
    try:
        filtro_asignaciones = AsigTrabajo.objects.select_related(
            'Dependencia', 'DireccionGeneral', 'tiponominaid'
        )
        empleados = Employee.objects.filter(
            assignments__isnull=False
        ).prefetch_related(
            Prefetch('assignments', queryset=filtro_asignaciones)
        ).distinct()
        serializer = CargaMasivaExcelSerializer(empleados, many=True)
        datos_formateados = serializer.data
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Carga Masiva"
        if datos_formateados:
            cabeceras = list(datos_formateados[0].keys())
            ws.append(cabeceras)

            for item in datos_formateados:
                ws.append([
                    item.get('Cedula', ''), 
                    item.get('Name_Com', ''), 
                    item.get('Code', ''), 
                    item.get('Location_Physical', ''), 
                    item.get('Location_Admin', ''), 
                    item.get('Estatus', ''), 
                    item.get('ESTADOS', ''), 
                    item.get('typeNomina', '')
                ])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        fecha_str = timezone.now().strftime("%d_%m_%Y")
        filename = f"carga_masiva_beneficios_{fecha_str}.xlsx"
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Error al generar el XLSX de beneficios: {str(e)}")
        return Response({
            'status': "error",
            'message': f"Error interno al generar el reporte: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)