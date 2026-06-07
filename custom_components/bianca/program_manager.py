"""Program manager for Bianca integration - Version 2.4.3."""

import json
import os
import logging
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .const import DOMAIN, PROGRAMS_FILE, PROGRAMS_NEXT_ID

_LOGGER = logging.getLogger(__name__)


class ProgramManager:
    """Manages program configurations and option availability."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the program manager."""
        self.hass = hass
        self.config_path = hass.config.path(f"custom_components/{DOMAIN}/{PROGRAMS_FILE}")
        self.config = self._load_config()
        self.programs = self.config.get("programs", {})
        self.next_id = self.config.get(PROGRAMS_NEXT_ID, 1)
        self._current_program_id = None
        
        # Миграция: добавляем PrStrRaw для старых программ
        self.migrate_add_pr_str_raw()

    def _load_config(self) -> dict:
        """Загружает конфигурацию из файла (синхронно, вызывается через executor)."""
        if not os.path.exists(self.config_path):
            return {"programs": {}, PROGRAMS_NEXT_ID: 1}
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            _LOGGER.error(f"Failed to load programs config: {e}")
            return {"programs": {}, PROGRAMS_NEXT_ID: 1}

    def _save_config(self):
        """Сохраняет конфигурацию в файл (синхронно, вызывается через executor)."""
        self.config[PROGRAMS_NEXT_ID] = self.next_id
        self.config["programs"] = self.programs
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _LOGGER.error(f"Failed to save programs config: {e}")

    def migrate_add_pr_str_raw(self):
        """Миграция: добавляет поле PrStrRaw для существующих программ."""
        modified = False
        for prog_id, prog in self.programs.items():
            if "PrStrRaw" not in prog:
                prog["PrStrRaw"] = prog.get("PrStr", "")
                modified = True
                _LOGGER.debug(f"Added PrStrRaw for program {prog_id}")
        
        if modified:
            self._save_config()
            _LOGGER.info("Migrated programs.json: added PrStrRaw field")

    def get_next_id(self) -> int:
        """Get next available program ID and increment."""
        prog_id = self.next_id
        self.next_id += 1
        return prog_id

    def get_program(self, program_id: int) -> Optional[Dict[str, Any]]:
        """Get program configuration by ID."""
        return self.programs.get(str(program_id))

    def get_program_by_name(self, name: str) -> Optional[tuple[int, Dict[str, Any]]]:
        """Get program ID and configuration by name."""
        for prog_id, prog in self.programs.items():
            if prog.get("name") == name:
                return int(prog_id), prog
        return None, None

    def get_program_by_pr(self, pr: int) -> Optional[tuple[int, Dict[str, Any]]]:
        """Get program ID and configuration by Pr value."""
        for prog_id, prog in self.programs.items():
            if prog.get("Pr") == pr:
                return int(prog_id), prog
        return None, None

    def get_all_programs(self) -> List[tuple[int, str]]:
        """Get list of all programs (id, name)."""
        return [(int(pid), prog.get("name", pid)) for pid, prog in self.programs.items()]

    def add_program(self, name: str, pr: int, pr_code: int, pr_str: str, pr_str_raw: str, options: dict, mutual_exclusion: list) -> int:
        """Add a new program and return its ID."""
        prog_id = self.get_next_id()
        self.programs[str(prog_id)] = {
            "name": name,
            "Pr": pr,
            "PrCode": pr_code,
            "PrStr": pr_str,
            "PrStrRaw": pr_str_raw,
            "options": options,
            "mutual_exclusion": mutual_exclusion
        }
        self._save_config()
        return prog_id

    def update_program(self, program_id: int, name: str, pr: int, pr_code: int, pr_str: str, pr_str_raw: str, options: dict, mutual_exclusion: list) -> bool:
        """Update an existing program."""
        if str(program_id) not in self.programs:
            return False
        
        self.programs[str(program_id)] = {
            "name": name,
            "Pr": pr,
            "PrCode": pr_code,
            "PrStr": pr_str,
            "PrStrRaw": pr_str_raw,
            "options": options,
            "mutual_exclusion": mutual_exclusion
        }
        self._save_config()
        return True

    def delete_program(self, program_id: int) -> bool:
        """Delete a program."""
        if str(program_id) not in self.programs:
            return False
        
        del self.programs[str(program_id)]
        self._save_config()
        return True

    def get_pr_value(self, program_id: int) -> int:
        """Get Pr (PrNm) value for a program."""
        program = self.get_program(program_id)
        return program.get("Pr", 0) if program else 0

    def get_pr_code_value(self, program_id: int) -> int:
        """Get PrCode value for a program."""
        program = self.get_program(program_id)
        return program.get("PrCode", 0) if program else 0

    def get_pr_str_value(self, program_id: int) -> str:
        """Get PrStr value for a program."""
        program = self.get_program(program_id)
        return program.get("PrStr", "test") if program else "test"

    def get_pr_str_raw_value(self, program_id: int) -> str:
        """Get PrStrRaw value for a program."""
        program = self.get_program(program_id)
        return program.get("PrStrRaw", "") if program else ""

    def get_program_options(self, program_id: int) -> Dict[str, Any]:
        """Get all options for a program."""
        program = self.get_program(program_id)
        if not program:
            return {}
        return program.get("options", {})

    def get_option_values(self, program_id: int, option_name: str) -> List[str]:
        """Get available values for a specific option in a program."""
        options = self.get_program_options(program_id)
        option = options.get(option_name, {})
        return option.get("values", [])

    def get_option_default(self, program_id: int, option_name: str) -> str:
        """Get default value for a specific option in a program."""
        options = self.get_program_options(program_id)
        option = options.get(option_name, {})
        return option.get("default", "")

    def is_option_available(self, program_id: int, option_name: str, context: Dict[str, str] = None) -> bool:
        """Check if an option is available for the program."""
        options = self.get_program_options(program_id)
        option = options.get(option_name, {})
        
        values = option.get("values", [])
        if not values or (len(values) == 1 and values[0] == "Нет"):
            return False
        
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

    def get_mutual_exclusions(self, program_id: int) -> List[List[str]]:
        """Get mutual exclusion rules for a program."""
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

    def check_mutual_exclusion(self, program_id: int, option_name: str, value: str, current_state: Dict[str, str]) -> Dict[str, str]:
        """Check mutual exclusion and return options to disable."""
        result = {}
        exclusions = self.get_mutual_exclusions(program_id)
        
        for exclusion in exclusions:
            if option_name in exclusion and value == "Есть":
                for opt in exclusion:
                    if opt != option_name:
                        result[opt] = "Нет"
        
        return result

    @property
    def current_program_id(self) -> Optional[int]:
        """Get current program ID."""
        return self._current_program_id

    @current_program_id.setter
    def current_program_id(self, program_id: int):
        """Set current program ID."""
        self._current_program_id = program_id