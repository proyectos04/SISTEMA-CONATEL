from rest_framework import  status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema,OpenApiExample
from django.apps import apps
from django.db.models import  Prefetch

from RAC.serializers.report_serializers import *
from RAC.services.mapa_reporte import *
from RAC.services.constants import *
from  RAC.services.pdf.generators.employee_passive_pdf import EmployeePassivePDFGenerator
from RAC.services.pdf.generators.family_pdf import FamilyPDFGenerator
from RAC.services.pdf.generators.assignment_pdf import AssignmentPDFGenerator
from RAC.services.pdf.generators.graduate_pdf import GraduatePDFGenerator



@extend_schema(
    tags=["Reportes"],
    summary="Generar  de personal pasivo Reporte PDF",
)
@api_view(['POST'])
def generate_pdf_report_passive(request):

    serializer = ReportePDFSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'status': "Error",
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        validated_data = serializer.validated_data
        categoria = validated_data.get('categoria', 'empleados')
        filtros = validated_data.get('filtros', {})
        
        # Categorías soportadas
        categorias_soportadas = ['empleados', 'familiares', 'asignaciones', 'egresados']
        
        if categoria not in categorias_soportadas:
            return Response({
                'status': "Error",
                'message': f"La categoría '{categoria}' no está soportada para PDF. Categorías disponibles: {', '.join(categorias_soportadas)}",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar PDF según la categoría
        if categoria == 'empleados':
            return _generate_employee_passive_pdf(filtros)
        elif categoria == 'familiares':
            return _generate_family_passive_pdf(filtros)
  
        
    except Exception as e:
        import traceback
        return Response({
            'status': "Error",
            'message': str(e),
            'detail': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _generate_employee_passive_pdf(filtros):
    Employee = apps.get_model('RAC', 'Employee')
    AsigTrabajo = apps.get_model('RAC', 'AsigTrabajo')
    OrganismoAdscrito = apps.get_model('RAC', 'OrganismoAdscrito')  # Se añade para consultar los hijos

    # 3. Procesamiento de filtros
    config = MAPA_REPORTES.get('empleados', {})
    filtros_permitidos = config.get('filtros_permitidos', {})
    query_filtros = {}
    asignacion_filtros = {}

    for k, v in filtros.items():
        if v is not None and k in filtros_permitidos:
            campo = filtros_permitidos[k]
            
            # --- NUEVA LÓGICA PARA EL ORGANISMO ADSCRITO ---
            if k == 'OrganismoAdscrito_id':
                # Obtenemos los IDs de los hijos y le sumamos el ID del padre (v)
                hijos_ids = OrganismoAdscrito.objects.filter(parent_id=v).values_list('id', flat=True)
                ids_busqueda = [v] + list(hijos_ids)
                
                # Agregamos __in al campo para buscar en la lista de IDs
                campo_in = f"{campo}__in"
                query_filtros[campo_in] = ids_busqueda
                if 'assignments__' in campo_in:
                    asignacion_filtros[campo_in.replace('assignments__', '')] = ids_busqueda
                    
            # --- LÓGICA ORIGINAL PARA EL RESTO DE LOS FILTROS ---
            else:
                query_filtros[campo] = v
                if 'assignments__' in campo:
                    asignacion_filtros[campo.replace('assignments__', '')] = v

    query_filtros['assignments__Tipo_personal__tipo_personal'] = PERSONAL_PASIVO
    asignacion_filtros['Tipo_personal__tipo_personal'] = PERSONAL_PASIVO

    queryset = Employee.objects.select_related(
        'sexoid', 'estadoCivil'
    ).filter(
        **query_filtros
    ).prefetch_related(
        Prefetch(
            'assignments',
            queryset=AsigTrabajo.objects.filter(**asignacion_filtros).select_related(
                'Dependencia',
                'DireccionGeneral',
                'tiponominaid',
                'Tipo_personal'
            ).order_by('denominacioncargoid__orden_by_cargo','-fecha_actualizacion'),
            to_attr='filtered_assignments'
        )
    ).order_by(
        'cedulaidentidad'
    ).distinct()

    generator = EmployeePassivePDFGenerator(
        employees=list(queryset),
        title="REPORTE DE TRABAJADORES (PASIVO)",
        filters=filtros
    )

    return generator.get_response(as_attachment=True)

def _generate_family_passive_pdf(filtros):
    """Genera el PDF de familiares."""
    Employee = apps.get_model('RAC', 'Employee')
    
    # Obtener empleados con sus familiares
    queryset = Employee.objects.select_related(
        'sexoid',
        'estadoCivil'
    ).prefetch_related(
        'carga_familiar',
        'carga_familiar__parentesco',
        'carga_familiar__sexo',
        'carga_familiar__estadoCivil',
        'assignments',
        'assignments__Dependencia',
        'assignments__DireccionGeneral',
        'assignments__DireccionLinea',
        'assignments__Coordinacion'
        
    ).filter(
        carga_familiar__isnull=False,
        assignments__Tipo_personal__tipo_personal= PERSONAL_PASIVO
    ).distinct()
    
    # Aplicar filtros
    config = MAPA_REPORTES.get('familiares', {})
    filtros_permitidos = config.get('filtros_permitidos', {})
    
    for filtro_key, filtro_value in filtros.items():
        if filtro_value is not None and filtro_key in filtros_permitidos:
            campo_db = filtros_permitidos[filtro_key]
            queryset = queryset.filter(**{campo_db: filtro_value})
    
    queryset = queryset.order_by('apellidos', 'nombres')
    
    generator = FamilyPDFGenerator(
        employees=queryset,
        title="Reporte de Familiares",
        filters=filtros
    )
    
    return generator.get_response(as_attachment=True)
