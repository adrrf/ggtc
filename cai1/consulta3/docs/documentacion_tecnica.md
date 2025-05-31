# Documentación Técnica: Protocolo de Identificación Preservando la Privacidad

## 1. Descripción del Protocolo

El protocolo implementa un sistema de identificación que permite a las autoridades detectar personas buscadas (delincuentes, personas con órdenes de búsqueda, terroristas, etc.) en listas de pasajeros de vuelos sin comprometer la privacidad de los pasajeros regulares.

### 1.1 Problema a Resolver

El problema requiere identificar la intersección entre dos conjuntos confidenciales:
- **Conjunto A**: Lista de personas buscadas por la justicia (en posesión de las autoridades)
- **Conjunto B**: Lista de pasajeros de un vuelo (en posesión de la aerolínea)

El objetivo es encontrar los elementos comunes (intersección) sin revelar el resto de los elementos de ambos conjuntos.

### 1.2 Solución Propuesta

La solución utiliza un protocolo de **Intersección Privada de Conjuntos** (Private Set Intersection - PSI), que permite a dos partes encontrar la intersección de sus conjuntos sin revelar ningún otro elemento de los mismos.

## 2. Tecnología Utilizada

### 2.1 OpenMined PSI

La implementación utiliza la biblioteca OpenMined PSI, una biblioteca de código abierto que proporciona implementaciones eficientes de protocolos PSI:

- **Biblioteca**: OpenMined PSI
- **Lenguaje**: Python (binding)
- **Funciones principales**: 
  - `psi.client.CreateWithNewKey()`
  - `psi.server.CreateWithNewKey()`
  - `client.CreateRequest()`
  - `server.ProcessRequest()`
  - `client.GetIntersection()`

### 2.2 Fundamentos Criptográficos

El protocolo se basa en criptografía de curva elíptica y utiliza un esquema basado en ECDH (Elliptic Curve Diffie-Hellman) para el cálculo seguro de la intersección.

## 3. Arquitectura de la Solución

### 3.1 Componentes Principales

La solución consta de varios componentes clave:

1. **Clase Authority**: Representa a la autoridad que posee la lista de personas buscadas.
   - Gestiona la lista de personas de interés
   - Crea el cliente PSI
   - Procesa la respuesta del servidor PSI

2. **Clase Airline**: Representa a la aerolínea que posee las listas de pasajeros.
   - Gestiona listas de pasajeros por vuelo
   - Crea el servidor PSI
   - Procesa la solicitud del cliente PSI
   
3. **Función buscaComunes**: Implementación directa de la funcionalidad principal.
   - Recibe dos conjuntos confidenciales
   - Devuelve la intersección de estos conjuntos
   - Implementa el protocolo PSI completo

4. **Módulo utils**: Funciones auxiliares para pruebas y evaluación.
   - Generación de datos aleatorios
   - Medición de tiempos
   - Comparativas de rendimiento

### 3.2 Flujo de Datos

El flujo del protocolo es el siguiente:

1. La autoridad prepara su lista de personas buscadas.
2. La aerolínea prepara su lista de pasajeros para un vuelo específico.
3. La autoridad crea un cliente PSI y genera una solicitud.
4. La solicitud se envía a la aerolínea.
5. La aerolínea procesa la solicitud con su lista de pasajeros.
6. La aerolínea genera una respuesta PSI y la envía a la autoridad.
7. La autoridad procesa la respuesta y calcula la intersección.
8. Solo las personas que aparecen en ambas listas son identificadas.

## 4. Implementación

### 4.1 Función Principal: buscaComunes

```python
def buscaComunes(Set_de_delincuentes_Confiden, Set_de_pasajeros_vuelo_Confiden):
    """
    Encuentra la intersección entre dos conjuntos confidenciales utilizando PSI.
    
    Args:
        Set_de_delincuentes_Confiden (set): Conjunto confidencial de personas buscadas.
        Set_de_pasajeros_vuelo_Confiden (set): Conjunto confidencial de pasajeros del vuelo.
        
    Returns:
        set: La intersección de los dos conjuntos.
    """
    import openmined.psi as psi
    
    # Convertir conjuntos a listas para PSI
    poi_list = list(Set_de_delincuentes_Confiden)
    pax_list = list(Set_de_pasajeros_vuelo_Confiden)
    
    # Crear un cliente PSI
    psi_client = psi.client.CreateWithNewKey(reveal_intersection=True)
    
    # Crear un servidor PSI
    psi_server = psi.server.CreateWithNewKey(reveal_intersection=True)
    
    # Crear una solicitud desde la lista de pasajeros
    request = psi_client.CreateRequest(pax_list)
    
    # Procesar la solicitud con la lista de personas buscadas
    psi_server.ProcessRequest(request, poi_list)
    
    # Obtener la intersección
    intersection_indices = psi_client.GetIntersection(psi_server.GetResponse())
    
    # Convertir índices a nombres reales
    Set_de_Comunes = {pax_list[i] for i in intersection_indices}
    
    return Set_de_Comunes
```

### 4.2 Implementación Orientada a Objetos

La implementación orientada a objetos separa las responsabilidades entre las dos partes:

- **Authority**: Maneja la lista de personas buscadas y crea el cliente PSI.
- **Airline**: Maneja las listas de pasajeros y crea el servidor PSI.

## 5. Optimizaciones de Rendimiento

### 5.1 Optimizaciones Implementadas

1. **Uso eficiente de estructuras de datos**:
   - Utilizamos conjuntos (`set`) para operaciones rápidas de búsqueda y comparación.
   - Convertimos a listas solo cuando es necesario para la API de PSI.

2. **Procesamiento por lotes**:
   - La implementación permite procesar listas completas de una sola vez.
   - Evita múltiples llamadas al protocolo para cada elemento.

3. **Almacenamiento eficiente**:
   - Los datos se guardan en formato JSON para un acceso rápido.
   - Se utilizan estructuras de datos optimizadas para búsqueda.

4. **Paralelización potencial**:
   - La arquitectura permite la paralelización de múltiples solicitudes.
   - Se puede implementar procesamiento asíncrono para mayor eficiencia.

### 5.2 Consideraciones para Escenarios Críticos

Para escenarios particularmente críticos donde se requiere máxima eficiencia:

1. **Preprocesamiento**:
   - Las listas de personas buscadas pueden preprocesarse.
   - Se pueden almacenar en formatos optimizados para PSI.

2. **Optimización de hardware**:
   - Despliegue en hardware optimizado para operaciones criptográficas.
   - Utilización de aceleradores de hardware cuando estén disponibles.

3. **Estrategias de caché**:
   - Implementación de caché para solicitudes frecuentes.
   - Reutilización de cálculos criptográficos cuando sea posible.

4. **Implementaciones especializadas**:
   - Para casos extremos, se pueden utilizar implementaciones específicas de PSI.
   - Optimizaciones a nivel de algoritmo para conjuntos de tamaño conocido.

## 6. Pruebas y Evaluación

### 6.1 Pruebas Unitarias

Se han implementado pruebas unitarias extensivas que verifican:

1. **Corrección funcional**:
   - Intersecciones básicas con conjuntos pequeños
   - Casos de intersección vacía
   - Casos de intersección completa

2. **Escalabilidad**:
   - Pruebas con conjuntos grandes (miles de elementos)
   - Verificación de rendimiento con diferentes tamaños

3. **Robustez**:
   - Carga de datos desde archivos
   - Manejo de errores y casos límite

### 6.2 Análisis de Rendimiento

Se ha realizado un análisis de rendimiento comparando:

1. **Tiempo de ejecución del PSI** vs. **Intersección de conjuntos ingenua**
2. **Escalabilidad** con diferentes tamaños de conjuntos
3. **Uso de memoria** durante la ejecución

Los resultados muestran que:
- El protocolo PSI es más lento que la intersección ingenua para conjuntos pequeños
- La diferencia de rendimiento se justifica por las garantías de privacidad
- El protocolo escala bien con conjuntos grandes (miles de elementos)

### 6.3 Pruebas de Seguridad

Se han realizado análisis de seguridad para verificar:

1. **Preservación de la privacidad**:
   - Solo se revelan los elementos en la intersección
   - No hay filtración de información sobre otros elementos

2. **Resistencia a ataques**:
   - Análisis contra intentos de recuperar información adicional
   - Verificación de las propiedades criptográficas del protocolo

## 7. Conclusiones

El protocolo implementado proporciona una solución eficiente y segura para el problema planteado, permitiendo:

1. Identificar personas buscadas en listas de pasajeros.
2. Preservar la privacidad de los pasajeros regulares.
3. Mantener la confidencialidad de la lista de personas buscadas.
4. Operar con eficiencia incluso en escenarios críticos.

La implementación es flexible y puede adaptarse a diferentes requisitos operativos, desde pequeñas comprobaciones hasta sistemas a gran escala con millones de registros.
