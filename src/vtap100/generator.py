"""config.txt file generator for VTAP100 NFC reader.

This module provides the ConfigGenerator class for generating VTAP100
configuration files from VTAPConfig objects.

Example:
    >>> from vtap100.models.config import VTAPConfig
    >>> from vtap100.models.vas import AppleVASConfig
    >>> from vtap100.generator import ConfigGenerator
    >>>
    >>> vas = AppleVASConfig(merchant_id="pass.com.example.test", key_slot=1)
    >>> config = VTAPConfig(vas_configs=[vas])
    >>> generator = ConfigGenerator(config)
    >>> print(generator.generate())
    !VTAPconfig
    VAS1MerchantID=pass.com.example.test
    VAS1KeySlot=1
"""

from pathlib import Path
from typing import TextIO
from vtap100.models.config import VTAPConfig


# Jinja2 template for dynamic wallet passes (VAS/SmartTap)
# fmt: off
JINJA_PASSES_TEMPLATE = """\
; === MOBILE WALLET PASSES ===
; (Rendered by Jinja2 - passes variable required)
{% for passinfo in passes %}
{% if passinfo.apple %}
VAS{{ passinfo.slot }}MerchantID={{ passinfo.apple.merchant_id }}
VAS{{ passinfo.slot }}KeySlot={{ passinfo.slot }}
{% if passinfo.apple.merchant_url -%}
VAS{{ passinfo.slot }}MerchantURL={{ passinfo.apple.merchant_url }}
{% endif -%}
{% endif %}
{% if passinfo.google %}
ST{{ passinfo.slot }}CollectorID={{ passinfo.google.collector_id }}
ST{{ passinfo.slot }}KeySlot={{ passinfo.slot }}
ST{{ passinfo.slot }}KeyVersion={{ passinfo.google.key_version | default(0) }}
{% endif %}
{% endfor %}
"""
# fmt: on


class ConfigGenerator:
    """Generator for VTAP100 config.txt files.

    This class takes a VTAPConfig object and generates the corresponding
    config.txt content that can be written to a VTAP100 NFC reader.

    Attributes:
        config: The VTAPConfig object to generate from.
    """

    HEADER = "!VTAPconfig"

    def __init__(self, config: VTAPConfig) -> None:
        """Initialize the generator with a configuration.

        Args:
            config: The VTAPConfig object containing all settings.
        """
        self.config = config

    def _generate_static_config_lines(self) -> list[str]:
        """Generate config lines for static sections (keyboard, NFC, DESFire, feedback).

        Returns:
            List of config lines for non-pass settings.
        """
        lines: list[str] = []

        # Keyboard emulation
        if self.config.keyboard:
            lines.append("; Keyboard Emulation")
            lines.extend(self.config.keyboard.to_config_lines())

        # NFC tag settings
        if self.config.nfc:
            nfc_lines = self.config.nfc.to_config_lines()
            if nfc_lines:
                lines.append("; NFC Tag Settings")
                lines.extend(nfc_lines)

        # MIFARE DESFire settings
        if self.config.desfire:
            desfire_lines = self.config.desfire.to_config_lines()
            if desfire_lines:
                lines.append("; MIFARE DESFire Settings")
                lines.extend(desfire_lines)

        # LED/Beep feedback settings
        # Apple Access (ECP2)
        if self.config.access:
            access_lines = self.config.access.to_config_lines()
            if access_lines:
                lines.append("; Apple Access (ECP2)")
                lines.extend(access_lines)

        if self.config.feedback:
            feedback_lines = self.config.feedback.to_config_lines()
            if feedback_lines:
                lines.append("; LED/Beep Settings")
                lines.extend(feedback_lines)

        return lines

    def generate(self, comment: str | None = None) -> str:
        """Generate the config.txt content as a string.

        Args:
            comment: Optional comment to include after the header.

        Returns:
            The complete config.txt content as a string.
        """
        lines: list[str] = []

        # Header
        lines.append(self.HEADER)

        # Optional comment
        if comment:
            lines.append(f"; {comment}")

        # Apple VAS configurations
        if self.config.vas_configs:
            lines.append("; Apple VAS Configuration")
            for vas in self.config.vas_configs:
                lines.extend(vas.to_config_lines(slot_number=vas.slot))

        # VAS default passes enabled
        if self.config.vas_default_passes:
            lines.append(self.config.vas_default_passes.to_config_line())

        # Google Smart Tap configurations
        # Slot numbers come from the model. New configurations default to slot 2
        # because ST1 does not work on real readers, but a slot read from a file
        # is written back unchanged rather than silently moved.
        if self.config.smarttap_configs:
            lines.append("; Google Smart Tap Configuration")
            for st in self.config.smarttap_configs:
                lines.extend(st.to_config_lines(slot_number=st.slot))

        # Smart Tap default passes enabled
        if self.config.smarttap_default_passes:
            lines.append(self.config.smarttap_default_passes.to_config_line())

        # Static configuration (keyboard, NFC, DESFire, feedback)
        lines.extend(self._generate_static_config_lines())

        return "\n".join(lines)

    def write_to_file(self, path: Path, comment: str | None = None) -> None:
        """Write the config.txt content to a file.

        Args:
            path: The path where to write the config.txt file.
            comment: Optional comment to include after the header.
        """
        content = self.generate(comment=comment)
        path.write_text(content, encoding="utf-8")

    def write_to_stream(self, stream: TextIO, comment: str | None = None) -> None:
        """Write the config.txt content to a text stream.

        Args:
            stream: A text stream (e.g., StringIO, file handle) to write to.
            comment: Optional comment to include after the header.
        """
        content = self.generate(comment=comment)
        stream.write(content)

    def generate_template(self, comment: str | None = None) -> str:
        """Generate a Jinja2 template config without VAS/SmartTap.

        This method generates a config.txt template where the VAS and SmartTap
        sections are replaced with a Jinja2 loop placeholder. The static
        configuration (keyboard, NFC, DESFire, feedback) is included as-is.

        Use this when you want to dynamically generate the passes section
        from an external data source (e.g., database, API).

        Args:
            comment: Optional comment to include after the header.

        Returns:
            Config content with Jinja2 placeholder for wallet passes.

        Example:
            >>> generator = ConfigGenerator(config)
            >>> template = generator.generate_template()
            >>> # Use Jinja2 to render with your passes data:
            >>> # from jinja2 import Template
            >>> # result = Template(template).render(passes=my_passes)
        """
        lines: list[str] = []

        # Header
        lines.append(self.HEADER)

        # Optional comment
        if comment:
            lines.append(f"; {comment}")

        # Jinja2 placeholder for dynamic passes
        lines.append(JINJA_PASSES_TEMPLATE)

        # Static configuration section
        lines.append("; === STATIC CONFIGURATION ===")

        # Static configuration (keyboard, NFC, DESFire, feedback)
        lines.extend(self._generate_static_config_lines())

        return "\n".join(lines)
