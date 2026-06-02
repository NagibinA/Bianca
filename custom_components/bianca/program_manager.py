"""Program manager for Bianca integration."""

import logging
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .const import load_programs_config

_LOGGER = logging.getLogger(__name__)


class ProgramManager:
    """Manages program configurations and option availability."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the program manager."""
        self.hass = hass
        self.config = load_programs_config(hass)
        self.programs = self.config.get("programs", {})
        self._current_program = None

    def get_program(self, program_id: str) -> Optional[Dict[str, Any]]:
        """Get program configuration by ID."""
        return self.programs.get(str(program_id))

    def get_program_by_name(self, name: str) -> Optional[tuple[str, Dict[str, Any]]]:
        """Get program ID and configuration by name."""
        for prog_id, prog in self.programs.items():
            if prog.get("name") == name:
                return prog_id, prog
        return None, None

    def get_program_options(self, program_id: str) -> Dict[str, Any]:
        """Get all options for a program."""
        program = self.get_program(program_id)
        if not program:
            return {}
        return program.get("options", {})

    def get_option_values(self, program_id: str, option_name: str) -> List[str]:
        """Get available values for a specific option in a program."""
        options = self.get_program_options(program_id)
        option = options.get(option_name, {})
        return option.get("values", [])

    def get_option_default(self, program_id: str, option_name: str) -> str:
        """Get default value for a specific option in a program."""
        options = self.get_program_options(program_id)
        option = options.get(option_name, {})
        return option.get("default", "")

    def get_pr_code(self, program_id: str) -> int:
        """Get PrCode for a program."""
        program = self.get_program(program_id)
        if not program:
            return 0
        return program.get("pr_code", 0)

    def get_pr_str(self, program_id: str) -> str:
        """Get PrStr for a program (display text on machine)."""
        program = self.get_program(program_id)
        if not program:
            return "test"
        return program.get("pr_str", "test")

    def is_option_available(self, program_id: str, option_name: str, context: Dict[str, str] = None) -> bool:
        """Check if an option is available for the program."""
        options = self.get_program_options(program_id)
        option = options.get(option_name, {})
        
        values = option.get("values", [])
        if not values or (len(values) == 1 and values[0] == "Нет"):
            return False
        
        # Проверяем зависимости
        depends_on = option.get("depends_on")
        if depends_on and context:
            dep_option = depends_on.get("option")
            dep_condition = depends_on.get("condition")
            dep_value = context.get(dep_option)
            
            if dep_condition and dep_value:
                if dep_condition.startswith(">="):
                    try:
                        threshold = int(dep_condition.replace(">=", "").replace("°C", ""))
                        current = int(dep_value.replace("°C", "")) if dep_value else 0
                        if current < threshold:
                            return False
                    except (ValueError, TypeError):
                        pass
        
        return True

    def get_mutual_exclusions(self, program_id: str) -> List[List[str]]:
        """
        Get mutual exclusion rules for a program.
        
        Поддерживает два формата:
        1. ["anti_crease", "night_spin"]  (простой массив)
        2. {"options": ["anti_crease", "night_spin"], "type": "mutual"}  (старый формат)
        """
        program = self.get_program(program_id)
        if not program:
            return []
        
        exclusions = program.get("mutual_exclusion", [])
        result = []
        
        for exclusion in exclusions:
            if isinstance(exclusion, list):
                result.append(exclusion)
            elif isinstance(exclusion, dict):
                options = exclusion.get("options", [])
                if options:
                    result.append(options)
        
        return result

    def check_mutual_exclusion(self, program_id: str, option_name: str, value: str, current_state: Dict[str, str]) -> Dict[str, str]:
        """
        Check mutual exclusion and return options to disable.
        
        Returns a dictionary of {option_key: "Нет"} for options that should be disabled.
        """
        result = {}
        exclusions = self.get_mutual_exclusions(program_id)
        
        for exclusion in exclusions:
            if option_name in exclusion and value == "Есть":
                for opt in exclusion:
                    if opt != option_name:
                        result[opt] = "Нет"
        
        return result

    @property
    def current_program(self) -> Optional[str]:
        """Get current program ID."""
        return self._current_program

    @current_program.setter
    def current_program(self, program_id: str):
        """Set current program ID."""
        self._current_program = str(program_id)

    def get_all_programs(self) -> List[tuple[str, str]]:
        """Get list of all programs (id, name)."""
        return [(pid, prog.get("name", pid)) for pid, prog in self.programs.items()]
