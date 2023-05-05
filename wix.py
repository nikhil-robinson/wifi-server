from PyQt6.QtWidgets import QApplication, QWizard, QWizardPage, QLabel, QGridLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, QProcess

class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle('Introduction')
        label = QLabel('Welcome to the Python requirements installer wizard.')
        label.setWordWrap(True)
        layout = QGridLayout()
        layout.addWidget(label)
        self.setLayout(layout)

class RequirementsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle('Requirements')
        self.setSubTitle('Please enter the Python requirements you would like to install:')
        self.requirements_textedit = QTextEdit()
        layout = QGridLayout()
        layout.addWidget(self.requirements_textedit)
        self.setLayout(layout)

class InstallPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle('Installing Requirements')
        self.install_label = QLabel('Click the Install button to install the Python requirements.')
        # self.install_label.setAlignment(Qt.AlignCenter)
        self.install_button = QPushButton('Install')
        self.install_button.clicked.connect(self.install_requirements)
        layout = QGridLayout()
        layout.addWidget(self.install_label)
        layout.addWidget(self.install_button)
        self.setLayout(layout)

    def install_requirements(self):
        requirements = self.wizard().page(1).requirements_textedit.toPlainText()
        if requirements:
            process = QProcess()
            process.start('pip', ['install', requirements])
            process.waitForFinished()
            self.install_label.setText('Python requirements installed successfully.')
        else:
            self.install_label.setText('Please enter the Python requirements first.')

if __name__ == '__main__':
    app = QApplication([])
    wizard = QWizard()
    wizard.addPage(IntroPage())
    wizard.addPage(RequirementsPage())
    wizard.addPage(InstallPage())
    wizard.setWindowTitle('Python Requirements Installer Wizard')
    wizard.show()
    app.exec()
