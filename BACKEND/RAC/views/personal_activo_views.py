from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from RAC.serializers.personal_activo_serializers import *
from django.db.models import Prefetch
from ..models.personal_models import *
from ..models.ubicacion_models import *
from RAC.filters.filters_personal import EmployeeFilter, AsigTrabajoFilter
from ..services.constants import *

from drf_spectacular.utils import extend_schema




import pandas as pd
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from USER.models.user_models import cuenta as User  

class ImportarCargosESPECIALESView(APIView):
    parser_classes = [MultiPartParser]
    serializer_class = CargosUploadSerializer

    def post(self, request):
        errores = []
        creados = 0
        
        serializer = CargosUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        archivo = request.FILES['archivo']
        
        try:
            df = pd.read_excel(archivo) if not archivo.name.endswith('.csv') else pd.read_csv(archivo)
            df.columns = df.columns.str.strip().str.lower()
            
            def normalizar(texto):
                if not texto or pd.isna(texto): return ""
                return " ".join(str(texto).split()).upper()

            # CACHÉ EXTENDIDA
            cache = {
                'cargos': {normalizar(obj.cargo): obj for obj in Denominacioncargo.objects.all()},
                'especificos': {normalizar(obj.cargo): obj for obj in Denominacioncargoespecifico.objects.all()},
                'nominas': {normalizar(obj.nomina): obj for obj in Tiponomina.objects.all()},
                'organismos': {normalizar(obj.Organismoadscrito): obj for obj in OrganismoAdscrito.objects.all() if obj.Organismoadscrito},
                'direcciones': {normalizar(obj.direccion_general): obj for obj in DireccionGeneral.objects.all() if obj.direccion_general},
                'estatus': {normalizar(obj.estatus): obj for obj in Estatus.objects.all()},
                'grados': {normalizar(obj.grado): obj for obj in Grado.objects.all()},
                'tipos_p': {normalizar(obj.tipo_personal): obj for obj in Tipo_personal.objects.all()},
                'dependencias': {normalizar(obj.dependencia): obj for obj in Dependencias.objects.all()},
                'lineas': {normalizar(obj.direccion_linea): obj for obj in DireccionLinea.objects.all()},
                'coordinaciones': {normalizar(obj.coordinacion): obj for obj in Coordinaciones.objects.all()},
            }

            tp_default = Tipo_personal.objects.filter(id=2).first()
            dep_default = Dependencias.objects.filter(id=1).first() 
            usuario_historial = User.objects.filter(id=10).first()

            if not usuario_historial:
                raise Exception("Error crítico: No existe el usuario con ID 10.")

            def generar_codigo_especial(prefijo):
                ultimo_registro = AsigTrabajo.objects.filter(codigo__startswith=prefijo).order_by('-codigo').first()
                if ultimo_registro and ultimo_registro.codigo:
                    try:
                        numero_actual = int(ultimo_registro.codigo.split('_')[1])
                        nuevo_numero = numero_actual + 1
                    except (IndexError, ValueError):
                        nuevo_numero = 1
                else:
                    nuevo_numero = 1
                return f"{prefijo}_{nuevo_numero:04d}"

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        def buscar(cat, col_name):
                            val = row.get(col_name)
                            if pd.isna(val) or str(val).strip() == "":
                                return None
                            return cache[cat].get(normalizar(val))

                        # --- LÓGICA DE CÉDULA Y ESTATUS (MODIFICADA) ---
                        estatus_val = normalizar(row.get('estatus'))
                        cedula_raw = row.get('cedula')
                        empleado = None
                        
                        if estatus_val == "VACANTE":
                            # Si es VACANTE, la cédula debe estar vacía
                            if not pd.isna(cedula_raw) and str(cedula_raw).strip() != "":
                                raise ValueError(f"El estatus es VACANTE, pero la cédula contiene datos: {cedula_raw}. Debe estar vacía.")
                            empleado = None
                        else:
                            # Si NO es VACANTE, la cédula es obligatoria
                            if not pd.isna(cedula_raw) and str(cedula_raw).strip() != "":
                                cedula_clean = str(cedula_raw).split('.')[0].strip()
                                empleado = Employee.objects.filter(cedulaidentidad=cedula_clean).first()
                                
                                if not empleado:
                                    raise ValueError(f"La cédula '{cedula_clean}' no existe en la base de datos de empleados.")
                            else:
                                raise ValueError(f"Para el estatus '{estatus_val}' la cédula es obligatoria.")
                        # -----------------------------------------------

                        # Lógica de Nómina y Código
                        nomina_obj = buscar('nominas', 'nomina')
                        nombre_nomina = normalizar(row.get('nomina'))
                        codigo_final = row.get('codigo')
                        
                        if nombre_nomina == "COMISION DE SERVICIO":
                            codigo_final = generar_codigo_especial("CS")
                        elif nombre_nomina == "HONORARIOS PROFESIONALES":
                            codigo_final = generar_codigo_especial("HP")
                        
                        # Validar si el código ya existe
                        if AsigTrabajo.objects.filter(codigo=codigo_final, tiponominaid=nomina_obj).exists():
                            if any(x in str(codigo_final) for x in ["CS_", "HP_"]):
                                codigo_final = generar_codigo_especial(str(codigo_final).split('_')[0])
                            else:
                                raise ValueError(f"El código '{codigo_final}' ya existe para la nómina '{nombre_nomina}'.")

                        cargo_obj = buscar('cargos', 'cargo')
                        especifico_obj = buscar('especificos', 'cargo_especifico')
                        estatus_obj = buscar('estatus', 'estatus')

                        if not all([cargo_obj, especifico_obj, nomina_obj, estatus_obj]):
                            f = []
                            if not cargo_obj: f.append(f"Cargo: '{row.get('cargo')}'")
                            if not especifico_obj: f.append(f"Específico: '{row.get('cargo_especifico')}'")
                            if not nomina_obj: f.append(f"Nómina: '{row.get('nomina')}'")
                            if not estatus_obj: f.append(f"Estatus: '{row.get('estatus')}'")
                            raise ValueError(f"Faltan datos críticos: {', '.join(f)}")

                        # CREACIÓN
                        asignacion = AsigTrabajo(
                            codigo=codigo_final,
                            employee=empleado,
                            denominacioncargoid=cargo_obj,
                            denominacioncargoespecificoid=especifico_obj,
                            tiponominaid=nomina_obj,
                            estatusid=estatus_obj,
                            OrganismoAdscritoid=buscar('organismos', 'organismo'),
                            DireccionGeneral=buscar('direcciones', 'direccion_general'),
                            Dependencia=buscar('dependencias', 'dependencia') or dep_default,
                            DireccionLinea=buscar('lineas', 'direccion_linea'),
                            Coordinacion=buscar('coordinaciones', 'coordinacion'),
                            gradoid=buscar('grados', 'grado'),
                            Tipo_personal=buscar('tipos_p', 'tipo_personal') or tp_default,
                            observaciones=str(row.get('observaciones', ''))[:255] if not pd.isna(row.get('observaciones')) else ''
                        )
                        
                        asignacion._history_user = usuario_historial
                        asignacion.save()
                        creados += 1

                    except Exception as e:
                        errores.append(f"Fila {index + 2}: {str(e)}")

                if errores:
                    raise Exception("Errores en el procesamiento del archivo.")

            return Response({"mensaje": f"Se crearon {creados} registros con éxito."}, status=201)

        except Exception as e:
            return Response({
                "error": "Operación cancelada", 
                "detalles": errores if errores else [str(e)]
            }, status=400)

# carga masiva de cargos 

class ImportarCargosView(APIView):
    parser_classes = [MultiPartParser]
    serializer_class = CargosUploadSerializer

    def post(self, request):
        errores = []
        creados = 0
        
        serializer = CargosUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        archivo = request.FILES['archivo']
        
        try:
            df = pd.read_excel(archivo) if not archivo.name.endswith('.csv') else pd.read_csv(archivo)
            df.columns = df.columns.str.strip().str.lower()
            
            cache = {
                'cargos': {str(obj.cargo).strip().upper(): obj for obj in Denominacioncargo.objects.all()},
                'especificos': {str(obj.cargo).strip().upper(): obj for obj in Denominacioncargoespecifico.objects.all()},
                'nominas': {str(obj.nomina).strip().upper(): obj for obj in Tiponomina.objects.all()},
                'organismos': {str(obj.Organismoadscrito).strip().upper(): obj for obj in OrganismoAdscrito.objects.all() if obj.Organismoadscrito},
                'direcciones': {str(obj.direccion_general).strip().upper(): obj for obj in DireccionGeneral.objects.all() if obj.direccion_general},
                'estatus': {str(obj.estatus).strip().upper(): obj for obj in Estatus.objects.all()},
                'grados': {str(obj.grado).strip().upper(): obj for obj in Grado.objects.all()},
                'tipos_p': {str(obj.tipo_personal).strip().upper(): obj for obj in Tipo_personal.objects.all()},
            }

            tp_default = Tipo_personal.objects.filter(id=2).first()
            
            usuario_historial = User.objects.filter(id=10).first()

            if not usuario_historial:
                raise Exception("Error crítico: No existe el usuario con ID 10 en la tabla 'cuenta'.")

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        def buscar(cat, col_name):
                            val = row.get(col_name)
                            if pd.isna(val) or str(val).strip() == "":
                                return None
                            limpio = str(val).strip().upper()
                            return cache[cat].get(limpio)

                        cedula = str(row.get('cedula', '')).strip().split('.')[0]
                        empleado = Employee.objects.filter(cedulaidentidad=cedula).first()

                        cargo_obj = buscar('cargos', 'cargo')
                        especifico_obj = buscar('especificos', 'cargo_especifico')
                        nomina_obj = buscar('nominas', 'nomina')
                        estatus_obj = buscar('estatus', 'estatus')

                        if not all([cargo_obj, especifico_obj, nomina_obj, estatus_obj]):
                            f = []
                            if not cargo_obj: f.append(f"Cargo: '{row.get('cargo')}'")
                            if not especifico_obj: f.append(f"Específico: '{row.get('cargo_especifico')}'")
                            if not nomina_obj: f.append(f"Nómina: '{row.get('nomina')}'")
                            if not estatus_obj: f.append(f"Estatus: '{row.get('estatus')}'")
                            raise ValueError(f"Faltan datos críticos: {', '.join(f)}")

                        asignacion = AsigTrabajo(
                            codigo=row.get('codigo'),
                            employee=empleado,
                            denominacioncargoid=cargo_obj,
                            denominacioncargoespecificoid=especifico_obj,
                            tiponominaid=nomina_obj,
                            estatusid=estatus_obj,
                            OrganismoAdscritoid=buscar('organismos', 'organismo'),
                            DireccionGeneral=buscar('direcciones', 'direccion_general'),
                            gradoid=buscar('grados', 'grado'),
                            Tipo_personal=buscar('tipos_p', 'tipo_personal') or tp_default,
                            observaciones=str(row.get('observaciones', ''))[:255] if not pd.isna(row.get('observaciones')) else ''
                        )
                        
                        asignacion._history_user = usuario_historial
                        asignacion.save()
                        creados += 1

                    except Exception as e:
                        errores.append(f"Fila {index + 2}: {str(e)}")

                if errores:
                    raise Exception("Errores encontrados en el procesamiento.")

            return Response({"mensaje": f"Se crearon {creados} registros correctamente."}, status=201)

        except Exception as e:
            return Response({
                "error": "Operación cancelada",
                "detalles": errores if errores else [str(e)]
            }, status=400)



# CARGA PERSONAL 
@extend_schema(
    tags=["Gestion de Empleado"],
    summary="Registrar datos personales de empleadoas",
    description="Permite registrar los datos personales del empleado",
    request=CargaMasivaSerializer,
)
class ImportEmployeesView(APIView):
    def post(self, request):
        serializer = CargaMasivaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['archivo']
        
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file)

            # Mapeo de Sexo: Convertimos etiquetas a IDs (1: Femenino, 2: Masculino)
            # Asumiendo que en el Excel la columna se llama 'sexo'
            gender_map = {
                'femenino': 1,
                'Femenino': 1,
                'FEMENINO': 1,
                'masculino': 2,
                'Masculino': 2,
                'MASCULINO': 2,
                'F': 1,
                'f': 1,
                'm': 2,
                'M': 2
            }

            employees_to_create = []
            errors = []

            for index, row in df.iterrows():
                try:
                    # Helper to clean and parse dates from various formats
                    def parse_date(val):
                        if pd.isna(val):
                            return None
                        # If it's already a Timestamp or datetime
                        if isinstance(val, (pd.Timestamp, datetime)):
                            try:
                                return pd.to_datetime(val).date()
                            except Exception:
                                return None

                        s = str(val).strip()
                        # Remove smart quotes and extra quote chars
                        for ch in ['\u201c','\u201d','\u2018','\u2019','"',"'"]:
                            s = s.replace(ch, '')
                        s = s.strip()

                        ts = pd.to_datetime(s, dayfirst=True, errors='coerce')
                        if pd.isna(ts):
                            return None
                        return ts.date()

                    # Obtener ID de sexo basado en el mapeo
                    sexo_raw = row.get('sexo', '')
                    sexo_id = gender_map.get(sexo_raw)
                    if not sexo_id:
                        errors.append(f"Fila {index}: Sexo '{sexo_raw}' no válido.")
                        continue

                    # Parsear fechas (acepta dd/mm/yyyy y limpia comillas tipográficas)
                    fecha_nac = parse_date(row.get('fecha_nacimiento'))
                    fecha_ingreso = parse_date(row.get('fechaingresoorganismo'))

                    if row.get('fecha_nacimiento') and fecha_nac is None:
                        errors.append(f"Fila {index}: fecha_nacimiento '{row.get('fecha_nacimiento')}' no válido.")

                    if row.get('fechaingresoorganismo') and fecha_ingreso is None:
                        errors.append(f"Fila {index}: fechaingresoorganismo '{row.get('fechaingresoorganismo')}' no válido.")

                    # Crear instancia del modelo (sin guardar en DB aún para optimizar)
                    employee = Employee(
                        cedulaidentidad=row.get('CEDULA DE IDENTIDAD'),
                        nombres=row.get('NOMBRES'),
                        apellidos=row.get('APELLIDOS'),
                        fecha_nacimiento=fecha_nac,
                        fechaingresoorganismo=fecha_ingreso,
                        sexoid_id=sexo_id, 
                        estadoCivil_id=1
                    )
                    employees_to_create.append(employee)

                except Exception as e:
                    errors.append(f"Fila {index}: {str(e)}")

            # Carga masiva en la base de datos
            if employees_to_create:
                Employee.objects.bulk_create(employees_to_create, ignore_conflicts=True)

            return Response({
                "message": f"Se procesaron {len(employees_to_create)} empleados.",
                "errors": errors
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Error al leer el archivo: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# ......................................................................


@extend_schema(
    tags=["Gestion de Empleado"],
    summary="Registrar datos personales de empleadoa",
    description="Permite registrar los datos personales del empleado",
    request=EmployeeCreateUpdateSerializer,
)
@api_view(['POST'])
def create_employee(request):
    serializer = EmployeeCreateUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({
                'status': "Created",
                "message": "Datos de empleado registrados correctamente",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': "Error",
                'message': str(e),
                
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        error_dict = serializer.errors 
        first_error_field = list(error_dict.values())[0] 
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

        return Response({
            'status': "Error",
            'message': clean_message, 
      
        }, status=status.HTTP_400_BAD_REQUEST)

#  ACTUALIZACION DE DATOS PERSONALES DEL EMPLEADO       
@extend_schema(
    tags=["Gestion de Empleado","Gestion de Personal Pasivo"],
    summary="Editar un empleado",
    description="Actualiza los datos de un empleado existente identificado por su id",
    request=EmployeeCreateUpdateSerializer, 
) 
@api_view(['PATCH'])
def update_employee(request, id):
    empleado = get_object_or_404(Employee, id=id)
    serializer = EmployeeCreateUpdateSerializer(empleado, data=request.data, partial=True)
    
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "OK",
            'message': "Empleado actualizado correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)
        
    except ValidationError:
        error_dict = serializer.errors
        first_error_field = list(error_dict.values())[0]
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field
        
        return Response({
            'status': "Error",
            'message': clean_message,
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'status': "Error",
            'message': "No se pudo actualizar el registro.",
            'debug': str(e),
         
        }, status=status.HTTP_400_BAD_REQUEST)
    
# LISTADO DE EMPLEADOS

@extend_schema(
    tags=["Gestion de Empleado"],
    summary="Buscar empleado por cédula",
    description="Devuelve los datos de un empleado identificado por su cédula",
    request=EmployeeListSerializer,
)
@api_view(['GET'])
def retrieve_employee(request, cedulaidentidad):
    try:
        empleado = Employee.objects.select_related(
            'sexoid', 'estadoCivil'
        ).prefetch_related(
           'datos_vivienda_set__estado_id',
            'datos_vivienda_set__municipio_id',
            'datos_vivienda_set__parroquia',
            'datos_vivienda_set__condicion_vivienda_id',
            
            'perfil_salud_set__grupoSanguineo',
            'perfil_salud_set__discapacidad',
            'perfil_salud_set__patologiaCronica',
            
            'formacion_academica_set__nivel_Academico_id',
            'formacion_academica_set__carrera_id',
            'formacion_academica_set__mencion_id',
            
            'perfil_fisico_set',
            'antecedentes_servicio_set',
            'assignments__denominacioncargoid',
            'assignments__estatusid'
        ).get(cedulaidentidad=cedulaidentidad)

        serializer = EmployeeListSerializer(empleado)
        
        return Response({
            'status': 'success',
            'message': 'Empleado obtenido correctamente',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'No se encontró un empleado con la cédula',
            'data': []
        
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': 'Ocurrió un error inesperado en el servidor',
            
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(
    tags=["Gestion de Cargos"],
    summary="Registrar Cargos",
    description="Permite registrar los datos personales del empleado",
    request=CodigosCreateUpdateSerializer,
)
@api_view(['POST'])
def create_position(request):
    serializer = CodigosCreateUpdateSerializer(data=request.data)
    
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "success",
            "message": "Cargo registrado correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError:
        error_dict = serializer.errors
        first_error_value = list(error_dict.values())[0]
        clean_message = first_error_value[0] if isinstance(first_error_value, list) else first_error_value
        return Response({
            'status': "error",
            'message': clean_message, 
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'status': "error",
            'message': str(e),
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Gestion de Cargos"],
    summary="Editar datos de un cargo",
    description="Actualiza los datos de un cargo existente identificado por su id.",
    request=CodigosCreateUpdateSerializer,
) 
@api_view(['PUT'])
def update_position(request, id):
    codigo = get_object_or_404(AsigTrabajo, id=id)
    serializer = CodigosCreateUpdateSerializer(codigo, data=request.data, partial=True)
    
    
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "success",
            'message': "Cargo actualizado correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)

    except ValidationError:
        error_dict = serializer.errors
        first_error_field = list(error_dict.values())[0]
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

        return Response({
            'status': "error",
            'message': clean_message,
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': "error",
            'message': str(e),
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(
    tags=["Asignacion de Cargos"],
    summary="Asigna un cargo al trabajador",
    description="Permite asignarle un cargo a un trabajador",
    request=EmployeeAssignmentSerializer,
)
@api_view(['PATCH'])
def assign_employee(request, id):       
    puesto = get_object_or_404(AsigTrabajo, id=id)
    serializer = EmployeeAssignmentSerializer(puesto, data=request.data, partial=True)
    
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "success",
            'message': "Cargo asignado correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)
        
    except ValidationError:
        error_dict = serializer.errors
        first_error_field = list(error_dict.values())[0]
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

        return Response({
            'status': "error",
            'message': clean_message, 
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': "error",
            'message': str(e) ,
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Asignacion de Cargos"],
    summary="Asignacion de cargos especiales (codigos autogenerables)",
    description="Permite registrar un cargo con codigo autogenerable y asignarlo a un trabajador",
    request=SpecialPositionAutoCreateSerializer,
)
@api_view(['POST'])
def assign_employee_special(request):
    serializer = SpecialPositionAutoCreateSerializer(data=request.data)
    
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "success",
            "message": "Empleado asignado y código especial generado correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError:
        error_dict = serializer.errors
        first_error_field = list(error_dict.values())[0]
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

        return Response({
            'status': "error",
            'message': clean_message,
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': "error",
            'message':str(e), 
         
        }, status=status.HTTP_400_BAD_REQUEST)
        

@extend_schema(
    tags=["Recursos Humanos - Organismo Adscrito"],
    summary="Registrar organismos adscritos",
    description="Registra los organismos adscritos",
     request=OrganismoAdscritoSerializer,
)
@api_view(['POST'])
def create_subsidiary_organism(request):
    serializer = OrganismoAdscritoSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "success",
            "message": "Organismo Adscrito registrado correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError:
        error_dict = serializer.errors
        first_error_field = list(error_dict.values())[0]
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

        return Response({
            'status': "error",
            'message': clean_message, 
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': "error",
            'message': str(e),

        }, status=status.HTTP_400_BAD_REQUEST)
        
  
@extend_schema(
    tags=["Recursos Humanos - Organismo Adscrito"],
    summary="Actualizacion de organismos adscritos",
    description="Actualizacion de los organismos adscritos",
     request=OrganismoAdscritoSerializer,
)  

@api_view(['PATCH'])
def update_organism(request, id):
    Organismos = get_object_or_404(OrganismoAdscrito, id=id)
    serializer = OrganismoAdscritoSerializer(Organismos, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    
    try:
        serializer.save()
        return Response({
            'status': "success",
            'message': "organismo adscrito actualizado correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': "Error",
            'message': str(e),
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
            
@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Creacion de Dependencia",
    description="Permite registrar una dependencia",
    request=DependenciaSerializer,
)
@api_view(['POST'])
def create_dependencia(request):
    serializer = DependenciaSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({
                'status': "success",
                "message": "Dependencia registrada correctamente",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': "error",
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    error_dict = serializer.errors
    first_error_field = list(error_dict.values())[0]
    clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field
    return Response({
        'status': "error",
        'message': clean_message, 
        'data': None
    }, status=status.HTTP_400_BAD_REQUEST)
  
@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Actualizacion de Dependencia",
    description="Permite la Actualizacion una dependencia",
    request=DependenciaSerializer,
)
@api_view(['PATCH'])
def update_dependencia(request, id):
    dependencia = get_object_or_404(Dependencias, id=id)
    serializer = DependenciaSerializer(dependencia, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    
    try:
        serializer.save()
        return Response({
            'status': "success",
            'message': "Dependencia actualizada correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': "Error",
            'message': str(e),
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
# direccion general creacion   
@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Creacion de Direccion General",
    description="Permite registrar una direccion general",
    request=DireccionGeneralSerializer,
)
@api_view(['POST'])
def create_general_directorate(request):
    serializer = DireccionGeneralSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({
                'status': "success",
                "message": "Dirección General registrada correctamente",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': "error",
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    error_dict = serializer.errors
    first_error_field = list(error_dict.values())[0]
    clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field
    return Response({
        'status': "error",
        'message': clean_message, 
        'data': None
    }, status=status.HTTP_400_BAD_REQUEST)

    
@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Actualizacion de Direccion General",
    description="Permite actualizar una direccion general",
    request=DireccionGeneralSerializer,
)
@api_view(['PATCH'])
def update_direccion_general(request, id):
    direccion_general = get_object_or_404(DireccionGeneral, id=id)
    serializer = DireccionGeneralSerializer(direccion_general, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    
    try:
        serializer.save()
        return Response({
            'status': "success",
            'message': "Dirección General actualizada correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': "Error",
            'message': str(e),
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

    
    
 #  CREACION DE DIRECCION DE LINEA 


@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Creacion de Direccion de Linea",
    description="Permite registrar una direccion de linea",
    request=DireccionLineaSerializer,
)     
@api_view(['POST'])
def create_line_directorate(request):
    serializer = DireccionLineaSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "success",
            "message": "Dirección de Línea registrada correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError:
        error_dict = serializer.errors
        first_error_field = list(error_dict.values())[0]
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

        return Response({
            'status': "error",
            'message': clean_message,
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': "error",
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Actualizacion de Direccion de Linea",
    description="Permite la Actualizacion una direccion de linea",
    request=DireccionLineaSerializer,
)     
@api_view(['PATCH'])
def update_line_directorate(request, id):
    direccion_linea = get_object_or_404(DireccionLinea, id=id)
    serializer = DireccionLineaSerializer(direccion_linea, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    
    try:
        serializer.save()
        return Response({
            'status': "success",
            'message': "Dirección de Línea actualizada correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': "Error",
            'message': str(e),
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)    
          
@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Creacion de Coordinacion",
    description="Permite registrar una Coordinacion",
    request=CoordinacionSerializer,
) 
@api_view(['POST'])
def create_coordination(request):
    serializer = CoordinacionSerializer(data=request.data)
     
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': "success",
            "message": "Coordinación registrada correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError:
        error_dict = serializer.errors
        first_error_field = list(error_dict.values())[0]
        clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

        return Response({
            'status': "error",
            'message': clean_message,
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': "error",
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Recursos Humanos - Dependencia"],
    summary="Creacion de Dependencia",
    description="Permite registrar una dependencia",
    request=CoordinacionSerializer,
) 
@api_view(['PATCH'])
def update_coordinacion(request, id):
    coordinacion = get_object_or_404(Coordinaciones, id=id)
    serializer = CoordinacionSerializer(coordinacion, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    
    try:
        serializer.save()
        return Response({
            'status': "success",
            'message': "Coordinación actualizada correctamente",
            'data': serializer.data            
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': "Error",
            'message': str(e),
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

# LISTAR Employee CON CARGOS 

@extend_schema(
    tags=["Asignacion de Cargos"],
    summary="Listar Empleados con sus cargos",
    description="Devuelve una lista de todos los empleados con sus cargos",
    request=EmployeeDetailSerializer,
)

@api_view(['GET'])
def list_employees_active(request):
    try:
        filtro_asignaciones = AsigTrabajo.objects.select_related('Tipo_personal').filter(
            Tipo_personal__tipo_personal__iexact=PERSONAL_ACTIVO
        )
        
        queryset = Employee.objects.filter(
            assignments__Tipo_personal__tipo_personal__iexact=PERSONAL_ACTIVO
        ).prefetch_related(
            Prefetch('assignments', queryset=filtro_asignaciones)
        ).distinct()

        filterset = EmployeeFilter(request.GET, queryset=queryset)
        
        if not filterset.is_valid():
            return Response({
                'status': "error",
                'message': "Los parámetros de búsqueda son inválidos.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

   
        empleados = filterset.qs[:10]

        serializer = EmployeeDetailSerializer(empleados, many=True)

        return Response({
            'status': "success",
            'message': "Empleados activos listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': f"Error al recuperar la lista de empleados: {str(e)}",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
  
  
  
        
@extend_schema(
    tags=["Asignacion de Cargos"],
    summary="Buscar empleado por cédula",
    description="Devuelve los datos de un empleado identificado por su cédula.",
     request=EmployeeDetailSerializer,
) 
@api_view(['GET'])
def get_employee_by_id(request, cedulaidentidad):

    try:
        filtro_asignaciones = AsigTrabajo.objects.filter(
            Tipo_personal__tipo_personal__iexact=PERSONAL_ACTIVO
        )

        empleado = Employee.objects.filter(
            cedulaidentidad=cedulaidentidad,
            assignments__Tipo_personal__tipo_personal__iexact=PERSONAL_ACTIVO
        ).prefetch_related(
            Prefetch('assignments', queryset=filtro_asignaciones)
        ).distinct().first()

        if not empleado:
            return Response({
                'status': "error",
                'message': "No se encontró el empleado o no posee cargos activos.",
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeDetailSerializer(empleado)
        
        return Response({
            'status': "success",
            'message': "Empleado localizado con éxito",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            'status': "error",
            'message': "Ocurrió un error al procesar la búsqueda del empleado.",
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
        
        

# LISTA DE CARGOS 

#  LISTA TODOS LOS CODIGOS 
@extend_schema(
    tags=["Gestion de Cargos"],
    summary="Listar Cargos Generales (Vacantes y Activos)",
    description="Devuelve una lista de todos los cargos registrados",
     request=ListerCodigosSerializer,
)
@api_view(['GET'])
def list_general_work_codes(request):
    try:
        queryset = AsigTrabajo.objects.filter(
            Tipo_personal__tipo_personal__iexact=PERSONAL_ACTIVO
        )

        filterset = AsigTrabajoFilter(request.GET, queryset=queryset)
        
        if not filterset.is_valid():
            return Response({
                'status': "error",
                'message': "Los parámetros de filtro son inválidos.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        codigos = filterset.qs.distinct()[:10]
        
        serializer = ListerCodigosSerializer(codigos, many=True)
        
        return Response({
            'status': "success",
            'message': "Códigos de trabajo listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': f"No se pudo recuperar la lista de códigos: {str(e)}",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
 
# LISTA DE CARGOS VACANTES  
@extend_schema(
    tags=["Gestion de Cargos"],
    summary="Listar Cargos Generales (Vacantes)",
    description="Devuelve una lista de todos los cargos registrados",
     request=ListerCodigosSerializer,
)
@api_view(['GET'])
def list_general_vacants_codes(request):
    try:
        queryset = AsigTrabajo.objects.filter(
            Tipo_personal__tipo_personal__iexact=PERSONAL_ACTIVO,
            estatusid__estatus__iexact=ESTATUS_VACANTE,
            tiponominaid__requiere_codig=False
            
        )

        filterset = AsigTrabajoFilter(request.GET, queryset=queryset)
        
        if not filterset.is_valid():
            return Response({
                'status': "error",
                'message': "Los parámetros de filtro son inválidos.",
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

        codigos = filterset.qs.distinct()[:10]
        
        serializer = ListerCodigosSerializer(codigos, many=True)
        
        return Response({
            'status': "success",
            'message': "Códigos de trabajo listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': f"No se pudo recuperar la lista de códigos: {str(e)}",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


# DATOS PERFIL

@extend_schema(
    tags=["Recursos Humanos - Datos Personales"],
    summary="Listar sexos",
    description="Devuelve una lista de todos los sexos disponibles.",
    responses=SexoSerializer
)
@api_view(['GET'])
def list_genders(request):
    try:
        queryset = Sexo.objects.all()
        serializer = SexoSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Sexos listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudieron recuperar los datos de sexo.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        

@extend_schema(
    tags=["Recursos Humanos - Datos Personales"],
    summary="Listar Estado civil",
    description="Devuelve una lista de todos los Estado civil disponibles.",
    responses=EstadoCivilSerializer
)
@api_view(['GET'])
def list_marital_statuses(request):
    try:
        queryset = estado_civil.objects.all()
        serializer = EstadoCivilSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Estados civiles listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la información de estados civiles.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


# DATOS ACADEMICOS 

@extend_schema(
    tags=["Recursos Humanos - Datos Academicos"],
    summary="Listar nivel Academico",
    description="Devuelve una lista de todos los niveles Academicos disponibles.",
    responses=NivelAcademicoSerializer
)
@api_view(['GET'])
def list_academic_levels(request):
    try:
        queryset = NivelAcademico.objects.all()
        serializer = NivelAcademicoSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Niveles académicos listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de niveles académicos.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(
    tags=["Recursos Humanos - Datos Academicos"],
    summary="Listar carreras",
    description="Devuelve una lista de todas las carreras disponibles.",
    responses=CarrerasSerializer
)
@api_view(['GET'])
def list_careers(request):
    try:
        queryset = carreras.objects.all()
        serializer = CarrerasSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Carreras listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de carreras.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(
    tags=["Recursos Humanos - Datos Academicos"],
    summary="Listar Menciones por Carrera",
    description="Devuelve una lista de las menciones asociadas a una carrera específica ",
    responses=MencionSerializer
)
@api_view(['GET'])
def list_career_specializations(request, carrera_id):
    try:
        menciones = Menciones.objects.filter(carrera_id=carrera_id)

        if not menciones.exists():
            return Response({
                'status': 'error',
                'message': "No se encontraron menciones para la carrera",
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = MencionSerializer(menciones, many=True)

        return Response({
            'status': 'success',
            'message': 'Menciones obtenidas correctamente',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': 'Ocurrió un error inesperado al recuperar las menciones.',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        


# UBICACION DEL VIVIENDA

@extend_schema(
    tags=["Recursos Humanos - Datos Vivienda"],
    summary="Listar condicion de vivienda",
    description="Devuelve una lista de todas las condiciones de vivienda disponibles.",
    responses=CondicionViviendaSerializer
)
@api_view(['GET'])
def list_housing_conditions(request):
    try:
        queryset = condicion_vivienda.objects.all()
        serializer = CondicionViviendaSerializer(queryset, many=True)
        return Response({
            'status': "success",
            'message': "Condiciones de vivienda listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de condiciones de vivienda.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

# DATOS DE VESTIMENTA
@extend_schema(
    tags=["Recursos Humanos - Datos Fisicos"],
    summary="Listar Tallas de Camisas",
    description="Devuelve una lista de todas las Tallas de Camisas disponibles.",
    responses=TallaCamisaSerializer
)
@api_view(['GET'])
def list_shirt_sizes(request):
    try:
        queryset = Talla_Camisas.objects.all()
        serializer = TallaCamisaSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Tallas de camisas listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de tallas de camisas.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Recursos Humanos - Datos Fisicos"],
    summary="Listar Tallas de Pantalones",
    description="Devuelve una lista de todas las Tallas de Pantalones disponibles.",
    responses=TallaPantalonSerializer
)
@api_view(['GET'])
def list_pant_sizes(request):
    try:

        queryset = Talla_Pantalones.objects.all()
        serializer = TallaPantalonSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Tallas de pantalones listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de tallas de pantalones.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recursos Humanos - Datos Fisicos"],
    summary="Listar Tallas de Zapatos",
    description="Devuelve una lista de todas las Tallas de Zapatos disponibles.",
    responses=TallaZapatosSerializer
)
@api_view(['GET'])
def list_shoe_sizes(request):
    try:

        queryset = Talla_Zapatos.objects.all()
        serializer = TallaZapatosSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Tallas de calzado listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de tallas de calzado.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

# DATOS DE SALUD  

@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    summary="Listar Grupo sanguineo",
    description="Devuelve una lista de todos los Grupos sanguineos disponibles.",
    responses=GrupoSanguineoSerializer
)
@api_view(['GET'])
def list_blood_types(request):
    try:
        queryset = GrupoSanguineo.objects.all()
        serializer = GrupoSanguineoSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Grupos sanguíneos listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la información de grupos sanguíneos.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
 
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['GET'],
    summary="Listar categorías de Patologías Crónicas",
   
)
@extend_schema(
      tags=["Recursos Humanos - Datos de Salud"],
    methods=['POST'],
    summary="Crear categoría de Patología Crónica",
    request=categoriasPatologiasSerializer,
 
)
@api_view(['GET', 'POST'])
def list_pathology_categories(request):
    if request.method == 'GET':
        try:
            queryset = categorias_patologias.objects.all()
            serializer = categoriasPatologiasSerializer(queryset, many=True)
            return Response({
                'status': "OK",
                'message': "Categorías listadas correctamente",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': "Error",
                'message': str(e),
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        serializer = categoriasPatologiasSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'status': "success",
                    "message": "Categoría creada correctamente",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': "Error",
                    'message': str(e),
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_dict = serializer.errors 
            first_error_field = list(error_dict.values())[0] 
            clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

            return Response({
                'status': "Error",
                'message': clean_message, 
            }, status=status.HTTP_400_BAD_REQUEST)
           

@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['GET'],
    summary="Listar Patologías Crónicas",
)
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['POST'],
    summary="Crear Patología Crónica",
    request=PatologiasSerializer,
    
)    
@api_view(['GET', 'POST'])
def list_chronic_pathologies(request):
    if request.method == 'GET':
        try:
            queryset = patologias_Cronicas.objects.all()
            serializer = PatologiasSerializer(queryset, many=True)
            return Response({
                'status': "OK",
                'message': "Patologías listadas correctamente",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': "Error",
                'message': str(e),
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        serializer = PatologiasSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'status': "success",
                    "message": "Patología crónica creada con éxito",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': "Error",
                    'message': str(e),
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_dict = serializer.errors 
            first_error_field = list(error_dict.values())[0] 
            clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

            return Response({
                'status': "Error",
                'message': clean_message, 
            }, status=status.HTTP_400_BAD_REQUEST)    

@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['GET'],
    summary="Listar categorías de discapacidad",
    description="Obtiene todas las categorías disponibles para clasificar discapacidades.",
 
)
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['POST'],
    summary="Crear categoría de discapacidad",
    description="Crea una nueva categoría. Ejemplo: 'Física', 'Sensorial', 'Psíquica'.",
    request=categoriasDiscapacidadesSerializer,

)
@api_view(['GET', 'POST'])
def list_disability_categories(request):
    if request.method == 'GET':
        try:
            queryset = categorias_discapacidad.objects.all()
            serializer = categoriasDiscapacidadesSerializer(queryset, many=True)
            return Response({
                'status': "OK",
                'message': "Categorías listadas correctamente",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': "Error",
                'message': str(e),
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        serializer = categoriasDiscapacidadesSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'status': "success",
                    "message": "Categoría creada exitosamente",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': "Error",
                    'message': str(e),
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_dict = serializer.errors 
            first_error_field = list(error_dict.values())[0] 
            clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

            return Response({
                'status': "Error",
                'message': clean_message, 
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['GET'],
    summary="Listar discapacidades",
    description="Devuelve una lista de todas las discapacidades disponibles.",

)
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['POST'],
    summary="Crear discapacidad",
    description="Registra una nueva discapacidad vinculada a una categoría mediante 'categoria_id'.",
    request=DiscapacidadSerializer,
 
)
@api_view(['GET', 'POST'])
def list_disabilities(request):
    if request.method == 'GET':
        try:
            queryset = Discapacidades.objects.all()
            serializer = DiscapacidadSerializer(queryset, many=True)
            return Response({
                'status': "OK",
                'message': "Discapacidades listadas correctamente",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': "Error",
                'message': str(e),
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        serializer = DiscapacidadSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'status': "success",
                    "message": "Discapacidad creada correctamente",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': "Error",
                    'message': str(e),
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_dict = serializer.errors 
            first_error_field = list(error_dict.values())[0] 
            clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

            return Response({
                'status': "Error",
                'message': clean_message, 
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
            
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['GET'],
    summary="Listar categorías de alergias",
    description="Obtiene el listado completo de categorías para clasificar alergias.",
    responses={200: categoriaAlergiaSerializers(many=True)}
)
@extend_schema(
      tags=["Recursos Humanos - Datos de Salud"],
    methods=['POST'],
    summary="Crear categoría de alergia",
    description="Registra una nueva categoría (ej. Alimentaria, Medicamentosa, Ambiental).",
    request=categoriaAlergiaSerializers
)
@api_view(['GET', 'POST'])
def list_allergies_categories(request):
    if request.method == 'GET':
        try:
            queryset = categorias_alergias.objects.all()
            serializer = categoriaAlergiaSerializers(queryset, many=True)
            return Response({
                'status': "OK",
                'message': "Categorías de alergias listadas correctamente",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': "Error",
                'message': str(e),
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        serializer = categoriaAlergiaSerializers(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'status': "success",
                    "message": "Categoría de alergia creada exitosamente",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': "Error",
                    'message': str(e),
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_dict = serializer.errors 
            first_error_field = list(error_dict.values())[0] 
            clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

            return Response({
                'status': "Error",
                'message': clean_message, 
            }, status=status.HTTP_400_BAD_REQUEST)
     
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['GET'],
    summary="Listar Alergias",
    description="Devuelve una lista de todas las Alergias registradas.",
    responses={200: AlergiasSerializer(many=True)}
)
@extend_schema(
    tags=["Recursos Humanos - Datos de Salud"],
    methods=['POST'],
    summary="Crear Alergia",
    description="Registra una nueva alergia. Debes enviar el ID de la categoría en `categoria_id`.",
    request=AlergiasSerializer
)    
@api_view(['GET', 'POST'])
def list_allergies(request):
    if request.method == 'GET':
        try:
            queryset = Alergias.objects.all()
            serializer = AlergiasSerializer(queryset, many=True)
            return Response({
                'status': "OK",
                'message': "Alergias listadas correctamente",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': "Error", 
                'message': str(e),
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        serializer = AlergiasSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'status': "success",
                    "message": "Alergia creada correctamente",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': "Error",
                    'message': str(e),
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_dict = serializer.errors 
            first_error_field = list(error_dict.values())[0] 
            clean_message = first_error_field[0] if isinstance(first_error_field, list) else first_error_field

            return Response({
                'status': "Error",
                'message': clean_message, 
            }, status=status.HTTP_400_BAD_REQUEST)


# DEPENDENCIAS

@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar Dependencias",
    description="Devuelve una lista de todas las Dependencias disponibles.",
    responses=DependenciaSerializer
)
@api_view(['GET'])
def list_dependencies(request):
    try:
        queryset = Dependencias.objects.all()
        serializer = DependenciaSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Dependencias listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de Dependencias",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
   
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar Direcciones Generales",
    description="Devuelve una lista de todas las Direcciones Generales disponibles.",
    responses=DireccionGeneralSerializer
)     
@api_view(['GET'])
def list_general_directorates_by_dependencia(request, dependencia_id):
    get_object_or_404(Dependencias, pk=dependencia_id)
    
    try:
        queryset = DireccionGeneral.objects.filter(dependenciaId=dependencia_id)
        serializer = DireccionGeneralSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Direcciones Generales filtradas por dependencia obtenidas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "Ocurrio un error al recuperar las Direcciones Generales por dependencia",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar Direcciones Generales",
    description="Devuelve una lista de todas las Direcciones Generales disponibles.",
    responses=DireccionGeneralSerializer
)
@api_view(['GET'])
def list_general_directorates(request):
    try:
        queryset = DireccionGeneral.objects.all()
        serializer = DireccionGeneralSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Direcciones Generales listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de Direcciones Generales.",
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar Direcciones de Linea",
    description="Devuelve una lista de todos los tipos de Direcciones de Linea disponibles.",
    responses=DireccionLineaSerializer
)
@api_view(['GET'])
def list_line_directorates_by_general(request, general_id):
 
    get_object_or_404(DireccionGeneral, pk=general_id)
    try:
        direcciones_linea = DireccionLinea.objects.filter(direccionGeneral=general_id)
        serializer = DireccionLineaSerializer(direcciones_linea, many=True)
        
        return Response({
            'status': "success",
            'message': "Direcciones de Línea obtenidas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "Ocurrió un error al recuperar las Direcciones de Línea.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar Coordinaciones",
    description="Devuelve una lista de todos los tipos de Coordinaciones disponibles.",
    responses=CoordinacionSerializer
)
@api_view(['GET'])
def list_coordinations_by_line(request, line_id):
    get_object_or_404(DireccionLinea, pk=line_id)

    try:
        queryset = Coordinaciones.objects.filter(direccionLinea=line_id)
        serializer = CoordinacionSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Coordinaciones obtenidas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "Ocurrió un error al recuperar las coordinaciones.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
 
@extend_schema(
    tags=["Recursos Humanos - Organismo Adscrito"],
    summary="Listar Organismos Adscritos",
    description="Devuelve una lista de todos los organismos adscritos disponibles",
    responses=OrganismoAdscritoSerializer
)       
@api_view(['GET'])
def list_subsidiary_organisms(request):
    try:
        queryset = OrganismoAdscrito.objects.exclude(Organismoadscrito='POLICIAL')
        serializer = OrganismoAdscritoSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Organismos adscritos listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de organismos adscritos.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)  
     

@extend_schema(
    tags=["Recursos Humanos - Organismo Adscrito"],
    summary="Listar Organismos Adscritos - para reportes",
    description="Devuelve una lista de todos los organismos adscritos disponibles",
    responses=OrganismoAdscritoSerializer
)       
@api_view(['GET'])
def list_subsidiary_organisms_report(request):
   try:
      
        queryset = OrganismoAdscrito.objects.all().prefetch_related('sub_organismos')
        
        serializer = OrganismoAdscritoSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Organismos adscritos listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

   except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de organismos adscritos.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST) 
       
# CARGOS 
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar denominaciones de cargo",
    description="Devuelve una lista de todas las denominaciones de cargo disponibles.",
    responses=denominacionCargoSerializer
)
@api_view(['GET'])
def list_position_denominations(request):
    try:
        # Excluir el cargo de personal pasivo
        queryset = Denominacioncargo.objects.exclude(cargo='PERSONAL PASIVO')
        serializer = denominacionCargoSerializer(queryset, many=True)

        return Response({
            'status': "success",
            'message': "Denominaciones de cargos listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de denominaciones de cargos.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar denominaciones de cargo específico",
    description="Devuelve una lista de todas las denominaciones de cargo específico disponibles.",
    responses=denominacionCargoEspecificoSerializer
)
@api_view(['GET'])
def list_specific_position_denominations(request):
    try:
        queryset = Denominacioncargoespecifico.objects.exclude(cargo='PERSONAL PASIVO')
        serializer = denominacionCargoEspecificoSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Denominaciones de cargos específicos listadas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de cargos específicos.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar grados",
    description="Devuelve una lista de todos los grados disponibles.",
    responses=gradoSerializer
)
@api_view(['GET'])
def list_job_grades(request):
    try:
        queryset = Grado.objects.all()
        serializer = gradoSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Grados listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de grados.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)

# NOMINAS
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar tipos de nómina generales",
    description="Devuelve una lista de todos los tipos de nómina disponibles.",
    responses=TipoNominaGeneralSerializer
)
@api_view(['GET'])
def list_payroll_types(request):
    try:
        queryset = Tiponomina.objects.filter(es_activo=True)
        serializer = TipoNominaGeneralSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Tipos de nómina listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:

        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de tipos de nómina.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar tipos de nómina sin las nominas especiales(comision de servicio y hp)",
    description="Devuelve una lista de todos los tipos de nómina disponibles.",
    responses=TipoNominaSerializer
)
@api_view(['GET'])
def list_active_payroll_types(request):

    try:
        queryset = Tiponomina.objects.filter(es_activo=True, requiere_codig=False )
        serializer = TipoNominaSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Tipos de nómina activos obtenidos correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return Response({
            'status': "error",
            'message': "Ocurrió un error al consultar los tipos de nómina.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar solo las nominas especiales(comision de servicio y hp)",
    description="Devuelve una lista de todos los tipos de nómina disponibles.",
    responses=TipoNominaSerializer
)
@api_view(['GET'])
def list_special_payroll_types(request):
    try:

        queryset = Tiponomina.objects.filter(requiere_codig=True)
        serializer = TipoNominaSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Tipos de nómina especiales listados correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de nóminas especiales.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)      
 
       
@extend_schema(
    tags=["Recursos Humanos - Datos para Cargo"],
    summary="Listar solo nóminas de Personal Pasivo",
    description="Devuelve una lista exclusiva de Jubilados y Pensionados.",
    responses=TipoNominaSerializer
)
@api_view(['GET'])
def list_retired_payroll_types(request):
    try:
        queryset = Tiponomina.objects.filter(es_activo=False)
        
        serializer = TipoNominaSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Nóminas de personal pasivo obtenidas correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            'status': "error",
            'message': "Error al recuperar las nóminas de personal pasivo.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        

# ESTATUS 

@extend_schema(
    tags=["Recursos Humanos - Gestion de estatus"],
    summary="Listar Estatus para personal pasivo y egresado",
    description="Devuelve una lista de todos los tipos de estatus  disponibles.",
    responses=EstatusSerializer
)
@api_view(['GET'])
def list_exit_statuses(request):
    try:

        queryset = Estatus.objects.filter(
            estatus__in=ESTATUS_PERMITIDOS_EGRESOS
        ).order_by('estatus')
        
        serializer = EstatusSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Estatus de egreso obtenidos correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:
    
        return Response({
            'status': "error",
            'message': "Error al recuperar los estatus de egreso.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema(
    tags=["Recursos Humanos - Gestion de estatus"],
    summary="Listar Estatus para la gestion de cambio de estatus (SUSPENDIDO, BLOQUEADO, VACANTE)",
    description="Devuelve una lista de todos los tipos de estatus  disponibles.",
    responses=EstatusSerializer
)
@api_view(['GET'])
def list_management_statuses(request):
    try:
        queryset = Estatus.objects.filter(
            estatus__in=ESTATUS_PERMITIDOS
        ).order_by('estatus')
        
        serializer = EstatusSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Estatus de gestión obtenidos correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:

        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de estatus de gestión.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
        
@extend_schema(
    tags=["Recursos Humanos - Gestion de estatus"],
    summary="Listar Estatus para reportes",
    description="Devuelve una lista de todos los tipos de estatus  disponibles.",
    responses=EstatusSerializer
)
@api_view(['GET'])
def list_status_reports(request):
    try:
        queryset = Estatus.objects.exclude(
            estatus__in=ESTATUS_PERMITIDOS_EGRESOS
        ).order_by('estatus')
        
        serializer = EstatusSerializer(queryset, many=True)
        
        return Response({
            'status': "success",
            'message': "Estatus de gestión obtenidos correctamente",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:

        return Response({
            'status': "error",
            'message': "No se pudo recuperar la lista de estatus de gestión.",
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
@api_view(['POST'])
def crear_menciones_view(request):
    is_many = isinstance(request.data, list)
    
    # Si no es una lista, convertimos a lista para uniformidad en el conteo
    data_to_process = request.data if is_many else [request.data]
    
    serializer = MencionSerializer(data=data_to_process, many=True)
    
    if serializer.is_valid():
        instancias_creadas = serializer.save()
        total_creadas = len(instancias_creadas)
        
        return Response({
            "status": "success",
            "mensaje": f"Se han creado {total_creadas} menciones correctamente.",
            "conteo": total_creadas,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    # En caso de error, DRF devuelve un diccionario o una lista de errores
    return Response({
        "status": "error",
        "mensaje": "No se pudieron crear las menciones.",
        "errores": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)