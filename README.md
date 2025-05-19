TuPrimeraPagina-Perez

Mi primera web en django para la gestion de propiedades

Funcionalidades

A continuación se describen las principales funcionalidades de la aplicación

Inserción de datos (Formularios)

Para insertar datos en cada uno de los modelos, puedes acceder a las siguientes url:

Agregar Corredor (Agente Inmobiliario): Ve a la url /agregar_corredor/. El formulario para ingresar datos del corredor (nombre, teléfono, correo). Llena los campos y darle a Guardar

Agregar Arriendo: Ve a la url /agregar_arriendo/. EL formulario para ingresar datos de arriendos (dirección, precio mensual, corredor asociado es *Obligatorio*). Llene los campos y Guardar

Agregar Venta: Ve a la url /agregar_venta/. El formulario para ingresar datos de ventas (dirección, precio, corredor asociado *Obligatorio*)Llene los campos y Guardar

Búsqueda en la Base de Datos

Para buscar información sobre ventas en la base de datos, sigue estos pasos:

1.Acceder al formulario de búsqueda de ventas: Ve a la URL /buscar_venta/.

2.Ingresar el término de búsqueda: En el campo de texto del formulario, escribe la dirección, precio o deja en blanco para ver todas las ventas creadas

3.Realizar la búsqueda: Haz clic en el botón Buscar.

4.Ver los resultados: Los resultados de la búsqueda de ventas se mostrarán en la misma página
