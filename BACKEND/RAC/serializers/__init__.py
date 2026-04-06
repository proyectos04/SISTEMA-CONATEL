# Exportar serializers desde personal_serializers
from .personal_activo_serializers import *
from .personal_pasivo_serializers import *
from .ubicacion_serializers import *
from .family_serializers import *
from .historial_personal_serializers import *
from .carga_excel_serializers import *




# Exportar todos los serializers que puedan necesitarse
__all__ = [
    'DireccionGeneralSerializer',
    'DireccionLineaSerializer',
    'CoordinacionSerializer',
    'TipoNominaSerializer',
    'denominacionCargoEspecificoSerializer',
    'denominacionCargoSerializer',
    'gradoSerializer',
    'OrganismoAdscritoSerializer',
    'ListerCodigosPassiveSerializer'
    'EmployeePasiveDetailSerializer',
    'CargaMasivaExcelSerializer'
]
