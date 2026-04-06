from rest_framework import serializers
from RAC.models import Employee

class CargaMasivaExcelSerializer(serializers.ModelSerializer):
    Cedula = serializers.CharField(source='cedulaidentidad', read_only=True)
    Name_Com = serializers.SerializerMethodField()
    Code = serializers.SerializerMethodField()
    Location_Admin = serializers.SerializerMethodField()
    Location_Physical = serializers.SerializerMethodField()
    Estatus = serializers.SerializerMethodField()
    ESTADOS = serializers.SerializerMethodField()
    typeNomina = serializers.SerializerMethodField()

    class Meta:
        model = Employee  
        fields = [
            'Cedula', 'Name_Com', 'Code', 'Location_Physical', 
            'Location_Admin', 'Estatus', 'ESTADOS', 'typeNomina'
        ]

    def get_Name_Com(self, obj):
        apellidos = obj.apellidos.strip() if obj.apellidos else ""
        nombres = obj.nombres.strip() if obj.nombres else ""
        return f"{apellidos}, {nombres}".upper()

    def _get_first_assignment(self, obj):
        asignaciones = obj.assignments.all()
        return asignaciones[0] if asignaciones else None

    def get_Code(self, obj):
        asig = self._get_first_assignment(obj)
        return asig.codigo if asig and asig.codigo else "0"

    def get_Location_Admin(self, obj):
        asig = self._get_first_assignment(obj)
        return asig.Dependencia.dependencia if asig and asig.Dependencia else ""

    def get_Location_Physical(self, obj):
        asig = self._get_first_assignment(obj)
        if not asig:
            return ""
        
        dependencia = asig.Dependencia.dependencia if asig.Dependencia else ""
        direccion_general = asig.DireccionGeneral.direccion_general if asig.DireccionGeneral else ""
        return direccion_general if direccion_general else dependencia

    def get_Estatus(self, obj):
        asig = self._get_first_assignment(obj)
        
        if not asig or not asig.Tipo_personal:
            return "" 
        tipo_nombre = asig.Tipo_personal.tipo_personal.upper()
        if tipo_nombre == 'ACTIVO':
            return 1
        elif tipo_nombre == 'PASIVO':
            return 2
        return ""

    def get_ESTADOS(self, obj):
        return "" 

    def get_typeNomina(self, obj):
        asig = self._get_first_assignment(obj)
        return asig.tiponominaid.nomina if asig and asig.tiponominaid else ""