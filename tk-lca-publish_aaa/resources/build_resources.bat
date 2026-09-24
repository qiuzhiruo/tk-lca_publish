echo "building user interfaces..."
C:/Python27/Scripts/pyside-uic --from-imports dialog.ui > ../python/example_app/ui/dialog.py

echo "building resources..."
C:/Python27/Lib/site-packages/PySide/pyside-rcc resources.qrc > ../python/example_app/ui/resources_rc.py
