"""Domain filter widget for OpenUP."""

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QButtonGroup
from PyQt6.QtCore import pyqtSignal


class DomainFilter(QWidget):
    """
    Domain filter widget.
    
    Displays list of domains with checkboxes for filtering.
    """
    
    domain_changed = pyqtSignal(str)  # Emitted when domain selection changes
    
    def __init__(self, parent=None):
        """Initialize domain filter."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # "All" checkbox
        self.all_checkbox = QCheckBox("All Domains")
        self.all_checkbox.setChecked(True)
        self.all_checkbox.toggled.connect(self._on_all_toggled)
        self.layout.addWidget(self.all_checkbox)
        
        # Domain checkboxes (will be populated)
        self.domain_checkboxes = {}
        
        self.layout.addStretch()
        
    def set_domains(self, domains: list):
        """
        Set available domains.
        
        Args:
            domains: List of domain names
        """
        # Clear existing checkboxes
        for checkbox in self.domain_checkboxes.values():
            self.layout.removeWidget(checkbox)
            checkbox.deleteLater()
            
        self.domain_checkboxes.clear()
        
        # Add new checkboxes
        for domain in sorted(domains):
            checkbox = QCheckBox(domain)
            checkbox.setChecked(False)
            checkbox.toggled.connect(self._on_domain_toggled)
            self.layout.insertWidget(self.layout.count() - 1, checkbox)
            self.domain_checkboxes[domain] = checkbox
            
        self.logger.debug(f"Set {len(domains)} domains")
        
    def _on_all_toggled(self, checked: bool):
        """Handle 'All' checkbox toggle."""
        if checked:
            # Uncheck all domain checkboxes
            for checkbox in self.domain_checkboxes.values():
                checkbox.setChecked(False)
            self.domain_changed.emit("All")
            
    def _on_domain_toggled(self, checked: bool):
        """Handle domain checkbox toggle."""
        if checked:
            # Uncheck 'All'
            self.all_checkbox.setChecked(False)
            
        # Get selected domains
        selected = [
            domain for domain, cb in self.domain_checkboxes.items()
            if cb.isChecked()
        ]
        
        if not selected:
            # If nothing selected, select 'All'
            self.all_checkbox.setChecked(True)
        else:
            # Emit first selected domain
            self.domain_changed.emit(selected[0])
            
    def get_selected_domains(self) -> list:
        """
        Get list of selected domains.
        
        Returns:
            List of domain names, or empty list if 'All' is selected
        """
        if self.all_checkbox.isChecked():
            return []
            
        return [
            domain for domain, cb in self.domain_checkboxes.items()
            if cb.isChecked()
        ]
