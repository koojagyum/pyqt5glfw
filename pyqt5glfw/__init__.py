from PyQt5.QtGui import QSurfaceFormat

format = QSurfaceFormat()
format.setDepthBufferSize(24)
format.setStencilBufferSize(8)
format.setVersion(3, 3)
format.setProfile(QSurfaceFormat.CoreProfile)
QSurfaceFormat.setDefaultFormat(format)
