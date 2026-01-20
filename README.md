# 🛠️ Gestión de Activos y Mantenimiento

![Status](https://img.shields.io/badge/Status-Live-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)

Una aplicación web completa para la gestión, trazabilidad y control de mantenimiento de equipos industriales. Diseñada para optimizar el flujo de trabajo de técnicos y administradores, permitiendo monitoreo en tiempo real y generación de reportes.

🔗 **[VER DEMO EN VIVO AQUÍ](https://sistema-mantenimiento-fase2.onrender.com/)**

---

## 🚀 Características Principales

* **📊 Dashboard Interactivo:** Visualización de métricas en tiempo real con gráficos (Chart.js) y contadores de estado.
* **🔐 Seguridad Robusta:** Sistema de autenticación con roles (Administrador vs. Invitado) y contraseñas encriptadas (Hashing).
* **☁️ Base de Datos Cloud:** Persistencia de datos usando **PostgreSQL** (Neon Tech) en producción y SQLite en desarrollo local.
* **📄 Reportes Automatizados:** Generación de PDFs profesionales con listados de equipos.
* **🔍 Búsqueda Instantánea:** Filtros en tiempo real mediante JavaScript puro (sin recargas).
* **📱 Diseño Responsivo:** Interfaz moderna adaptada a móviles y escritorio usando **Bootstrap 5**.
* **🏷️ Generación de QR:** Creación automática de códigos QR para identificación de activos.

---

## 🛠️ Stack Tecnológico

Este proyecto fue construido demostrando el ciclo completo de desarrollo (Full Stack):

* **Backend:** Python, Flask, Flask-Login, SQLAlchemy.
* **Database:** PostgreSQL (Producción), SQLite (Local).
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js.
* **Tools:** ReportLab (PDFs), QRcode (Imágenes).
* **Deployment:** Render (Web Service) + Neon (Database).

---

## 💻 Instalación y Uso Local

Si deseas correr este proyecto en tu propia máquina:

1.  **Clonar el repositorio**
    ```bash
    git clone [https://github.com/rafael-rodriguez-dev/Sistema-Mantenimiento.git](https://github.com/rafael-rodriguez-dev/Sistema-Mantenimiento.git)
    cd Sistema-Mantenimiento
    ```

2.  **Crear entorno virtual**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```

3.  **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**
    ```bash
    python app.py
    ```

5.  **Abrir en el navegador**
    Ingresa a `http://127.0.0.1:5000`

---

## 🔑 Credenciales de Acceso (Demo)

Para probar la aplicación puedes usar las siguientes credenciales o el botón de "Invitado":

| Rol | Usuario | Contraseña | Permisos |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Control Total (CRUD) |
| **Invitado** | `invitado` | *(Sin clave)* | Solo Lectura |

---

## 👤 Autor

*Desarrollado por Rafael Rodriguez - Ingeniero de Sistemas*
* [LinkedIn](https://www.linkedin.com/in/rafael-rodriguez-dev/)
* [GitHub](https://github.com/rafael-rodriguez-dev)
